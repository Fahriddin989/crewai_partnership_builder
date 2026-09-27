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

    def perform_create(self, serializer):
        model = serializer.Meta.model
        field_names = {field.name for field in model._meta.fields}

        save_kwargs = {}

        if "created_by" in field_names:
            save_kwargs["created_by"] = self.request.user

        if "updated_by" in field_names:
            save_kwargs["updated_by"] = self.request.user

        serializer.save(**save_kwargs)

    def perform_update(self, serializer):
        model = serializer.Meta.model
        field_names = {field.name for field in model._meta.fields}

        save_kwargs = {}

        if "updated_by" in field_names:
            save_kwargs["updated_by"] = self.request.user

        serializer.save(**save_kwargs)


class OrganizationViewSet(AuditModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer


class AgreementViewSet(AuditModelViewSet):
    queryset = Agreement.objects.all()
    serializer_class = AgreementSerializer


class ContactViewSet(AuditModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer


class AgreementContactViewSet(AuditModelViewSet):
    queryset = AgreementContact.objects.all()
    serializer_class = AgreementContactSerializer


class DocumentViewSet(AuditModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


class ActivityViewSet(AuditModelViewSet):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer


class PublicOrganizationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Organization.objects.filter(is_public=True)
    serializer_class = PublicOrganizationSerializer
    permission_classes = [permissions.AllowAny]


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id": user.id, "username": user.username, "first_name": user.first_name,
            "last_name": user.last_name, "email": user.email,
        })
