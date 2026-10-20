from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import AcademicUnit, Organization, OrganizationAcademicUnit, OrganizationNote


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


class AcademicUnitAndOrganizationWorkspaceTests(AuthenticationAndPermissionsTests):
    def test_editor_creates_academic_unit(self):
        self.authenticate(self.editor)
        response = self.client.post("/api/academic-units/", {"name": "Artificial Intelligence", "category": "Program"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_viewer_cannot_create_academic_unit(self):
        self.authenticate(self.viewer)
        self.assertEqual(self.client.post("/api/academic-units/", {"name": "X", "category": "Unit"}, format="json").status_code, status.HTTP_403_FORBIDDEN)

    def test_viewer_can_get_academic_units(self):
        self.authenticate(self.viewer)
        self.assertEqual(self.client.get("/api/academic-units/").status_code, status.HTTP_200_OK)

    def test_editor_can_patch_academic_unit(self):
        unit = AcademicUnit.objects.create(name="Old", category="Program")
        self.authenticate(self.editor)
        response = self.client.patch(f"/api/academic-units/{unit.pk}/", {"name": "New"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "New")

    def test_academic_unit_cannot_parent_itself(self):
        unit = AcademicUnit.objects.create(name="Unit", category="Faculty")
        self.authenticate(self.editor)
        response = self.client.patch(f"/api/academic-units/{unit.pk}/", {"parent": unit.pk}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_circular_academic_unit_hierarchy_is_rejected(self):
        a = AcademicUnit.objects.create(name="A", category="Faculty")
        b = AcademicUnit.objects.create(name="B", category="Department", parent=a)
        c = AcademicUnit.objects.create(name="C", category="Program", parent=b)
        self.authenticate(self.editor)
        response = self.client.patch(f"/api/academic-units/{a.pk}/", {"parent": c.pk}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        a.parent = c
        with self.assertRaises(ValidationError):
            a.clean()

    def test_organization_relationship_crud_and_many_to_many(self):
        one = AcademicUnit.objects.create(name="One", category="Department")
        two = AcademicUnit.objects.create(name="Two", category="Program")
        self.authenticate(self.editor)
        response = self.client.post("/api/organizations/", {"name": "Partner", "organization_type": "COMPANY", "country": "US", "academic_unit_ids": [one.pk, two.pk]}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        org_id = response.data["id"]
        self.assertEqual(len(response.data["academic_units"]), 2)
        other_response = self.client.post("/api/organizations/", {"name": "Other", "organization_type": "COMPANY", "country": "US", "academic_unit_ids": [one.pk]}, format="json")
        self.assertEqual(other_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(one.organizations.count(), 2)
        update = self.client.patch(f"/api/organizations/{org_id}/", {"academic_unit_ids": [one.pk, one.pk]}, format="json")
        self.assertEqual(update.status_code, status.HTTP_200_OK)
        self.assertEqual(OrganizationAcademicUnit.objects.filter(organization_id=org_id).count(), 1)
        self.assertEqual(self.client.get("/api/organizations/", {"academic_unit": two.pk}).data[0]["id"], org_id)
        filtered = self.client.get("/api/organizations/", {"academic_unit": 99999})
        self.assertEqual(filtered.data, [])

    def test_inactive_link_survives_without_relationship_update(self):
        unit = AcademicUnit.objects.create(name="Historical", category="Department", is_active=False)
        org = Organization.objects.create(name="Partner", organization_type="COMPANY", country="US")
        OrganizationAcademicUnit.objects.create(organization=org, academic_unit=unit)
        self.authenticate(self.editor)
        self.client.patch(f"/api/organizations/{org.pk}/", {"name": "Updated"}, format="json")
        self.assertTrue(org.academic_units.filter(pk=unit.pk).exists())

    def test_notes_permissions_audit_filter_order_and_crud(self):
        self.authenticate(self.editor)
        create = self.client.post("/api/organization-notes/", {"organization": self.public_org.pk, "body": "First", "next_step": "Send details"}, format="json")
        self.assertEqual(create.status_code, status.HTTP_201_CREATED)
        note_id = create.data["id"]
        self.assertEqual(create.data["created_by"], self.editor.pk)
        later = self.client.post("/api/organization-notes/", {"organization": self.private_org.pk, "body": "Later"}, format="json")
        self.assertEqual(later.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.client.get("/api/organization-notes/", {"organization": self.public_org.pk}).data[0]["id"], note_id)
        self.assertEqual(self.client.get("/api/organization-notes/").data[0]["id"], later.data["id"])
        self.assertEqual(self.client.patch(f"/api/organization-notes/{note_id}/", {"body": "Updated"}, format="json").status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.delete(f"/api/organization-notes/{note_id}/").status_code, status.HTTP_204_NO_CONTENT)

    def test_viewer_can_read_but_not_create_notes(self):
        self.authenticate(self.viewer)
        self.assertEqual(self.client.get("/api/organization-notes/").status_code, status.HTTP_200_OK)
        response = self.client.post("/api/organization-notes/", {"organization": self.public_org.pk, "body": "No"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_public_api_does_not_expose_notes_or_academic_units(self):
        unit = AcademicUnit.objects.create(name="Internal", category="Program")
        self.public_org.academic_units.add(unit)
        OrganizationNote.objects.create(organization=self.public_org, body="Internal note", next_step="Private", follow_up_date="2026-10-20", created_by=self.editor)
        response = self.client.get(f"/api/public/organizations/{self.public_org.pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn("academic_units", response.data)
        self.assertNotIn("academic_unit_ids", response.data)
        self.assertNotIn("notes", response.data)
        self.assertNotIn("next_step", response.data)
        self.assertNotIn("follow_up_date", response.data)
        self.assertNotIn("created_by", response.data)
