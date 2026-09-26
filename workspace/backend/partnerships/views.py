from rest_framework import permissions, viewsets
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser

from .models import Activity, Agreement, AgreementContact, Contact, Document, Organization
from .serializers import (
    ActivitySerializer,
    AgreementContactSerializer,
    AgreementSerializer,
    ContactSerializer,
    DocumentSerializer,
    OrganizationSerializer,
    PublicOrganizationSerializer,
)


class AuditModelViewSet(viewsets.ModelViewSet):
    """Authenticated CRUD base that owns server-side audit assignments."""

    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class OrganizationViewSet(AuditModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer


class AgreementViewSet(AuditModelViewSet):
    queryset = Agreement.objects.all()
    serializer_class = AgreementSerializer


class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [permissions.IsAuthenticated]


class AgreementContactViewSet(viewsets.ModelViewSet):
    queryset = AgreementContact.objects.all()
    serializer_class = AgreementContactSerializer
    permission_classes = [permissions.IsAuthenticated]


class DocumentViewSet(AuditModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]


class ActivityViewSet(AuditModelViewSet):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer


class PublicOrganizationViewSet(viewsets.ReadOnlyModelViewSet):
    """Unauthenticated public directory exposing only explicitly public organizations."""

    queryset = Organization.objects.filter(is_public=True)
    serializer_class = PublicOrganizationSerializer
    permission_classes = [permissions.AllowAny]
