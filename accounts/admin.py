from django.contrib import admin
from accounts.models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'area', 'academic_area')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    list_filter = ('role', 'area', 'academic_area')
    filter_horizontal = ('careers',)
