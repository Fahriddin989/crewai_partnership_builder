"""Routing for the partnerships API."""
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ActivityViewSet, AcademicUnitViewSet, AgreementContactViewSet, AgreementViewSet, ContactViewSet, DashboardView, DocumentViewSet, OrganizationMediaViewSet, OrganizationNoteAttachmentDownloadView, OrganizationNoteAttachmentViewSet, OrganizationNoteViewSet, OrganizationViewSet, PublicOrganizationViewSet
router = DefaultRouter()
router.register("organizations", OrganizationViewSet, basename="organization")
router.register("academic-units", AcademicUnitViewSet, basename="academic-unit")
router.register("organization-notes", OrganizationNoteViewSet, basename="organization-note")
router.register("organization-note-attachments", OrganizationNoteAttachmentViewSet, basename="organization-note-attachment")
router.register("agreements", AgreementViewSet, basename="agreement")
router.register("contacts", ContactViewSet, basename="contact")
router.register("agreement-contacts", AgreementContactViewSet, basename="agreement-contact")
router.register("documents", DocumentViewSet, basename="document")
router.register("organization-media", OrganizationMediaViewSet, basename="organization-media")
router.register("activities", ActivityViewSet, basename="activity")
public_router = DefaultRouter(); public_router.register("organizations", PublicOrganizationViewSet, basename="public-organization")
urlpatterns = [path("dashboard/", DashboardView.as_view(), name="dashboard"), path("organization-note-attachments/<int:pk>/download/", OrganizationNoteAttachmentDownloadView.as_view(), name="organization-note-attachment-download")] + router.urls
public_urlpatterns = public_router.urls
