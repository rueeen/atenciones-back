from django.contrib import admin
from .models import Case, CaseAttachment, CaseCategory, CaseComment, CaseHistory, CaseSubcategory, CaseTransfer


class CaseAttachmentInline(admin.TabularInline):
    model = CaseAttachment
    extra = 0


class CaseCommentInline(admin.TabularInline):
    model = CaseComment
    extra = 0


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ('folio', 'title', 'student', 'current_area', 'status', 'priority', 'current_assignee', 'created_at')
    list_filter = ('status', 'priority', 'current_area', 'category')
    search_fields = ('folio', 'title', 'student__full_name', 'student__rut')
    inlines = [CaseAttachmentInline, CaseCommentInline]


admin.site.register(CaseCategory)
admin.site.register(CaseSubcategory)
admin.site.register(CaseTransfer)
admin.site.register(CaseHistory)
