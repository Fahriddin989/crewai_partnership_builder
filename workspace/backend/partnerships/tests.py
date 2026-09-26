from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Organization


class AuthenticationAndPermissionsTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.password = "test-password-123"
        cls.editor = User.objects.create_user("editor", password=cls.password, first_name="Edit", last_name="User", email="editor@example.com")
        cls.viewer = User.objects.create_user("viewer", password=cls.password)
        cls.unrelated = User.objects.create_user("unrelated", password=cls.password)
        cls.superuser = User.objects.create_superuser("admin", password=cls.password)
        cls.editor.groups.add(Group.objects.get(name="Partnership Editors"))
        cls.viewer.groups.add(Group.objects.get(name="Partnership Viewers"))
        cls.public_org = Organization.objects.create(name="Public University", organization_type="UNIVERSITY", country="US", website="https://public.example", description="private description", is_public=True)
        cls.private_org = Organization.objects.create(name="Private Partner", organization_type="COMPANY", country="UK", description="confidential", is_public=False)

    def authenticate(self, user):
        response = self.client.post(reverse("token_obtain_pair"), {"username": user.username, "password": self.password}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")

    def test_public_organizations_works_anonymously(self):
        response = self.client.get("/api/public/organizations/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_anonymous_internal_organizations_is_denied(self):
        self.assertEqual(self.client.get("/api/organizations/").status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_me_is_denied(self):
        self.assertEqual(self.client.get("/api/auth/me/").status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_endpoint_returns_access_and_refresh(self):
        response = self.client.post("/api/auth/token/", {"username": "editor", "password": self.password}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_me_returns_only_expected_fields(self):
        self.authenticate(self.editor)
        response = self.client.get("/api/auth/me/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data), {"id", "username", "first_name", "last_name", "email"})

    def test_viewer_can_get_organizations(self):
        self.authenticate(self.viewer)
        self.assertEqual(self.client.get("/api/organizations/").status_code, status.HTTP_200_OK)

    def test_viewer_cannot_post_organizations(self):
        self.authenticate(self.viewer)
        response = self.client.post("/api/organizations/", {"name": "Nope", "organization_type": "NGO", "country": "US"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_editor_can_get_organizations(self):
        self.authenticate(self.editor)
        self.assertEqual(self.client.get("/api/organizations/").status_code, status.HTTP_200_OK)

    def test_editor_can_post_organizations(self):
        self.authenticate(self.editor)
        response = self.client.post("/api/organizations/", {"name": "New Partner", "organization_type": "NGO", "country": "US"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_unrelated_user_cannot_get_internal_organizations(self):
        self.authenticate(self.unrelated)
        self.assertEqual(self.client.get("/api/organizations/").status_code, status.HTTP_403_FORBIDDEN)

    def test_superuser_can_get_and_post(self):
        self.authenticate(self.superuser)
        self.assertEqual(self.client.get("/api/organizations/").status_code, status.HTTP_200_OK)
        response = self.client.post("/api/organizations/", {"name": "Admin Partner", "organization_type": "NGO", "country": "US"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_public_endpoint_does_not_expose_private_fields(self):
        response = self.client.get("/api/public/organizations/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn("description", response.data[0])
        self.assertNotIn("is_public", response.data[0])
        self.assertNotIn("created_by", response.data[0])
