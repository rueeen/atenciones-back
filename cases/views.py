from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from accounts.services import can_close_case, can_manage_case, can_transfer_or_reassign, visible_cases_for
from cases.forms import (
    CaseAttachmentForm,
    CaseCloseForm,
    CaseCommentForm,
    CaseForm,
    CaseTakeForm,
    CaseTransferForm,
    CategoryForm,
    ReassignCaseForm,
    SubcategoryForm,
)
from cases.models import Case, CaseAttachment, CaseCategory, CaseComment, CaseHistory, CaseSubcategory, CaseTransfer


class CaseListView(LoginRequiredMixin, ListView):
    model = Case
    template_name = 'cases/case_list.html'
    context_object_name = 'cases'
    paginate_by = 20

    def get_queryset(self):
        qs = visible_cases_for(self.request.user).select_related(
            'student', 'current_area', 'category', 'current_assignee')
        search = self.request.GET.get('q')
        if search:
            qs = qs.filter(
                Q(folio__icontains=search) |
                Q(student__full_name__icontains=search) |
                Q(student__rut__icontains=search)
            )
        for field in ['status', 'priority', 'category', 'current_area', 'current_assignee']:
            value = self.request.GET.get(field)
            if value:
                qs = qs.filter(**{field: value})
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        if date_from:
            qs = qs.filter(created_at__date__gte=date_from)
        if date_to:
            qs = qs.filter(created_at__date__lte=date_to)
        return qs


class CaseCreateView(LoginRequiredMixin, CreateView):
    model = Case
    form_class = CaseForm
    template_name = 'cases/case_form.html'
    success_url = reverse_lazy('cases:list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        profile = getattr(self.request.user, 'profile', None)
        if not profile or not profile.area:
            form.add_error(None, 'Tu usuario no tiene área configurada. Contacta al administrador.')
            return self.form_invalid(form)

        form.instance.created_by = self.request.user
        form.instance.origin_area = profile.area
        form.instance.current_area = profile.area
        form.instance.current_assignee = self.request.user

        action = self.request.POST.get('action')

        if action == 'close':
            form.instance.status = Case.Status.CLOSED
            if not form.instance.final_resolution:
                form.instance.final_resolution = 'Caso cerrado al momento de su creación.'
        else:
            form.instance.status = Case.Status.OPEN

        response = super().form_valid(form)

        CaseHistory.objects.create(
            case=self.object,
            event_type=CaseHistory.EventType.CREATED,
            description='Caso creado en el sistema.',
            actor=self.request.user,
        )

        if self.object.status == Case.Status.CLOSED:
            CaseHistory.objects.create(
                case=self.object,
                event_type=CaseHistory.EventType.CLOSED,
                description='Caso cerrado al momento de su creación.',
                actor=self.request.user,
            )
            messages.success(
                self.request, f'Caso {self.object.folio} creado y cerrado correctamente.')
        else:
            messages.success(
                self.request, f'Caso {self.object.folio} creado correctamente.')

        return response


def load_subcategories(request):
    category_id = request.GET.get('category_id')
    subcategories = CaseSubcategory.objects.filter(
        category_id=category_id
    ).order_by('name').values('id', 'name')
    return JsonResponse(list(subcategories), safe=False)


class CaseDetailView(LoginRequiredMixin, DetailView):
    model = Case
    template_name = 'cases/case_detail.html'
    context_object_name = 'case'

    def get_queryset(self):
        return visible_cases_for(self.request.user).select_related(
            'student',
            'category',
            'subcategory',
            'current_area',
            'current_assignee',
        ).prefetch_related(
            'history__actor',
            'comments__author',
            'attachments',
            'transfers__from_area',
            'transfers__to_area',
            'transfers__transferred_by',
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CaseCommentForm()
        context['attachment_form'] = CaseAttachmentForm()
        context['can_transfer'] = self.object.can_be_transferred()
        context['can_take_case'] = self.object.can_be_taken_by(self.request.user)
        context['can_close'] = can_close_case(self.request.user)
        context['transfer_form'] = CaseTransferForm(case=self.object)
        return context


class CaseUpdateView(LoginRequiredMixin, UpdateView):
    model = Case
    form_class = CaseForm
    template_name = 'cases/case_form.html'

    def get_success_url(self):
        return reverse_lazy('cases:detail', kwargs={'pk': self.object.pk})

    def dispatch(self, request, *args, **kwargs):
        if not can_manage_case(request.user):
            messages.error(request, 'No tiene permisos para editar casos.')
            return redirect('cases:list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        previous = self.get_object()
        response = super().form_valid(form)
        if previous.status != self.object.status:
            CaseHistory.objects.create(
                case=self.object,
                event_type=CaseHistory.EventType.STATUS_CHANGED,
                description=f'Estado actualizado a {self.object.get_status_display()}.',
                actor=self.request.user,
            )
        messages.success(self.request, 'Caso actualizado correctamente.')
        return response


class CaseTransferView(LoginRequiredMixin, View):
    def post(self, request, pk):
        case = get_object_or_404(visible_cases_for(request.user), pk=pk)
        if not case.can_be_transferred():
            messages.error(request, 'No se puede derivar un caso cerrado.')
            return redirect('cases:detail', pk=pk)
        form = CaseTransferForm(request.POST, case=case)
        if form.is_valid():
            with transaction.atomic():
                previous_assignee = case.current_assignee
                transfer = form.save(commit=False)
                transfer.case = case
                transfer.from_area = case.current_area
                transfer.transferred_by = request.user
                transfer.save()

                case.current_area = transfer.to_area
                case.current_assignee = None
                case.status = Case.Status.PENDING_AREA
                case.save(update_fields=['current_area', 'current_assignee', 'status', 'updated_at'])

                description = (
                    f'Derivado de {transfer.from_area} a {transfer.to_area}. '
                    f'Motivo: {transfer.note}'
                )
                if previous_assignee:
                    description += f' Responsable anterior: {previous_assignee}.'

                CaseHistory.objects.create(
                    case=case,
                    event_type=CaseHistory.EventType.TRANSFERRED,
                    description=description,
                    actor=request.user,
                )
            messages.success(request, 'Caso derivado correctamente.')
        else:
            errors = ' '.join(form.non_field_errors())
            field_errors = []
            for field, error_list in form.errors.items():
                if field == '__all__':
                    continue
                field_errors.extend([f'{form.fields[field].label}: {error}' for error in error_list])
            details = ' '.join(field_errors)
            messages.error(request, f'No se pudo derivar el caso. {errors} {details}'.strip())
        return redirect('cases:detail', pk=pk)


class PendingAreaCasesListView(LoginRequiredMixin, ListView):
    model = Case
    template_name = 'cases/pending_take_list.html'
    context_object_name = 'cases'
    paginate_by = 20

    def get_queryset(self):
        profile = getattr(self.request.user, 'profile', None)
        if not profile or not profile.area_id:
            return Case.objects.none()
        return visible_cases_for(self.request.user).filter(
            current_area=profile.area,
            current_assignee__isnull=True,
        ).exclude(
            status__in=[Case.Status.CLOSED, Case.Status.RESOLVED, Case.Status.REJECTED]
        ).select_related('student', 'current_area', 'category')


class CaseTakeView(LoginRequiredMixin, View):
    def post(self, request, pk):
        case = get_object_or_404(visible_cases_for(request.user), pk=pk)
        form = CaseTakeForm(request.POST, case=case, user=request.user)
        if not form.is_valid():
            messages.error(request, ' '.join(form.non_field_errors()) or 'No fue posible tomar el caso.')
            return redirect('cases:detail', pk=pk)

        with transaction.atomic():
            case.current_assignee = request.user
            if case.status in {Case.Status.TRANSFERRED, Case.Status.PENDING_AREA, Case.Status.OPEN}:
                case.status = Case.Status.IN_REVIEW
            case.save(update_fields=['current_assignee', 'status', 'updated_at'])
            CaseHistory.objects.create(
                case=case,
                event_type=CaseHistory.EventType.ASSIGNEE_CHANGED,
                description=f'Caso tomado por {request.user}. Responsable actual actualizado.',
                actor=request.user,
            )
        messages.success(request, 'Tomaste el caso correctamente.')
        return redirect('cases:detail', pk=pk)


class CaseReassignView(LoginRequiredMixin, View):
    def post(self, request, pk):
        case = get_object_or_404(Case, pk=pk)
        if not can_transfer_or_reassign(request.user):
            messages.error(request, 'No tiene permisos para reasignar casos.')
            return redirect('cases:detail', pk=pk)
        form = ReassignCaseForm(request.POST, instance=case)
        if form.is_valid():
            old_assignee = case.current_assignee
            case = form.save()
            CaseHistory.objects.create(
                case=case,
                event_type=CaseHistory.EventType.ASSIGNEE_CHANGED,
                description=f'Responsable cambiado de {old_assignee or "Sin asignar"} a {case.current_assignee or "Sin asignar"}.',
                actor=request.user,
            )
            messages.success(request, 'Caso reasignado correctamente.')
        else:
            messages.error(request, 'No fue posible reasignar el caso.')
        return redirect('cases:detail', pk=pk)


class CaseCommentCreateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        case = get_object_or_404(Case, pk=pk)
        form = CaseCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.case = case
            comment.author = request.user
            comment.save()
            CaseHistory.objects.create(
                case=case,
                event_type=CaseHistory.EventType.COMMENT,
                description='Se agregó un comentario interno.' if comment.is_internal else 'Se agregó comentario.',
                actor=request.user,
            )
            messages.success(request, 'Comentario agregado.')
        else:
            messages.error(request, 'Comentario inválido.')
        return redirect('cases:detail', pk=pk)


class CaseAttachmentCreateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        case = get_object_or_404(Case, pk=pk)
        form = CaseAttachmentForm(request.POST, request.FILES)
        if form.is_valid():
            attachment = form.save(commit=False)
            attachment.case = case
            attachment.uploaded_by = request.user
            attachment.save()
            CaseHistory.objects.create(
                case=case,
                event_type=CaseHistory.EventType.ATTACHMENT,
                description=f'Adjunto agregado: {attachment.file.name.split("/")[-1]}',
                actor=request.user,
            )
            messages.success(request, 'Adjunto cargado correctamente.')
        else:
            messages.error(
                request, 'Adjunto inválido. Revise formato o tamaño.')
        return redirect('cases:detail', pk=pk)


class CaseCloseView(LoginRequiredMixin, View):
    def post(self, request, pk):
        case = get_object_or_404(Case, pk=pk)
        if not can_close_case(request.user):
            messages.error(request, 'No tiene permisos para cerrar casos.')
            return redirect('cases:detail', pk=pk)
        form = CaseCloseForm(request.POST, instance=case)
        if form.is_valid():
            case = form.save()
            CaseHistory.objects.create(
                case=case,
                event_type=CaseHistory.EventType.CLOSED,
                description=f'Caso cerrado con estado {case.get_status_display()}.',
                actor=request.user,
            )
            messages.success(request, 'Caso cerrado correctamente.')
        else:
            messages.error(
                request, 'Para cerrar debe registrar estado final y resolución.')
        return redirect('cases:detail', pk=pk)


class CategoryListView(LoginRequiredMixin, ListView):
    model = CaseCategory
    template_name = 'cases/category_list.html'
    context_object_name = 'categories'


class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = CaseCategory
    form_class = CategoryForm
    template_name = 'cases/category_form.html'
    success_url = reverse_lazy('cases:category-list')


class SubcategoryCreateView(LoginRequiredMixin, CreateView):
    model = CaseSubcategory
    form_class = SubcategoryForm
    template_name = 'cases/category_form.html'
    success_url = reverse_lazy('cases:category-list')
