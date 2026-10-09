"""
Comprehensive tests for ActivityPub federation, draft-cavage HTTP signatures,
inbound verb processing, collections, outbox pagination, and NodeInfo discovery.
"""

import email.utils
import json
import time
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from socialize.models import Activity, Actor, Follow, Object
from socialize.services import ActivityService, ActorService
from socialize.signatures import (
    build_digest,
    build_signed_headers,
    generate_key_pair,
    verify_http_signature,
)


class HttpSignaturesTestCase(TestCase):
    """Tests draft-cavage HTTP Signatures signing and verification."""

    def setUp(self):
        self.privkey, self.pubkey = generate_key_pair()
        self.key_id = "https://example.com/users/alice#main-key"
        self.factory = RequestFactory()

    def test_key_pair_generation(self):
        """Test RSA key pair generation."""
        self.assertTrue(self.privkey.startswith("-----BEGIN RSA PRIVATE KEY-----"))
        self.assertTrue(self.pubkey.startswith("-----BEGIN PUBLIC KEY-----"))

    def test_build_digest(self):
        """Test SHA-256 Digest header calculation."""
        payload = b'{"hello": "fediverse"}'
        digest = build_digest(payload)
        self.assertTrue(digest.startswith("SHA-256="))

    def test_sign_and_verify_request(self):
        """Test roundtrip outbound signing and inbound verification."""
        body = b'{"type": "Follow", "actor": "https://example.com/users/alice"}'
        headers = build_signed_headers(
            private_key_pem=self.privkey,
            key_id=self.key_id,
            method="POST",
            target_url="https://target.com/users/bob/inbox",
            body=body,
        )

        # Convert headers for Django RequestFactory
        req_headers = {
            "HTTP_HOST": "target.com",
            "HTTP_DATE": headers["Date"],
            "HTTP_DIGEST": headers["Digest"],
            "HTTP_SIGNATURE": headers["Signature"],
            "CONTENT_TYPE": headers.get("Content-Type", "application/activity+json"),
        }
        request = self.factory.post(
            "/users/bob/inbox",
            data=body,
            content_type="application/activity+json",
            **req_headers,
        )

        valid, resolved_key = verify_http_signature(
            request,
            fetch_actor_fn=lambda k: self.pubkey,
        )
        self.assertTrue(valid)
        self.assertEqual(resolved_key, self.key_id)

    def test_tampered_body_rejected(self):
        """Test that modified payload body fails digest check."""
        body = b'{"type": "Follow"}'
        headers = build_signed_headers(
            private_key_pem=self.privkey,
            key_id=self.key_id,
            method="POST",
            target_url="https://target.com/inbox",
            body=body,
        )

        # Send tampered body with original digest
        tampered_body = b'{"type": "Hacked"}'
        req_headers = {
            "HTTP_HOST": "target.com",
            "HTTP_DATE": headers["Date"],
            "HTTP_DIGEST": headers["Digest"],
            "HTTP_SIGNATURE": headers["Signature"],
            "CONTENT_TYPE": "application/activity+json",
        }
        request = self.factory.post(
            "/inbox",
            data=tampered_body,
            content_type="application/activity+json",
            **req_headers,
        )

        valid, error = verify_http_signature(
            request,
            fetch_actor_fn=lambda k: self.pubkey,
        )
        self.assertFalse(valid)
        self.assertIn("Digest header mismatch", error)

    def test_expired_date_rejected(self):
        """Test that date older than 300s is rejected."""
        body = b"{}"
        headers = build_signed_headers(
            private_key_pem=self.privkey,
            key_id=self.key_id,
            method="POST",
            target_url="https://target.com/inbox",
            body=body,
        )

        expired_date = email.utils.formatdate(time.time() - 600, usegmt=True)
        req_headers = {
            "HTTP_HOST": "target.com",
            "HTTP_DATE": expired_date,
            "HTTP_DIGEST": headers["Digest"],
            "HTTP_SIGNATURE": headers["Signature"],
            "CONTENT_TYPE": "application/activity+json",
        }
        request = self.factory.post(
            "/inbox",
            data=body,
            content_type="application/activity+json",
            **req_headers,
        )

        valid, error = verify_http_signature(
            request,
            fetch_actor_fn=lambda k: self.pubkey,
        )
        self.assertFalse(valid)
        self.assertIn("Date header has expired", error)


class ActivityPubFederationVerbsTestCase(TestCase):
    """Tests inbound ActivityPub verb handlers and task queue integration."""

    def setUp(self):
        self.factory = RequestFactory()
        self.actor_service = ActorService()
        self.activity_service = ActivityService()

        # Create local user & actor
        self.local_user = User.objects.create_user(
            username="alice", email="alice@atria.local"
        )
        self.local_actor = self.actor_service.create_actor({"username": "alice"})

        # Create remote actor fixture
        self.remote_actor = Actor.objects.create(
            actor_url="https://mastodon.social/users/bob",
            username="bob",
            domain="mastodon.social",
            inbox="https://mastodon.social/users/bob/inbox",
            outbox="https://mastodon.social/users/bob/outbox",
            public_key="fake-pubkey",
        )

    @patch("socialize.tasks.deliver_activity_task.delay")
    def test_inbound_follow_verb(self, mock_deliver):
        """Test receiving a Follow activity: creates Follow record and enqueues Accept delivery."""
        follow_activity = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "id": "https://mastodon.social/activities/follow-1",
            "type": "Follow",
            "actor": "https://mastodon.social/users/bob",
            "object": self.local_actor.get_actor_url(),
        }

        self.activity_service.process_inbound_activity(follow_activity)

        follow_obj = Follow.objects.filter(
            actor=self.remote_actor,
            target=self.local_actor,
        ).first()
        self.assertIsNotNone(follow_obj)
        self.assertTrue(follow_obj.accepted)

        # Verify an Accept activity was created and enqueued
        accept_activity = Activity.objects.filter(
            actor=self.local_actor,
            activity_type="Accept",
        ).first()
        self.assertIsNotNone(accept_activity)
        self.assertEqual(
            accept_activity.object_data["object"]["id"], follow_activity["id"]
        )
        mock_deliver.assert_called_once()

    def test_inbound_create_verb(self):
        """Test receiving a Create Note activity: persists Object and Activity."""
        create_activity = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "id": "https://mastodon.social/activities/create-1",
            "type": "Create",
            "actor": "https://mastodon.social/users/bob",
            "object": {
                "id": "https://mastodon.social/notes/1",
                "type": "Note",
                "content": "<p>Hello Fediverse!</p>",
                "summary": "Greeting",
                "attachment": [
                    {
                        "type": "Document",
                        "mediaType": "image/jpeg",
                        "url": "https://mastodon.social/media/1.jpg",
                    }
                ],
            },
        }

        self.activity_service.process_inbound_activity(create_activity)

        obj = Object.objects.filter(
            object_url="https://mastodon.social/notes/1"
        ).first()
        self.assertIsNotNone(obj)
        self.assertEqual(obj.content, "<p>Hello Fediverse!</p>")
        self.assertEqual(obj.object_type, "Note")
        self.assertEqual(len(obj.attachment), 1)

        act = Activity.objects.filter(
            activity_url="https://mastodon.social/activities/create-1"
        ).first()
        self.assertIsNotNone(act)
        self.assertEqual(act.activity_type, "Create")

    def test_inbound_like_verb(self):
        """Test receiving a Like activity: increments target author's score."""
        local_obj = Object.objects.create(
            actor=self.local_actor,
            content="My great article",
            object_type="Article",
        )
        initial_score = self.local_actor.score

        like_activity = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "id": "https://mastodon.social/activities/like-1",
            "type": "Like",
            "actor": "https://mastodon.social/users/bob",
            "object": local_obj.get_object_url(),
        }

        self.activity_service.process_inbound_activity(like_activity)

        self.local_actor.refresh_from_db()
        self.assertEqual(self.local_actor.score, initial_score + 1)

    def test_inbound_undo_follow_verb(self):
        """Test receiving an Undo Follow activity: deletes Follow record."""
        Follow.objects.create(
            actor=self.remote_actor,
            target=self.local_actor,
            accepted=True,
        )

        undo_activity = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "id": "https://mastodon.social/activities/undo-1",
            "type": "Undo",
            "actor": "https://mastodon.social/users/bob",
            "object": {
                "id": "https://mastodon.social/activities/follow-1",
                "type": "Follow",
                "actor": "https://mastodon.social/users/bob",
                "object": self.local_actor.get_actor_url(),
            },
        }

        self.activity_service.process_inbound_activity(undo_activity)

        self.assertFalse(
            Follow.objects.filter(
                actor=self.remote_actor,
                target=self.local_actor,
            ).exists()
        )


class ActivityPubCollectionsAndDiscoveryTestCase(TestCase):
    """Tests followers, following, outbox pagination, WebFinger, and NodeInfo endpoints."""

    def setUp(self):
        self.factory = RequestFactory()
        self.actor_service = ActorService()
        self.activity_service = ActivityService()

        self.user = User.objects.create_user(username="carol")
        self.actor = self.actor_service.create_actor({"username": "carol"})

        self.remote1 = Actor.objects.create(
            actor_url="https://remote.social/users/1",
            username="rem1",
        )
        self.remote2 = Actor.objects.create(
            actor_url="https://remote.social/users/2",
            username="rem2",
        )

        Follow.objects.create(actor=self.remote1, target=self.actor, accepted=True)
        Follow.objects.create(actor=self.actor, target=self.remote2, accepted=True)

    def test_followers_collection(self):
        """Test followers OrderedCollection endpoint."""
        req = self.factory.get("/users/carol/followers/")
        resp = self.actor_service.get_followers(req, "carol")
        self.assertEqual(resp.status_code, 200)

        data = json.loads(resp.content)
        self.assertEqual(data["type"], "OrderedCollection")
        self.assertEqual(data["totalItems"], 1)
        self.assertIn(self.remote1.get_actor_url(), data["orderedItems"])

    def test_following_collection(self):
        """Test following OrderedCollection endpoint."""
        req = self.factory.get("/users/carol/following/")
        resp = self.actor_service.get_following(req, "carol")
        self.assertEqual(resp.status_code, 200)

        data = json.loads(resp.content)
        self.assertEqual(data["type"], "OrderedCollection")
        self.assertEqual(data["totalItems"], 1)
        self.assertIn(self.remote2.get_actor_url(), data["orderedItems"])

    def test_outbox_pagination(self):
        """Test outbox base collection and paginated OrderedCollectionPage."""
        # Create 25 activities
        for i in range(25):
            Activity.objects.create(
                actor=self.actor,
                activity_type="Create",
                object_data={"type": "Note", "content": f"Note {i}"},
            )

        # Base outbox query without ?page
        req_base = self.factory.get("/users/carol/outbox/")
        resp_base = self.activity_service.get_activity(req_base, "carol")
        self.assertEqual(resp_base.status_code, 200)
        data_base = json.loads(resp_base.content)
        self.assertEqual(data_base["type"], "OrderedCollection")
        self.assertEqual(data_base["totalItems"], 25)
        self.assertIn("first", data_base)
        self.assertIn("last", data_base)

        # Page 1 query with ?page=1
        req_page1 = self.factory.get("/users/carol/outbox/?page=1")
        resp_page1 = self.activity_service.get_activity(req_page1, "carol")
        self.assertEqual(resp_page1.status_code, 200)
        data_page1 = json.loads(resp_page1.content)
        self.assertEqual(data_page1["type"], "OrderedCollectionPage")
        self.assertEqual(len(data_page1["orderedItems"]), 20)
        self.assertIn("next", data_page1)

    def test_webfinger_discovery(self):
        """Test WebFinger discovery endpoint."""
        req = self.factory.get(
            "/.well-known/webfinger?resource=acct:carol@localhost:8000"
        )
        resp = self.actor_service.get_webfinger(req)
        self.assertEqual(resp.status_code, 200)

        data = json.loads(resp.content)
        self.assertTrue(data["subject"].startswith("acct:carol@"))
        self.assertTrue(any(link["rel"] == "self" for link in data["links"]))

    def test_nodeinfo_discovery_and_schema(self):
        """Test .well-known/nodeinfo and nodeinfo/2.0 metadata."""
        req_disc = self.factory.get("/.well-known/nodeinfo")
        resp_disc = self.actor_service.get_nodeinfo_discovery(req_disc)
        self.assertEqual(resp_disc.status_code, 200)
        data_disc = json.loads(resp_disc.content)
        self.assertEqual(len(data_disc["links"]), 1)

        req_node = self.factory.get("/nodeinfo/2.0")
        resp_node = self.actor_service.get_nodeinfo_2_0(req_node)
        self.assertEqual(resp_node.status_code, 200)
        data_node = json.loads(resp_node.content)
        self.assertEqual(data_node["version"], "2.0")
        self.assertIn("activitypub", data_node["protocols"])
        self.assertIn("usage", data_node)
