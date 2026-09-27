from rest_framework import permissions, viewsets
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Activity, Agreement, AgreementContact, Contact, Document, Organization
from .permissions import PartnershipPermission
from .serializers import (
    ActivitySerializer, AgreementContactSerializer, AgreementSerializer, ContactSerializer,
    DocumentSerializer, OrganizationSerializer, PublicOrganizationSerializer,
)


class AuditModelViewSet(viewsets.ModelViewSet):
    permission_classes = [PartnershipPermission]

    def _audit_kwargs(self, serializer, *, creating=False):
        field_names = {field.name for field in serializer.Meta.model._meta.fields}
        kwargs = {}
        if creating and "created_by" in field_names:
            kwargs["created_by"] = self.request.user
        if "updated_by" in field_names:
            kwargs["updated_by"] = self.request.user
        return kwargs

    def perform_create(self, serializer):
        serializer.save(**self._audit_kwargs(serializer, creating=True))

    def perform_update(self, serializer):
        serializer.save(**self._audit_kwargs(serializer))


class OrganizationViewSet(AuditModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer


class AgreementViewSet(AuditModelViewSet):
    queryset = Agreement.objects.all()
    serializer_class = AgreementSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        organization_id = self.request.query_params.get("organization")
        if organization_id:
            queryset = queryset.filter(organization_id=organization_id)
        return queryset


class ContactViewSet(AuditModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer


class AgreementContactViewSet(AuditModelViewSet):
    queryset = AgreementContact.objects.all()
    serializer_class = AgreementContactSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        agreement_id = self.request.query_params.get("agreement")
        if agreement_id:
            queryset = queryset.filter(agreement_id=agreement_id)
        return queryset


class DocumentViewSet(AuditModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        queryset = super().get_queryset()
        agreement_id = self.request.query_params.get("agreement")
        if agreement_id:
            queryset = queryset.filter(agreement_id=agreement_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


class ActivityViewSet(AuditModelViewSet):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        agreement_id = self.request.query_params.get("agreement")
        if agreement_id:
            queryset = queryset.filter(agreement_id=agreement_id)
        return queryset


class PublicOrganizationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Organization.objects.filter(is_public=True)
    serializer_class = PublicOrganizationSerializer
    permission_classes = [permissions.AllowAny]


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({"id": user.id, "username": user.username, "first_name": user.first_name, "last_name": user.last_name, "email": user.email})
