from rest_framework import serializers
from .models import Activity, Agreement, AgreementContact, Contact, Document, Organization, OrganizationMedia

AUDIT_READ_ONLY_FIELDS = ["id", "created_by", "updated_by", "created_at", "updated_at"]
TIMESTAMP_READ_ONLY_FIELDS = ["id", "created_at", "updated_at"]

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ["id", "name", "organization_type", "country", "website", "description", "is_public", "created_by", "updated_by", "created_at", "updated_at"]
        read_only_fields = AUDIT_READ_ONLY_FIELDS

class PublicOrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ["id", "name", "organization_type", "country", "website"]
        read_only_fields = fields

class PublicOrganizationDetailSerializer(PublicOrganizationSerializer):
    media = serializers.SerializerMethodField()
    class Meta(PublicOrganizationSerializer.Meta):
        fields = PublicOrganizationSerializer.Meta.fields + ["media"]
    def get_media(self, obj): return PublicOrganizationMediaSerializer(obj.media.filter(is_public=True), many=True, context=self.context).data

class PublicOrganizationMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationMedia
        fields = ["id", "title", "image", "description", "uploaded_at"]
        read_only_fields = fields

class AgreementSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source="organization.name", read_only=True)
    class Meta:
        model = Agreement
        fields = ["id", "organization", "organization_name", "title", "agreement_type", "status", "description", "signed_date", "start_date", "expiration_date", "created_by", "updated_by", "created_at", "updated_at"]
        read_only_fields = AUDIT_READ_ONLY_FIELDS + ["organization_name"]
    def validate(self, attrs):
        start_date = attrs.get("start_date", getattr(self.instance, "start_date", None)); expiration_date = attrs.get("expiration_date", getattr(self.instance, "expiration_date", None))
        if start_date and expiration_date and expiration_date < start_date: raise serializers.ValidationError({"expiration_date": "Expiration date cannot be earlier than start date."})
        return attrs

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ["id", "full_name", "organization", "position", "email", "phone", "notes", "created_at", "updated_at"]
        read_only_fields = TIMESTAMP_READ_ONLY_FIELDS

class AgreementContactSerializer(serializers.ModelSerializer):
    contact_name = serializers.CharField(source="contact.full_name", read_only=True); contact_position = serializers.CharField(source="contact.position", read_only=True); contact_email = serializers.EmailField(source="contact.email", read_only=True); contact_phone = serializers.CharField(source="contact.phone", read_only=True)
    class Meta:
        model = AgreementContact
        fields = ["id", "agreement", "contact", "contact_name", "contact_position", "contact_email", "contact_phone", "side", "role", "is_primary"]
        read_only_fields = ["id", "contact_name", "contact_position", "contact_email", "contact_phone"]

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ["id", "agreement", "title", "document_type", "file", "description", "uploaded_by", "uploaded_at"]
        read_only_fields = ["id", "uploaded_by", "uploaded_at"]

class OrganizationMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationMedia
        fields = ["id", "organization", "title", "image", "description", "is_public", "uploaded_by", "uploaded_at"]
        read_only_fields = ["id", "uploaded_by", "uploaded_at"]

class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ["id", "agreement", "activity_type", "title", "description", "activity_date", "created_by", "updated_by", "created_at", "updated_at"]
        read_only_fields = AUDIT_READ_ONLY_FIELDS
