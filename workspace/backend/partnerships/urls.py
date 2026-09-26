"""Routing for the partnerships API."""

from rest_framework.routers import DefaultRouter

from .views import (
    ActivityViewSet,
    AgreementContactViewSet,
    AgreementViewSet,
    ContactViewSet,
    DocumentViewSet,
    OrganizationViewSet,
    PublicOrganizationViewSet,
)

router = DefaultRouter()
router.register("organizations", OrganizationViewSet, basename="organization")
router.register("agreements", AgreementViewSet, basename="agreement")
router.register("contacts", ContactViewSet, basename="contact")
router.register("agreement-contacts", AgreementContactViewSet, basename="agreement-contact")
router.register("documents", DocumentViewSet, basename="document")
router.register("activities", ActivityViewSet, basename="activity")

public_router = DefaultRouter()
public_router.register("organizations", PublicOrganizationViewSet, basename="public-organization")

urlpatterns = router.urls
public_urlpatterns = public_router.urls
