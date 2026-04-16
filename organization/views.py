from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from organization.models import AcademicArea, Area, Career


class AreaListView(LoginRequiredMixin, ListView):
    model = Area
    template_name = 'organization/area_list.html'
    context_object_name = 'areas'


class CareerListView(LoginRequiredMixin, ListView):
    model = Career
    template_name = 'organization/career_list.html'
    context_object_name = 'careers'

    def get_queryset(self):
        return Career.objects.select_related('academic_area', 'academic_area__parent_area')
