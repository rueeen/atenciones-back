from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Count, DurationField, ExpressionWrapper, F, Q
from django.views.generic import TemplateView

from accounts.services import visible_cases_for
from cases.models import Case


class DashboardHomeView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = visible_cases_for(self.request.user)
        closed_states = [Case.Status.CLOSED, Case.Status.RESOLVED, Case.Status.REJECTED]

        context['open_total'] = qs.exclude(status__in=closed_states).count()
        context['closed_total'] = qs.filter(status__in=closed_states).count()
        context['by_area'] = qs.values('current_area__name').annotate(total=Count('id')).order_by('-total')[:10]
        context['by_status'] = qs.values('status').annotate(total=Count('id')).order_by('-total')
        context['by_priority'] = qs.values('priority').annotate(total=Count('id')).order_by('-total')
        context['recent_cases'] = qs.select_related('student')[:8]
        context['overdue_cases'] = qs.filter(due_date__isnull=False, due_date__lt=F('updated_at__date')).count()
        avg_delta = qs.filter(closed_at__isnull=False).annotate(
            resolution=ExpressionWrapper(F('closed_at') - F('created_at'), output_field=DurationField())
        ).aggregate(avg=Avg('resolution'))['avg']
        context['avg_resolution'] = avg_delta
        return context
