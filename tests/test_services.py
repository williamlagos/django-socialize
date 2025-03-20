"""Test Service classes."""

import json

from unittest.mock import patch, MagicMock
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User

from socialize.models import Actor, Activity, Object, Vault, Token
from socialize.services import (
    ActorService, ActivityService, ObjectService, VaultService, AuthenticationService
)


class ActorServiceTest(TestCase):
    """Test ActorService class."""

    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()
        self.actor_service = ActorService()
        self.actor = Actor.objects.create(username="testuser")

    def test_get_actor(self):
        """Test get_actor method."""
        request = self.factory.get("/actor/testuser")
        response = self.actor_service.get_actor(request, "testuser")
        self.assertEqual(response.status_code, 200)

    def test_create_actor(self):
        """Test create_actor method."""
        data = {"username": "newuser"}
        actor = self.actor_service.create_actor(data)
        self.assertEqual(actor.username, "newuser")

    @patch("socialize.services.ActorService.generate_keys")
    def test_generate_keys(self, mock_generate_keys):
        """Test generate_keys method."""
        mock_generate_keys.return_value = ("private_key", "public_key")
        private_key, public_key = self.actor_service.generate_keys()
        self.assertEqual(private_key, "private_key")
        self.assertEqual(public_key, "public_key")


class ActivityServiceTest(TestCase):
    """Test ActivityService class."""

    def setUp(self):
        self.factory = RequestFactory()
        self.activity_service = ActivityService()
        self.actor = Actor.objects.create(username="testuser")

    def test_create_activity(self):
        """Test create_activity method."""
        request = self.factory.post(
            "/inbox/testuser",
            data=json.dumps({"type": "Create", "object": "TestObject"}),
            content_type="application/json",
        )
        response = self.activity_service.create_activity(request, "testuser")
        self.assertEqual(response.status_code, 202)

    def test_get_activity(self):
        """Test get_activity method."""
        Activity.objects.create(actor=self.actor, object_data={
                                "type": "Test"}, activity_type="Create")
        request = self.factory.get("/outbox/testuser")
        response = self.activity_service.get_activity(request, "testuser")
        self.assertEqual(response.status_code, 200)


class ObjectServiceTest(TestCase):
    """Test ObjectService class."""

    def setUp(self):
        self.factory = RequestFactory()
        self.object_service = ObjectService()
        self.actor = Actor.objects.create(username="testuser")

    def test_get_object(self):
        """Test get_object method."""
        obj = Object.objects.create(
            actor=self.actor, object_type="Note", content="Test content")
        request = self.factory.get(f"/object/{obj.id}")
        response = self.object_service.get_object(request, obj.id)
        self.assertEqual(response.status_code, 200)

    def test_create_object(self):
        """Test create_object method."""
        request = self.factory.post(
            "/object/testuser",
            data=json.dumps({"type": "Note", "content": "Test content"}),
            content_type="application/json",
        )
        response = self.object_service.create_object(request, "testuser")
        self.assertEqual(response.status_code, 200)


class VaultServiceTest(TestCase):
    """Test VaultService class."""

    def setUp(self):
        """Set up test data."""
        self.vault_service = VaultService()
        self.actor = Actor.objects.create(username="testuser")
        Vault.objects.create(actor=self.actor, private_key="private_key")

    def test_get_private_key(self):
        """Test get_private_key method."""
        private_key = self.vault_service.get_private_key("testuser")
        self.assertEqual(private_key, "private_key")

    def test_check_user_vault(self):
        """Test check_user_vault method."""
        response = self.vault_service.check_user_vault("testuser")
        self.assertEqual(response.status_code, 200)


class AuthenticationServiceTest(TestCase):
    """Test AuthenticationService class."""

    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()
        self.auth_service = AuthenticationService()
        self.user = User.objects.create_user(
            username="testuser", password="password")

    @patch("socialize.services.authenticate")
    @patch("socialize.services.login")
    def test_authenticate(self, _, mock_authenticate):
        """Test authenticate method."""
        mock_authenticate.return_value = self.user
        request = self.factory.post("/auth")
        response = self.auth_service.authenticate(
            request, {"username": "testuser"}, "access_token")
        self.assertEqual(response.status_code, 200)

    @patch("requests.get")
    def test_verify_access_token(self, mock_get):
        """Test verify_access_token method."""
        mock_get.return_value = MagicMock(status_code=200, json=lambda: {
                                          "email": "test@example.com"})
        response = self.auth_service.verify_access_token(
            "google", "valid_token")
        self.assertIsNotNone(response)
