from django.contrib import admin
from .models import Activity, Agreement, AgreementContact, Contact, Document, Organization

class AgreementInline(admin.TabularInline):
    model = Agreement; extra = 0; fields = ("title", "agreement_type", "status", "signed_date", "start_date", "expiration_date"); show_change_link = True
class AgreementContactInline(admin.TabularInline):
    model = AgreementContact; extra = 0; fields = ("contact", "side", "role", "is_primary"); autocomplete_fields = ("contact",)
class DocumentInline(admin.TabularInline):
    model = Document; extra = 0; fields = ("title", "document_type", "file", "uploaded_by"); autocomplete_fields = ("uploaded_by",); show_change_link = True
class ActivityInline(admin.TabularInline):
    model = Activity; extra = 0; fields = ("activity_type", "title", "description", "activity_date", "created_by", "updated_by"); autocomplete_fields = ("created_by", "updated_by"); show_change_link = True

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "organization_type", "country", "website", "is_public", "updated_at"); list_filter = ("organization_type", "country", "is_public"); search_fields = ("name", "country", "website", "description"); readonly_fields = ("created_at", "updated_at"); autocomplete_fields = ("created_by", "updated_by"); inlines = (AgreementInline,)
@admin.register(Agreement)
class AgreementAdmin(admin.ModelAdmin):
    list_display = ("title", "organization", "agreement_type", "status", "start_date", "expiration_date", "updated_at"); list_filter = ("agreement_type", "status", "organization__country"); search_fields = ("title", "organization__name", "description"); list_select_related = ("organization",); readonly_fields = ("created_at", "updated_at"); autocomplete_fields = ("organization", "created_by", "updated_by"); date_hierarchy = "expiration_date"; inlines = (AgreementContactInline, DocumentInline, ActivityInline)
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("full_name", "organization", "position", "email", "phone", "updated_at"); list_filter = ("organization",); search_fields = ("full_name", "organization__name", "position", "email", "phone", "notes"); list_select_related = ("organization",); autocomplete_fields = ("organization",); readonly_fields = ("created_at", "updated_at")
@admin.register(AgreementContact)
class AgreementContactAdmin(admin.ModelAdmin):
    list_display = ("agreement", "contact", "side", "role", "is_primary"); list_filter = ("side", "is_primary", "agreement__status"); search_fields = ("agreement__title", "agreement__organization__name", "contact__full_name", "contact__email", "role"); list_select_related = ("agreement", "contact"); autocomplete_fields = ("agreement", "contact")
@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "agreement", "document_type", "uploaded_by", "uploaded_at"); list_filter = ("document_type", "uploaded_at", "agreement__status"); search_fields = ("title", "document_type", "agreement__title", "agreement__organization__name", "description"); list_select_related = ("agreement", "uploaded_by"); autocomplete_fields = ("agreement", "uploaded_by"); readonly_fields = ("uploaded_at",); date_hierarchy = "uploaded_at"
@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ("agreement", "title", "activity_type", "activity_date", "created_by", "updated_by", "created_at"); list_filter = ("activity_type", "activity_date", "agreement__status"); search_fields = ("agreement__title", "title", "agreement__organization__name", "description"); list_select_related = ("agreement", "created_by", "updated_by"); autocomplete_fields = ("agreement", "created_by", "updated_by"); readonly_fields = ("created_at", "updated_at"); date_hierarchy = "activity_date"; ordering = ("-activity_date", "-created_at")
