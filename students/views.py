from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView

from .forms import StudentForm
from .models import Student


class StudentListView(LoginRequiredMixin, ListView):
    model = Student
    template_name = 'students/student_list.html'
    context_object_name = 'students'


class StudentCreateView(LoginRequiredMixin, CreateView):
    model = Student
    form_class = StudentForm
    template_name = 'students/student_form.html'
    success_url = reverse_lazy('students:list')

    def form_valid(self, form):
        messages.success(self.request, 'Estudiante creado correctamente.')
        return super().form_valid(form)


class StudentModalCreateView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        form = StudentForm()
        html = render_to_string(
            'students/includes/student_create_form.html',
            {'form': form},
            request=request
        )
        return JsonResponse({'html': html})

    def post(self, request, *args, **kwargs):
        form = StudentForm(request.POST)

        if form.is_valid():
            student = form.save()
            return JsonResponse({
                'success': True,
                'id': student.id,
                'full_name': student.full_name,
                'rut': student.rut,
                'label': f'{student.rut} - {student.full_name}',
            })

        html = render_to_string(
            'students/includes/student_create_form.html',
            {'form': form},
            request=request
        )
        return JsonResponse({
            'success': False,
            'html': html,
        }, status=400)


class StudentLookupByRutView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        rut = (request.GET.get('rut') or '').strip()
        if not rut:
            return JsonResponse({'success': False, 'message': 'Debe ingresar un RUT.'}, status=400)

        student = Student.objects.filter(rut__iexact=rut).first()
        if not student:
            return JsonResponse({'success': False, 'message': 'No se encontró estudiante con ese RUT.'}, status=404)

        return JsonResponse({
            'success': True,
            'id': student.id,
            'full_name': student.full_name,
            'rut': student.rut,
            'label': f'{student.rut} - {student.full_name}',
        })


class StudentUpdateView(LoginRequiredMixin, UpdateView):
    model = Student
    form_class = StudentForm
    template_name = 'students/student_form.html'
    success_url = reverse_lazy('students:list')

    def form_valid(self, form):
        messages.success(self.request, 'Estudiante actualizado correctamente.')
        return super().form_valid(form)
