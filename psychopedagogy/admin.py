from django.contrib import admin

from psychopedagogy.models import (
    PsychopedagogyAttachment,
    PsychopedagogyLogEntry,
    PsychopedagogyRecord,
    PsychopedagogyRecordAccess,
)


class PsychopedagogyLogEntryInline(admin.TabularInline):
    model = PsychopedagogyLogEntry
    extra = 0


class PsychopedagogyAttachmentInline(admin.TabularInline):
    model = PsychopedagogyAttachment
    extra = 0


class PsychopedagogyRecordAccessInline(admin.TabularInline):
    model = PsychopedagogyRecordAccess
    fk_name = 'record'
    extra = 0


@admin.register(PsychopedagogyRecord)
class PsychopedagogyRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'responsible_tutor', 'status', 'is_confidential', 'start_date', 'end_date')
    list_filter = ('status', 'is_confidential')
    search_fields = ('student__full_name', 'student__rut', 'support_reason')
    inlines = [PsychopedagogyLogEntryInline, PsychopedagogyAttachmentInline, PsychopedagogyRecordAccessInline]


admin.site.register(PsychopedagogyLogEntry)
admin.site.register(PsychopedagogyAttachment)
admin.site.register(PsychopedagogyRecordAccess)
