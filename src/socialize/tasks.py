"""
Celery background tasks for ActivityPub delivery and asynchronous activity processing.
"""

import json
import logging

import requests

from .models import Activity, Vault
from .signatures import build_signed_headers

logger = logging.getLogger(__name__)

try:
    from celery import shared_task
except ImportError:
    # Fallback decorator when Celery is not installed
    def shared_task(*args, **kwargs):
        def decorator(fn):
            fn.delay = lambda *a, **k: fn(*a, **k)
            return fn

        if args and callable(args[0]):
            return decorator(args[0])
        return decorator


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def deliver_activity_task(self, activity_id: str, recipient_inbox_urls: list[str]):
    """
    Asynchronously delivers a signed ActivityPub activity payload to recipient inboxes.
    """
    try:
        activity = Activity.objects.select_related("actor").get(id=activity_id)
    except Activity.DoesNotExist:
        logger.error(f"Activity {activity_id} not found for delivery")
        return

    actor = activity.actor
    vault = Vault.objects.filter(actor=actor).first()
    if not vault or not vault.private_key:
        logger.error(f"Vault or private key not found for actor {actor.id}")
        return

    payload_dict = activity.as_activitypub()
    body_bytes = json.dumps(payload_dict).encode("utf-8")
    key_id = f"{actor.get_actor_url()}#main-key"

    for inbox_url in set(recipient_inbox_urls):
        if not inbox_url:
            continue
        try:
            signed_headers = build_signed_headers(
                private_key_pem=vault.private_key,
                key_id=key_id,
                method="POST",
                target_url=inbox_url,
                body=body_bytes,
            )
            response = requests.post(
                inbox_url,
                data=body_bytes,
                headers=signed_headers,
                timeout=10,
            )
            logger.info(
                f"Delivered activity {activity_id} to {inbox_url}: {response.status_code}"
            )
        except Exception as exc:
            logger.warning(
                f"Failed to deliver activity {activity_id} to {inbox_url}: {exc}"
            )
            # Retry entire task if all failed, or log and continue


@shared_task
def process_inbound_activity_task(
    activity_data: dict, sender_key_id: str | None = None
):
    """
    Asynchronously processes an accepted inbound activity.
    """
    from .services import ActivityService

    service = ActivityService()
    service.process_inbound_activity(activity_data, sender_key_id)
