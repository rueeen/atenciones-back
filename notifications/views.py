from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView

from notifications.models import Notification
from notifications.services import mark_all_as_read_for_user


class NotificationListView(LoginRequiredMixin, ListView):
    template_name = 'notifications/notification_list.html'
    context_object_name = 'notifications'
    paginate_by = 25

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).select_related(
            'case', 'psychopedagogy_record', 'psychopedagogy_log_entry'
        )


class NotificationMarkReadView(LoginRequiredMixin, View):
    def post(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, user=request.user)
        notification.mark_as_read()
        next_url = request.POST.get('next') or 'notifications:list'
        return redirect(next_url)


class NotificationMarkAllReadView(LoginRequiredMixin, View):
    def post(self, request):
        mark_all_as_read_for_user(request.user)
        next_url = request.POST.get('next') or 'notifications:list'
        return redirect(next_url)
