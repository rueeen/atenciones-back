from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.db.models import Count, Max
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, ListView

from psychopedagogy.forms import (
    PsychopedagogyAttachmentForm,
    PsychopedagogyLogEntryForm,
    PsychopedagogyRecordForm,
)
from psychopedagogy.models import PsychopedagogyAttachment, PsychopedagogyLogEntry
from psychopedagogy.services import (
    can_access_psychopedagogy_module,
    can_edit_psychopedagogy_record,
    user_can_create_inclusion_log,
    visible_psychopedagogy_records_for,
)


class PsychopedagogyModuleAccessMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not can_access_psychopedagogy_module(request.user):
            messages.error(
                request, 'No tiene permisos para acceder al módulo psicopedagógico.')
            return redirect('dashboard:home')
        return super().dispatch(request, *args, **kwargs)




class InclusionLogCreatePermissionMixin:
    def dispatch(self, request, *args, **kwargs):
        if not user_can_create_inclusion_log(request.user):
            raise PermissionDenied('Solo las tutoras pueden crear bitácoras de inclusión.')
        return super().dispatch(request, *args, **kwargs)


class PsychopedagogyRecordListView(PsychopedagogyModuleAccessMixin, ListView):
    template_name = 'psychopedagogy/record_list.html'
    context_object_name = 'records'

    def get_queryset(self):
        return visible_psychopedagogy_records_for(self.request.user).select_related(
            'student', 'responsible_tutor', 'created_by'
        ).annotate(
            log_entries_count=Count('log_entries', distinct=True),
            last_log_date=Max('log_entries__entry_date'),
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_create_inclusion_log'] = user_can_create_inclusion_log(self.request.user)
        return context


class PsychopedagogyRecordDetailView(PsychopedagogyModuleAccessMixin, DetailView):
    template_name = 'psychopedagogy/record_detail.html'
    context_object_name = 'record'

    def get_queryset(self):
        return visible_psychopedagogy_records_for(self.request.user).select_related(
            'student', 'responsible_tutor', 'created_by'
        ).prefetch_related('log_entries__author', 'attachments__uploaded_by', 'authorized_users__user')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['log_form'] = PsychopedagogyLogEntryForm()
        context['attachment_form'] = PsychopedagogyAttachmentForm()
        context['can_edit_record'] = can_edit_psychopedagogy_record(self.request.user, self.object)
        context['can_create_inclusion_log'] = user_can_create_inclusion_log(self.request.user)
        return context


class PsychopedagogyRecordCreateView(InclusionLogCreatePermissionMixin, PsychopedagogyModuleAccessMixin, CreateView):
    form_class = PsychopedagogyRecordForm
    template_name = 'psychopedagogy/record_form.html'
    success_url = reverse_lazy('psychopedagogy:list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        try:
            response = super().form_valid(form)
        except IntegrityError:
            form.add_error(
                'student',
                'Ya existe una ficha psicopedagógica activa para este estudiante.',
            )
            return self.form_invalid(form)
        messages.success(
            self.request, 'Ficha psicopedagógica creada correctamente.')
        return response


class PsychopedagogyLogEntryCreateView(InclusionLogCreatePermissionMixin, PsychopedagogyModuleAccessMixin, View):
    def post(self, request, pk):
        record = get_object_or_404(
            visible_psychopedagogy_records_for(request.user), pk=pk)
        if not can_edit_psychopedagogy_record(request.user, record):
            messages.error(
                request, 'No tiene permisos para agregar bitácora en esta ficha.')
            return redirect('psychopedagogy:detail', pk=pk)

        form = PsychopedagogyLogEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.record = record
            entry.author = request.user
            entry.save()
            messages.success(
                request, 'Entrada de bitácora agregada correctamente.')
        else:
            messages.error(
                request, 'No se pudo agregar la bitácora. Revise los datos ingresados.')
        return redirect('psychopedagogy:detail', pk=pk)


class PsychopedagogyAttachmentCreateView(PsychopedagogyModuleAccessMixin, View):
    def post(self, request, pk):
        record = get_object_or_404(
            visible_psychopedagogy_records_for(request.user), pk=pk)
        if not can_edit_psychopedagogy_record(request.user, record):
            messages.error(
                request, 'No tiene permisos para adjuntar archivos en esta ficha.')
            return redirect('psychopedagogy:detail', pk=pk)

        form = PsychopedagogyAttachmentForm(request.POST, request.FILES)
        if form.is_valid():
            attachment = form.save(commit=False)
            attachment.record = record
            attachment.uploaded_by = request.user
            attachment.save()
            messages.success(
                self.request, 'Archivo adjunto cargado correctamente.')
        else:
            messages.error(
                self.request, 'No se pudo cargar el adjunto. Revise formato y tamaño de archivo.')
        return redirect('psychopedagogy:detail', pk=pk)
