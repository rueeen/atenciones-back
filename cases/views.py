from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
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
    CaseTransferForm,
    CategoryForm,
    ReassignCaseForm,
    SubcategoryForm,
)
from cases.models import Case, CaseAttachment, CaseCategory, CaseComment, CaseHistory, CaseSubcategory, CaseTransfer
from organization.models import Area


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
        return visible_cases_for(self.request.user).prefetch_related('history', 'comments', 'attachments', 'transfers')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CaseCommentForm()
        context['attachment_form'] = CaseAttachmentForm()
        context['can_transfer'] = can_transfer_or_reassign(self.request.user)
        context['can_close'] = can_close_case(self.request.user)
        context['available_areas'] = Area.objects.exclude(
            pk=self.object.current_area_id)
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
        case = get_object_or_404(Case, pk=pk)
        if not can_transfer_or_reassign(request.user):
            messages.error(request, 'No tiene permisos para derivar casos.')
            return redirect('cases:detail', pk=pk)
        form = CaseTransferForm(
            request.POST, areas_qs=Area.objects.exclude(pk=case.current_area_id))
        if form.is_valid():
            transfer = form.save(commit=False)
            transfer.case = case
            transfer.from_area = case.current_area
            transfer.transferred_by = request.user
            transfer.save()
            case.current_area = transfer.to_area
            case.status = Case.Status.TRANSFERRED
            case.save(update_fields=['current_area', 'status', 'updated_at'])
            CaseHistory.objects.create(
                case=case,
                event_type=CaseHistory.EventType.TRANSFERRED,
                description=f'Derivado de {transfer.from_area} a {transfer.to_area}. Motivo: {transfer.note}',
                actor=request.user,
            )
            messages.success(request, 'Caso derivado correctamente.')
        else:
            messages.error(
                request, 'Debe indicar área de destino y comentario de derivación.')
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
