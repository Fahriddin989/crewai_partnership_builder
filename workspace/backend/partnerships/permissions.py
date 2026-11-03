from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission


class PartnershipPermission(BasePermission):
    """Allow editors CRUD and viewers read-only; writes use organization ownership."""

    editor_group = "Partnership Editors"
    viewer_group = "Partnership Viewers"

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser or user.groups.filter(name=self.editor_group).exists():
            return True
        return request.method in ("GET", "HEAD", "OPTIONS") and user.groups.filter(
            name=self.viewer_group
        ).exists()


def organization_for(obj):
    """Resolve an organization's ownership for a related partnership record."""
    if hasattr(obj, "academic_units") and hasattr(obj, "created_by_id"):
        return obj
    if hasattr(obj, "organization_id"):
        return getattr(obj, "organization", None)
    if hasattr(obj, "agreement_id"):
        agreement = getattr(obj, "agreement", None)
        return getattr(agreement, "organization", None)
    if hasattr(obj, "note_id"):
        note = getattr(obj, "note", None)
        return getattr(note, "organization", None)
    return None


def owns_related_object(user, obj):
    if user.is_superuser:
        return True
    organization = organization_for(obj)
    return bool(organization and organization.created_by_id == user.id)


def require_owned_organization(user, organization):
    if not user.is_superuser and (not organization or organization.created_by_id != user.id):
        raise PermissionDenied("You do not have permission to modify this organization.")
