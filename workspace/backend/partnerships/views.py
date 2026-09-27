from rest_framework import permissions, viewsets
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Activity, Agreement, AgreementContact, Contact, Document, Organization, OrganizationMedia
from .permissions import PartnershipPermission
from .serializers import ActivitySerializer, AgreementContactSerializer, AgreementSerializer, ContactSerializer, DocumentSerializer, OrganizationMediaSerializer, OrganizationSerializer, PublicOrganizationDetailSerializer, PublicOrganizationSerializer

class AuditModelViewSet(viewsets.ModelViewSet):
    permission_classes = [PartnershipPermission]
    def _audit_kwargs(self, serializer, *, creating=False):
        names = {field.name for field in serializer.Meta.model._meta.fields}; kwargs = {}
        if creating and "created_by" in names: kwargs["created_by"] = self.request.user
        if "updated_by" in names: kwargs["updated_by"] = self.request.user
        return kwargs
    def perform_create(self, serializer): serializer.save(**self._audit_kwargs(serializer, creating=True))
    def perform_update(self, serializer): serializer.save(**self._audit_kwargs(serializer))

class OrganizationViewSet(AuditModelViewSet):
    queryset = Organization.objects.all(); serializer_class = OrganizationSerializer
class AgreementViewSet(AuditModelViewSet):
    queryset = Agreement.objects.all(); serializer_class = AgreementSerializer
    def get_queryset(self):
        qs = super().get_queryset(); value = self.request.query_params.get("organization")
        return qs.filter(organization_id=value) if value else qs
class ContactViewSet(AuditModelViewSet):
    queryset = Contact.objects.all(); serializer_class = ContactSerializer
class AgreementContactViewSet(AuditModelViewSet):
    queryset = AgreementContact.objects.all(); serializer_class = AgreementContactSerializer
    def get_queryset(self):
        qs = super().get_queryset(); value = self.request.query_params.get("agreement")
        return qs.filter(agreement_id=value) if value else qs
class DocumentViewSet(AuditModelViewSet):
    queryset = Document.objects.all(); serializer_class = DocumentSerializer; parser_classes = [MultiPartParser, FormParser, JSONParser]
    def get_queryset(self):
        qs = super().get_queryset(); value = self.request.query_params.get("agreement")
        return qs.filter(agreement_id=value) if value else qs
    def perform_create(self, serializer): serializer.save(uploaded_by=self.request.user)
class OrganizationMediaViewSet(AuditModelViewSet):
    queryset = OrganizationMedia.objects.all(); serializer_class = OrganizationMediaSerializer; parser_classes = [MultiPartParser, FormParser, JSONParser]
    def get_queryset(self):
        qs = super().get_queryset(); value = self.request.query_params.get("organization")
        return qs.filter(organization_id=value) if value else qs
    def perform_create(self, serializer): serializer.save(uploaded_by=self.request.user)
class ActivityViewSet(AuditModelViewSet):
    queryset = Activity.objects.all(); serializer_class = ActivitySerializer
    def get_queryset(self):
        qs = super().get_queryset(); value = self.request.query_params.get("agreement")
        return qs.filter(agreement_id=value) if value else qs

class PublicOrganizationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Organization.objects.filter(is_public=True); permission_classes = [permissions.AllowAny]
    def get_serializer_class(self): return PublicOrganizationDetailSerializer if self.action == "retrieve" else PublicOrganizationSerializer

class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        user = request.user
        return Response({"id": user.id, "username": user.username, "first_name": user.first_name, "last_name": user.last_name, "email": user.email})
