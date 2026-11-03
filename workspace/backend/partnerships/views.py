from django.http import FileResponse, Http404
from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Activity, AcademicUnit, Agreement, AgreementContact, Contact, Document, Organization, OrganizationMedia, OrganizationNote, OrganizationNoteAttachment
from .permissions import PartnershipPermission, owns_related_object, organization_for, require_owned_organization
from .serializers import ActivitySerializer, AcademicUnitSerializer, AgreementContactSerializer, AgreementSerializer, ContactSerializer, DocumentSerializer, OrganizationMediaSerializer, OrganizationNoteAttachmentSerializer, OrganizationNoteSerializer, OrganizationSerializer, PublicOrganizationDetailSerializer, PublicOrganizationSerializer


class AuditModelViewSet(viewsets.ModelViewSet):
    permission_classes = [PartnershipPermission]

    def _audit_kwargs(self, serializer, *, creating=False):
        names = {field.name for field in serializer.Meta.model._meta.fields}
        kwargs = {}
        if creating and "created_by" in names:
            kwargs["created_by"] = self.request.user
        if "updated_by" in names:
            kwargs["updated_by"] = self.request.user
        return kwargs

    def perform_create(self, serializer):
        serializer.save(**self._audit_kwargs(serializer, creating=True))

    def perform_update(self, serializer):
        serializer.save(**self._audit_kwargs(serializer))

    def perform_destroy(self, instance):
        require_owned_organization(self.request.user, organization_for(instance))
        super().perform_destroy(instance)


class AcademicUnitViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AcademicUnit.objects.all()
    serializer_class = AcademicUnitSerializer
    permission_classes = [PartnershipPermission]


class OrganizationViewSet(AuditModelViewSet):
    queryset = Organization.objects.prefetch_related("academic_units").all()
    serializer_class = OrganizationSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        value = self.request.query_params.get("academic_unit")
        return qs.filter(academic_units__id=value).distinct() if value else qs

    def perform_update(self, serializer):
        require_owned_organization(self.request.user, serializer.instance)
        super().perform_update(serializer)

    def perform_destroy(self, instance):
        require_owned_organization(self.request.user, instance)
        super(AuditModelViewSet, self).perform_destroy(instance)


class OrganizationNoteViewSet(AuditModelViewSet):
    queryset = OrganizationNote.objects.select_related("organization", "created_by", "updated_by").all()
    serializer_class = OrganizationNoteSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_superuser:
            qs = qs.filter(organization__created_by_id=self.request.user.id)
        value = self.request.query_params.get("organization")
        return qs.filter(organization_id=value) if value else qs

    def perform_create(self, serializer):
        require_owned_organization(self.request.user, serializer.validated_data.get("organization"))
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        require_owned_organization(self.request.user, serializer.instance.organization)
        require_owned_organization(self.request.user, serializer.validated_data.get("organization", serializer.instance.organization))
        serializer.save(created_by=serializer.instance.created_by, updated_by=self.request.user)


class OrganizationNoteAttachmentViewSet(AuditModelViewSet):
    queryset = OrganizationNoteAttachment.objects.select_related("note__organization", "uploaded_by").all()
    serializer_class = OrganizationNoteAttachmentSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_superuser:
            qs = qs.filter(note__organization__created_by_id=self.request.user.id)
        value = self.request.query_params.get("note")
        return qs.filter(note_id=value) if value else qs

    def perform_create(self, serializer):
        require_owned_organization(self.request.user, serializer.validated_data["note"].organization)
        serializer.save(uploaded_by=self.request.user)

    def perform_update(self, serializer):
        require_owned_organization(self.request.user, serializer.instance.note.organization)
        note = serializer.validated_data.get("note", serializer.instance.note)
        require_owned_organization(self.request.user, note.organization)
        serializer.save(uploaded_by=serializer.instance.uploaded_by)


class AgreementViewSet(AuditModelViewSet):
    queryset = Agreement.objects.select_related("organization").all()
    serializer_class = AgreementSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        value = self.request.query_params.get("organization")
        return qs.filter(organization_id=value) if value else qs

    def perform_create(self, serializer):
        require_owned_organization(self.request.user, serializer.validated_data.get("organization"))
        super().perform_create(serializer)

    def perform_update(self, serializer):
        require_owned_organization(self.request.user, serializer.instance.organization)
        require_owned_organization(self.request.user, serializer.validated_data.get("organization", serializer.instance.organization))
        super().perform_update(serializer)


class ContactViewSet(AuditModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_superuser:
            qs = qs.filter(organization__created_by_id=self.request.user.id)
        return qs

    def perform_create(self, serializer):
        require_owned_organization(self.request.user, serializer.validated_data.get("organization"))
        super().perform_create(serializer)

    def perform_update(self, serializer):
        linked_organizations = Organization.objects.filter(agreements__agreement_contacts__contact=serializer.instance).distinct()
        if not self.request.user.is_superuser and linked_organizations.exclude(created_by_id=self.request.user.id).exists():
            raise PermissionDenied("This contact is linked to another department's organization.")
        require_owned_organization(self.request.user, serializer.validated_data.get("organization", serializer.instance.organization))
        super().perform_update(serializer)

    def perform_destroy(self, instance):
        linked_organizations = Organization.objects.filter(agreements__agreement_contacts__contact=instance).distinct()
        if not self.request.user.is_superuser and linked_organizations.exclude(created_by_id=self.request.user.id).exists():
            raise PermissionDenied("This contact is linked to another department's organization.")
        require_owned_organization(self.request.user, instance.organization)
        super(AuditModelViewSet, self).perform_destroy(instance)


class AgreementContactViewSet(AuditModelViewSet):
    queryset = AgreementContact.objects.select_related("agreement__organization", "contact__organization").all()
    serializer_class = AgreementContactSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        value = self.request.query_params.get("agreement")
        qs = qs.filter(agreement_id=value) if value else qs
        if not self.request.user.is_superuser:
            qs = qs.filter(agreement__organization__created_by_id=self.request.user.id)
        return qs

    def perform_create(self, serializer):
        require_owned_organization(self.request.user, serializer.validated_data["agreement"].organization)
        contact = serializer.validated_data["contact"]
        if contact.agreement_contacts.filter(agreement__organization__created_by_id__isnull=False).exclude(agreement__organization__created_by_id=self.request.user.id).exists():
            raise PermissionDenied("This contact is linked to another department's organization.")
        if contact.organization_id:
            require_owned_organization(self.request.user, contact.organization)
        super().perform_create(serializer)

    def perform_update(self, serializer):
        require_owned_organization(self.request.user, serializer.instance.agreement.organization)
        agreement = serializer.validated_data.get("agreement", serializer.instance.agreement)
        contact = serializer.validated_data.get("contact", serializer.instance.contact)
        require_owned_organization(self.request.user, agreement.organization)
        if contact.agreement_contacts.exclude(pk=serializer.instance.pk).filter(agreement__organization__created_by_id__isnull=False).exclude(agreement__organization__created_by_id=self.request.user.id).exists():
            raise PermissionDenied("This contact is linked to another department's organization.")
        if contact.organization_id:
            require_owned_organization(self.request.user, contact.organization)
        super().perform_update(serializer)


class DocumentViewSet(AuditModelViewSet):
    queryset = Document.objects.select_related("agreement__organization").all()
    serializer_class = DocumentSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        qs = super().get_queryset()
        value = self.request.query_params.get("agreement")
        return qs.filter(agreement_id=value) if value else qs

    def perform_create(self, serializer):
        require_owned_organization(self.request.user, serializer.validated_data["agreement"].organization)
        serializer.save(uploaded_by=self.request.user)

    def perform_update(self, serializer):
        require_owned_organization(self.request.user, serializer.instance.agreement.organization)
        require_owned_organization(self.request.user, serializer.validated_data.get("agreement", serializer.instance.agreement).organization)
        serializer.save(uploaded_by=serializer.instance.uploaded_by)


class OrganizationMediaViewSet(AuditModelViewSet):
    queryset = OrganizationMedia.objects.select_related("organization").all()
    serializer_class = OrganizationMediaSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        qs = super().get_queryset()
        value = self.request.query_params.get("organization")
        return qs.filter(organization_id=value) if value else qs

    def perform_create(self, serializer):
        require_owned_organization(self.request.user, serializer.validated_data["organization"])
        serializer.save(uploaded_by=self.request.user)

    def perform_update(self, serializer):
        require_owned_organization(self.request.user, serializer.instance.organization)
        require_owned_organization(self.request.user, serializer.validated_data.get("organization", serializer.instance.organization))
        serializer.save(uploaded_by=serializer.instance.uploaded_by)


class ActivityViewSet(AuditModelViewSet):
    queryset = Activity.objects.select_related("agreement__organization").all()
    serializer_class = ActivitySerializer

    def get_queryset(self):
        qs = super().get_queryset()
        value = self.request.query_params.get("agreement")
        return qs.filter(agreement_id=value) if value else qs

    def perform_create(self, serializer):
        require_owned_organization(self.request.user, serializer.validated_data["agreement"].organization)
        super().perform_create(serializer)

    def perform_update(self, serializer):
        require_owned_organization(self.request.user, serializer.instance.agreement.organization)
        require_owned_organization(self.request.user, serializer.validated_data.get("agreement", serializer.instance.agreement).organization)
        super().perform_update(serializer)


class OrganizationNoteAttachmentDownloadView(APIView):
    permission_classes = [PartnershipPermission]

    def get(self, request, pk):
        try:
            attachment = OrganizationNoteAttachment.objects.select_related("note__organization").get(pk=pk)
        except OrganizationNoteAttachment.DoesNotExist:
            raise Http404
        if not request.user.is_superuser and not owns_related_object(request.user, attachment):
            raise Http404
        if not attachment.file:
            raise Http404
        return FileResponse(attachment.file.storage.open(attachment.file.name, "rb"), as_attachment=True, filename=attachment.original_name)


class PublicOrganizationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Organization.objects.filter(is_public=True)
    permission_classes = [permissions.AllowAny]
    def get_serializer_class(self): return PublicOrganizationDetailSerializer if self.action == "retrieve" else PublicOrganizationSerializer


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        user = request.user
        return Response({"id": user.id, "username": user.username, "first_name": user.first_name, "last_name": user.last_name, "email": user.email, "is_superuser": user.is_superuser})
