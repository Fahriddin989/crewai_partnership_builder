from rest_framework import serializers
from .models import Activity, Agreement, AgreementContact, Contact, Document, Organization


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ["id", "name", "organization_type", "country", "website", "description", "is_public", "created_by", "updated_by", "created_at", "updated_at"]
        read_only_fields = ["id", "created_by", "updated_by", "created_at", "updated_at"]

class PublicOrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ["id", "name", "organization_type", "country", "website"]
        read_only_fields = fields

class AgreementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agreement
        fields = ["id", "organization", "title", "agreement_type", "status", "description", "signed_date", "start_date", "expiration_date", "created_by", "updated_by", "created_at", "updated_at"]
        read_only_fields = ["id", "created_by", "updated_by", "created_at", "updated_at"]

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ["id", "full_name", "organization", "position", "email", "phone", "notes", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

class AgreementContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgreementContact
        fields = ["id", "agreement", "contact", "side", "role", "is_primary"]
        read_only_fields = ["id"]

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ["id", "agreement", "title", "document_type", "file", "description", "uploaded_by", "uploaded_at"]
        read_only_fields = ["id", "uploaded_by", "uploaded_at"]

class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ["id", "agreement", "activity_type", "title", "description", "activity_date", "created_by", "updated_by", "created_at", "updated_at"]
        read_only_fields = ["id", "created_by", "updated_by", "created_at", "updated_at"]
