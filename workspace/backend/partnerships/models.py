from django.conf import settings
from django.db import models


def user_foreign_key(related_name: str):
    """Standard nullable reference to a Django user."""
    return models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name=related_name)


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True


class AcademicUnit(TimeStampedModel):
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-is_active", "name"]
        verbose_name = "Direction"
        verbose_name_plural = "Directions"

    def __str__(self): return self.name


class Organization(TimeStampedModel):
    class OrganizationType(models.TextChoices):
        UNIVERSITY = "UNIVERSITY", "University"
        COMPANY = "COMPANY", "Company"
        GOVERNMENT = "GOVERNMENT", "Government"
        NGO = "NGO", "NGO"
        OTHER = "OTHER", "Other"
    name = models.CharField(max_length=255)
    organization_type = models.CharField(max_length=20, choices=OrganizationType.choices)
    country = models.CharField(max_length=100)
    website = models.URLField(blank=True)
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=True)
    created_by = user_foreign_key("created_organizations")
    updated_by = user_foreign_key("updated_organizations")
    academic_units = models.ManyToManyField(AcademicUnit, through="OrganizationAcademicUnit", related_name="organizations")
    def __str__(self): return self.name


class OrganizationAcademicUnit(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    academic_unit = models.ForeignKey(AcademicUnit, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["organization", "academic_unit"], name="unique_organization_academic_unit")]

    def __str__(self): return f"{self.organization} — {self.academic_unit}"


class OrganizationNote(TimeStampedModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="notes")
    body = models.TextField()
    next_step = models.TextField(blank=True)
    follow_up_date = models.DateField(null=True, blank=True)
    created_by = user_foreign_key("created_organization_notes")
    updated_by = user_foreign_key("updated_organization_notes")

    class Meta:
        ordering = ["-created_at", "-pk"]

    def __str__(self): return f"Note for {self.organization}"


def organization_note_attachment_upload_path(instance, filename):
    return f"organization_notes/{instance.note.organization_id}/{instance.note_id}/{filename}"


class OrganizationNoteAttachment(models.Model):
    note = models.ForeignKey(OrganizationNote, on_delete=models.CASCADE, related_name="attachments")
    file = models.FileField(upload_to=organization_note_attachment_upload_path)
    original_name = models.CharField(max_length=255)
    uploaded_by = user_foreign_key("uploaded_organization_note_attachments")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self): return self.original_name

    def delete(self, *args, **kwargs):
        storage, name = self.file.storage, self.file.name
        result = super().delete(*args, **kwargs)
        if name:
            storage.delete(name)
        return result


class Agreement(TimeStampedModel):
    class AgreementType(models.TextChoices):
        MOU = "MOU", "Memorandum of Understanding"
        MOA = "MOA", "Memorandum of Agreement"
        ACADEMY = "ACADEMY", "Academy"
        PARTNERSHIP = "PARTNERSHIP", "Partnership"
        EXCHANGE = "EXCHANGE", "Exchange"
        NDA = "NDA", "Non-Disclosure Agreement"
        OTHER = "OTHER", "Other"
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        ACTIVE = "ACTIVE", "Active"
        INACTIVE = "INACTIVE", "Inactive"
        EXPIRED = "EXPIRED", "Expired"
        UNDER_RENEWAL = "UNDER_RENEWAL", "Under renewal"
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="agreements")
    title = models.CharField(max_length=255)
    agreement_type = models.CharField(max_length=20, choices=AgreementType.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    description = models.TextField(blank=True)
    signed_date = models.DateField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    expiration_date = models.DateField(null=True, blank=True)
    created_by = user_foreign_key("created_agreements")
    updated_by = user_foreign_key("updated_agreements")
    def __str__(self): return f"{self.title} ({self.organization})"


class Contact(TimeStampedModel):
    full_name = models.CharField(max_length=255)
    organization = models.ForeignKey(Organization, null=True, blank=True, on_delete=models.SET_NULL, related_name="contacts")
    position = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    def __str__(self): return self.full_name


class AgreementContact(models.Model):
    class Side(models.TextChoices):
        OUR_SIDE = "OUR_SIDE", "Our side"
        PARTNER_SIDE = "PARTNER_SIDE", "Partner side"
    agreement = models.ForeignKey(Agreement, on_delete=models.CASCADE, related_name="agreement_contacts")
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name="agreement_contacts")
    side = models.CharField(max_length=20, choices=Side.choices)
    role = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["agreement", "contact", "side"], name="unique_agreement_contact_side")]
    def __str__(self): return f"{self.contact} — {self.agreement} ({self.get_side_display()})"


def document_upload_path(instance, filename): return f"documents/agreement_{instance.agreement_id}/{filename}"


class Document(models.Model):
    agreement = models.ForeignKey(Agreement, on_delete=models.CASCADE, related_name="documents")
    title = models.CharField(max_length=255)
    document_type = models.CharField(max_length=100, blank=True)
    file = models.FileField(upload_to=document_upload_path)
    description = models.TextField(blank=True)
    uploaded_by = user_foreign_key("uploaded_documents")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.title


def media_upload_path(instance, filename): return f"organizations/{instance.organization_id}/media/{filename}"


class OrganizationMedia(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="media")
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to=media_upload_path)
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=False)
    uploaded_by = user_foreign_key("uploaded_organization_media")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.title


class Activity(TimeStampedModel):
    class ActivityType(models.TextChoices):
        NOTE = "NOTE", "Note"
        MEETING = "MEETING", "Meeting"
        EMAIL = "EMAIL", "Email"
        CALL = "CALL", "Call"
        STATUS_CHANGE = "STATUS_CHANGE", "Status change"
        OTHER = "OTHER", "Other"
    agreement = models.ForeignKey(Agreement, on_delete=models.CASCADE, related_name="activities")
    activity_type = models.CharField(max_length=20, choices=ActivityType.choices)
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    activity_date = models.DateTimeField()
    created_by = user_foreign_key("created_activities")
    updated_by = user_foreign_key("updated_activities")
    def __str__(self): return f"{self.get_activity_type_display()}: {self.agreement}"
