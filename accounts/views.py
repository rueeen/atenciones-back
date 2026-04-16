from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.views import View

from accounts.forms import UserCreateForm, UserProfileForm


class AdminOnlyMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser or getattr(self.request.user.profile, 'role', '') == 'admin'


class UserCreateView(LoginRequiredMixin, AdminOnlyMixin, View):
    template_name = 'accounts/user_form.html'

    def get(self, request):
        return render(request, self.template_name, {'form': UserCreateForm(), 'profile_form': UserProfileForm()})

    def post(self, request):
        form = UserCreateForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        if form.is_valid() and profile_form.is_valid():
            user = User.objects.create_user(**form.cleaned_data)
            profile = user.profile
            for field, value in profile_form.cleaned_data.items():
                setattr(profile, field, value)
            profile.save()
            messages.success(request, 'Usuario creado correctamente.')
            return redirect('accounts:user-create')
        messages.error(request, 'Revise los datos del formulario.')
        return render(request, self.template_name, {'form': form, 'profile_form': profile_form})
