"""Services for the socialize app."""

# !/usr/bin/python
# pylint: disable=E1101
#
# This file is part of django-socialize project.
#
# Copyright (C) 2010-2025 William Oliveira de Lagos <william.lagos@icloud.com>
#
# Socialize is free software: you can redistribute it and/or modify
# it under the terms of the Lesser GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Socialize is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Socialize. If not, see <http://www.gnu.org/licenses/>.
#

import json
import logging
import uuid
from urllib.parse import urlparse

import requests
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from .models import Activity, Actor, Follow, Object, Token, Vault
from .signatures import generate_key_pair, verify_http_signature
from .tasks import deliver_activity_task, process_inbound_activity_task

logger = logging.getLogger(__name__)


class ActorService:
    """Handles ActivityPub Actor endpoints and discovery."""

    def get_actor(self, _, username, as_activitypub=True):
        """Returns the ActivityPub representation of an Actor for the given username."""
        actor = get_object_or_404(Actor, user__username=username)
        if as_activitypub:
            return JsonResponse(
                actor.as_activitypub(),
                content_type="application/activity+json",
            )
        return JsonResponse(
            {
                "id": str(actor.id),
                "username": actor.user.username,
                "display_name": actor.get_display_name(),
                "actor_type": actor.actor_type,
                "bio": actor.bio,
                "title": actor.title,
                "birthdate": actor.birthdate,
                "inbox": actor.get_inbox_url(),
                "outbox": actor.get_outbox_url(),
                "followers": actor.get_followers_url(),
                "following": actor.get_following_url(),
                "permissions": list(actor.get_user_permissions()),
                "score": actor.score,
                "joined_at": actor.joined_at,
            }
        )

    def create_actor(self, data):
        """Creates a new Actor and Vault with RSA keys from the given data."""
        private_key, public_key = self.generate_keys()
        user, _ = User.objects.get_or_create(username=data.get("username"))
        actor = Actor.objects.create(
            user=user,
            username=user.username,
            public_key=public_key,
        )
        Vault.objects.create(actor=actor, private_key=private_key)
        return actor

    def generate_keys(self):
        """Generates a new private/public RSA key pair."""
        return generate_key_pair()

    def get_or_create_remote_actor(self, actor_url: str) -> Actor:
        """
        Retrieves a cached remote Actor or fetches and persists the actor document.
        """
        existing = Actor.objects.filter(actor_url=actor_url).first()
        if existing:
            return existing

        # Fetch remote actor via ActivityPub JSON
        try:
            resp = requests.get(
                actor_url,
                headers={
                    "Accept": 'application/activity+json, application/ld+json; profile="https://www.w3.org/ns/activitystreams"',
                    "User-Agent": f'Socialize-ActivityPub ({getattr(settings, "SITE_DOMAIN", "localhost")})',
                },
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json()
                username = (
                    data.get("preferredUsername")
                    or urlparse(actor_url).path.strip("/").split("/")[-1]
                )
                display_name = data.get("name") or username
                inbox = data.get("inbox")
                outbox = data.get("outbox")
                shared_inbox = (data.get("endpoints") or {}).get("sharedInbox")
                followers_url = data.get("followers")
                following_url = data.get("following")
                pubkey = ""
                if "publicKey" in data and isinstance(data["publicKey"], dict):
                    pubkey = data["publicKey"].get("publicKeyPem", "")

                actor, _ = Actor.objects.get_or_create(
                    actor_url=actor_url,
                    defaults={
                        "username": username,
                        "display_name": display_name,
                        "domain": urlparse(actor_url).netloc,
                        "inbox": inbox,
                        "outbox": outbox,
                        "shared_inbox": shared_inbox,
                        "followers_url": followers_url,
                        "following_url": following_url,
                        "public_key": pubkey,
                        "actor_type": data.get("type", "Person"),
                    },
                )
                return actor
        except Exception as e:
            logger.warning(f"Failed to fetch remote actor {actor_url}: {e}")

        # Fallback placeholder actor
        fallback_username = urlparse(actor_url).path.strip("/").split("/")[-1]
        actor, _ = Actor.objects.get_or_create(
            actor_url=actor_url,
            defaults={
                "username": fallback_username,
                "domain": urlparse(actor_url).netloc,
            },
        )
        return actor

    def get_webfinger(self, request):
        """Returns the WebFinger response for user discovery."""
        resource = request.GET.get("resource")
        site_domain = getattr(settings, "SITE_DOMAIN", "localhost:8000")

        if resource and resource.startswith("acct:"):
            username = resource.split("acct:")[1].split("@")[0]
            actor = get_object_or_404(Actor, user__username=username)

            return JsonResponse(
                {
                    "subject": f"acct:{actor.user.username}@{site_domain}",
                    "aliases": [actor.get_actor_url()],
                    "links": [
                        {
                            "rel": "self",
                            "type": "application/activity+json",
                            "href": actor.get_actor_url(),
                        },
                        {
                            "rel": "http://webfinger.net/rel/profile-page",
                            "type": "text/html",
                            "href": actor.get_actor_url(),
                        },
                    ],
                },
                content_type="application/jrd+json",
            )

        return JsonResponse({"error": "Invalid WebFinger request"}, status=400)

    def get_followers(self, _, username):
        """Returns the followers collection for the given actor."""
        actor = get_object_or_404(Actor, user__username=username)
        follows = Follow.objects.filter(target=actor, accepted=True).select_related(
            "actor"
        )

        items = [f.actor.get_actor_url() for f in follows]
        return JsonResponse(
            {
                "@context": "https://www.w3.org/ns/activitystreams",
                "id": actor.get_followers_url(),
                "type": "OrderedCollection",
                "totalItems": len(items),
                "orderedItems": items,
            },
            content_type="application/activity+json",
        )

    def get_following(self, _, username):
        """Returns the following collection for the given actor."""
        actor = get_object_or_404(Actor, user__username=username)
        follows = Follow.objects.filter(actor=actor, accepted=True).select_related(
            "target"
        )

        items = [f.target.get_actor_url() for f in follows]
        return JsonResponse(
            {
                "@context": "https://www.w3.org/ns/activitystreams",
                "id": actor.get_following_url(),
                "type": "OrderedCollection",
                "totalItems": len(items),
                "orderedItems": items,
            },
            content_type="application/activity+json",
        )

    def get_nodeinfo_discovery(self, _):
        """Returns /.well-known/nodeinfo discovery links."""
        site_domain = getattr(settings, "SITE_DOMAIN", "localhost:8000")
        return JsonResponse(
            {
                "links": [
                    {
                        "rel": "http://nodeinfo.diaspora.software/ns/schema/2.0",
                        "href": f"https://{site_domain}/nodeinfo/2.0",
                    }
                ]
            }
        )

    def get_nodeinfo_2_0(self, _):
        """Returns NodeInfo 2.0 metadata."""
        local_users_count = Actor.objects.filter(user__isnull=False).count()
        local_posts_count = Object.objects.filter(actor__user__isnull=False).count()

        return JsonResponse(
            {
                "version": "2.0",
                "software": {
                    "name": "atria-socialize",
                    "version": "0.1.0",
                },
                "protocols": ["activitypub"],
                "services": {"inbound": [], "outbound": []},
                "openRegistrations": False,
                "usage": {
                    "users": {
                        "total": local_users_count,
                        "activeHalfyear": local_users_count,
                        "activeMonth": local_users_count,
                    },
                    "localPosts": local_posts_count,
                    "localComments": 0,
                },
                "metadata": {
                    "nodeName": "Atria Federated Node",
                    "nodeDescription": "Decentralized social marketplace with ActivityPub federation",
                },
            }
        )


class ActivityService:
    """Handles ActivityPub Activity endpoints for inbox and outbox."""

    def create_activity(self, request, username=None):
        """
        Handles ActivityPub inbox messages (personal or shared inbox).
        Verifies HTTP signatures and processes activities.
        """
        # Signature verification if signature header is provided
        has_sig = bool(
            request.headers.get("Signature") or request.META.get("HTTP_SIGNATURE")
        )
        sender_key_id = None

        if has_sig:
            is_valid, key_or_err = verify_http_signature(request)
            if not is_valid:
                return JsonResponse(
                    {"error": f"Signature verification failed: {key_or_err}"},
                    status=401,
                )
            sender_key_id = key_or_err

        try:
            data = json.loads(request.body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return JsonResponse({"error": "Invalid JSON data"}, status=400)

        # Delegate processing to background task or process inline
        try:
            process_inbound_activity_task.delay(data, sender_key_id)
        except Exception:
            self.process_inbound_activity(data, sender_key_id)

        return JsonResponse({"status": "accepted"}, status=202)

    def process_inbound_activity(self, data: dict, sender_key_id: str | None = None):
        """
        Dispatches and processes inbound ActivityPub verbs:
        Follow, Accept, Create, Like, Announce, Undo, Delete.
        """
        activity_type = data.get("type")
        actor_url = data.get("actor")
        if not activity_type or not actor_url:
            return

        actor_service = ActorService()
        remote_actor = actor_service.get_or_create_remote_actor(actor_url)

        if activity_type == "Follow":
            self._handle_follow(data, remote_actor)
        elif activity_type == "Accept":
            self._handle_accept(data, remote_actor)
        elif activity_type == "Create":
            self._handle_create(data, remote_actor)
        elif activity_type == "Like":
            self._handle_like(data, remote_actor)
        elif activity_type == "Announce":
            self._handle_announce(data, remote_actor)
        elif activity_type == "Undo":
            self._handle_undo(data, remote_actor)

    def _handle_follow(self, data: dict, remote_actor: Actor):
        """Handles inbound Follow activity and sends Accept back to remote actor."""
        target_obj = data.get("object")
        target_actor = None

        if isinstance(target_obj, str):
            # Target is an actor URL, e.g. https://domain/users/alice/
            target_actor = Actor.objects.filter(actor_url=target_obj).first()
            if not target_actor:
                # Try finding by username parsed from URL
                uname = urlparse(target_obj).path.strip("/").split("/")[-1]
                target_actor = Actor.objects.filter(user__username=uname).first()
        elif isinstance(target_obj, dict):
            target_id = target_obj.get("id")
            if target_id:
                target_actor = Actor.objects.filter(actor_url=target_id).first()

        if not target_actor:
            logger.warning(f"Follow target actor not found: {target_obj}")
            return

        follow_obj, _ = Follow.objects.update_or_create(
            actor=remote_actor,
            target=target_actor,
            defaults={
                "accepted": True,
                "activity_id": data.get("id"),
            },
        )

        # Send Accept activity back to remote actor's inbox
        accept_activity = Activity.objects.create(
            actor=target_actor,
            activity_type="Accept",
            object_data={
                "@context": "https://www.w3.org/ns/activitystreams",
                "id": f"{target_actor.get_actor_url()}#accept-{uuid.uuid4()}",
                "type": "Accept",
                "actor": target_actor.get_actor_url(),
                "object": data,
            },
        )
        if remote_actor.inbox:
            deliver_activity_task.delay(str(accept_activity.id), [remote_actor.inbox])

    def _handle_accept(self, data: dict, remote_actor: Actor):
        """Handles inbound Accept activity."""
        follow_act = data.get("object")
        if isinstance(follow_act, dict) and follow_act.get("id"):
            Follow.objects.filter(activity_id=follow_act["id"]).update(accepted=True)

    def _handle_create(self, data: dict, remote_actor: Actor):
        """Handles inbound Create activity (Note, Article, Video, Audio, etc.)."""
        obj_data = data.get("object")
        if not isinstance(obj_data, dict):
            return

        obj_id = obj_data.get("id")
        obj_type = obj_data.get("type", "Note")
        content = obj_data.get("content", "")
        summary = obj_data.get("summary", "")
        attachment = obj_data.get("attachment", [])

        Object.objects.update_or_create(
            object_url=obj_id,
            defaults={
                "actor": remote_actor,
                "object_type": obj_type,
                "content": content,
                "summary": summary,
                "attachment": (
                    attachment if isinstance(attachment, list) else [attachment]
                ),
            },
        )
        Activity.objects.create(
            actor=remote_actor,
            activity_type="Create",
            object_data=data,
            activity_url=data.get("id"),
        )

    def _handle_like(self, data: dict, remote_actor: Actor):
        """Handles inbound Like activity."""
        Activity.objects.create(
            actor=remote_actor,
            activity_type="Like",
            object_data=data,
            activity_url=data.get("id"),
        )
        # Increment actor score on object author
        obj_target = data.get("object")
        target_obj = None
        if isinstance(obj_target, str):
            target_obj = (
                Object.objects.filter(object_url=obj_target)
                .select_related("actor")
                .first()
            )
            if not target_obj:
                parts = [
                    p for p in urlparse(obj_target).path.strip("/").split("/") if p
                ]
                if parts:
                    try:
                        obj_uuid = uuid.UUID(parts[-1])
                        target_obj = (
                            Object.objects.filter(id=obj_uuid)
                            .select_related("actor")
                            .first()
                        )
                    except ValueError:
                        pass
        if target_obj and target_obj.actor:
            Actor.objects.filter(id=target_obj.actor.id).update(score=F("score") + 1)

    def _handle_announce(self, data: dict, remote_actor: Actor):
        """Handles inbound Announce (Boost) activity."""
        Activity.objects.create(
            actor=remote_actor,
            activity_type="Announce",
            object_data=data,
            activity_url=data.get("id"),
        )

    def _handle_undo(self, data: dict, remote_actor: Actor):
        """Handles inbound Undo activity."""
        inner_obj = data.get("object")
        if not isinstance(inner_obj, dict):
            return

        inner_type = inner_obj.get("type")
        if inner_type == "Follow":
            target_id = inner_obj.get("object")
            target_actor = None
            if isinstance(target_id, str):
                target_actor = Actor.objects.filter(actor_url=target_id).first()
                if not target_actor:
                    parts = [
                        p for p in urlparse(target_id).path.strip("/").split("/") if p
                    ]
                    if parts:
                        uname = parts[-1]
                        target_actor = Actor.objects.filter(
                            user__username=uname
                        ).first()
            if target_actor:
                Follow.objects.filter(
                    actor=remote_actor,
                    target=target_actor,
                ).delete()
            else:
                Follow.objects.filter(
                    actor=remote_actor,
                    target__actor_url=target_id,
                ).delete()
        elif inner_type == "Like":
            inner_id = inner_obj.get("id")
            if inner_id:
                Activity.objects.filter(activity_url=inner_id).delete()

    def get_activity(self, request, username):
        """Returns the ActivityPub representation of an Actor's outbox with pagination."""
        actor = get_object_or_404(Actor, user__username=username)
        activities = Activity.objects.filter(actor=actor).order_by("-published_at")
        page_num = request.GET.get("page")
        outbox_url = actor.get_outbox_url()

        if page_num is None:
            # Base OrderedCollection with first/last links
            total = activities.count()
            return JsonResponse(
                {
                    "@context": "https://www.w3.org/ns/activitystreams",
                    "id": outbox_url,
                    "type": "OrderedCollection",
                    "totalItems": total,
                    "first": f"{outbox_url}?page=1",
                    "last": f"{outbox_url}?page=1",
                },
                content_type="application/activity+json",
            )

        # OrderedCollectionPage
        paginator = Paginator(activities, 20)
        try:
            current_page = paginator.page(int(page_num))
        except (ValueError, Exception):
            current_page = paginator.page(1)

        items = [act.as_activitypub() for act in current_page.object_list]
        page_data = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "id": f"{outbox_url}?page={current_page.number}",
            "type": "OrderedCollectionPage",
            "partOf": outbox_url,
            "totalItems": paginator.count,
            "orderedItems": items,
        }
        if current_page.has_next():
            page_data["next"] = f"{outbox_url}?page={current_page.next_page_number()}"
        if current_page.has_previous():
            page_data["prev"] = (
                f"{outbox_url}?page={current_page.previous_page_number()}"
            )

        return JsonResponse(page_data, content_type="application/activity+json")


class ObjectService:
    """Handles ActivityPub Object endpoints."""

    def get_object(self, _, object_id, as_activitypub=True):
        """Returns the ActivityPub representation of an Object for the given ID."""
        obj = get_object_or_404(Object, id=object_id)
        if as_activitypub:
            return JsonResponse(
                obj.as_activitypub(),
                content_type="application/activity+json",
            )
        return JsonResponse(
            {
                "id": str(obj.id),
                "actor": obj.actor.get_username(),
                "object_type": obj.object_type,
                "content": obj.content,
                "summary": obj.summary,
                "attachment": obj.attachment,
                "published_at": obj.published_at,
            }
        )

    def create_object(self, request, username=None):
        """Creates a new Object and fans out Create activity to local actor's followers."""
        try:
            data = json.loads(request.body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return JsonResponse({"error": "Invalid JSON data"}, status=400)

        user_obj = None
        if username:
            user_obj = User.objects.filter(username=username).first()
        elif request.user.is_authenticated:
            user_obj = request.user

        if not user_obj:
            return JsonResponse(
                {"error": "User not found or unauthenticated"}, status=400
            )

        actor = get_object_or_404(Actor, user=user_obj)
        obj = Object.objects.create(
            actor=actor,
            object_type=data.get("type", "Note"),
            content=data.get("content", ""),
            summary=data.get("summary", ""),
            attachment=data.get("attachment", []),
        )

        # Create and fan out Create activity to followers
        act = Activity.objects.create(
            actor=actor,
            activity_type="Create",
            object_data={
                "@context": "https://www.w3.org/ns/activitystreams",
                "id": f"{actor.get_actor_url()}#create-{uuid.uuid4()}",
                "type": "Create",
                "actor": actor.get_actor_url(),
                "object": obj.as_activitypub(),
                "to": ["https://www.w3.org/ns/activitystreams#Public"],
            },
        )

        follower_inboxes = list(
            Follow.objects.filter(target=actor, accepted=True)
            .exclude(actor__inbox__isnull=True)
            .values_list("actor__inbox", flat=True)
        )
        if follower_inboxes:
            deliver_activity_task.delay(str(act.id), follower_inboxes)

        return JsonResponse(
            obj.as_activitypub(),
            status=201,
            content_type="application/activity+json",
        )


class VaultService:
    """Handles Vault endpoints."""

    @staticmethod
    def get_private_key(username):
        """Fetches the private key for an actor securely."""
        vault = Vault.objects.filter(actor__user__username=username).first()
        if not vault:
            raise PermissionDenied("Access denied: Private key not found.")
        return vault.private_key

    def check_user_vault(self, username):
        """Check if the vault already has the private key for the actor."""
        user = User.objects.filter(username=username).first()
        if not user:
            return JsonResponse({"error": "User not found"}, status=404)

        vault = Vault.objects.filter(actor__user__username=username).first()
        if not vault:
            return JsonResponse({"error": "Private key not found in vault"}, status=404)

        return JsonResponse({"message": "Vault already has the private key"})


class AuthenticationService:
    """
    Handles authentication for the socialize app
    using OAuth providers like Google and Facebook.
    """

    def authenticate(self, request, user_data, access_token):
        """Authenticate the user using the OAuth provider."""
        user = authenticate(username=user_data["username"])
        if not user:
            user = ActorService().create_actor({"username": user_data["username"]}).user

        login(request, user)
        token, _ = Token.objects.get_or_create(access_token=access_token, user=user)
        return JsonResponse({"access_token": token.access_token, "expires_in": 3600})

    def verify_access_token(self, provider, token):
        """Check if token is valid with provider."""
        provider_urls = {
            "google": "https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={token}",
            "facebook": "https://graph.facebook.com/me?access_token={token}&fields=email",
        }
        if provider not in provider_urls:
            return None

        try:
            response = requests.get(
                provider_urls[provider].format(token=token), timeout=10
            )
            if response.status_code != 200:
                return None
            return response.json()
        except Exception:
            return None
