from rest_framework.permissions import BasePermission


class PartnershipPermission(BasePermission):
    """Allow authenticated superusers/editors full CRUD and viewers read-only."""

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
