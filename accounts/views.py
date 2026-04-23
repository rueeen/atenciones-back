from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.views import View

from accounts.forms import UserCreateForm, UserProfileForm


class AdminOnlyMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser or getattr(self.request.user.profile, 'role', '') in {'vrs', 'dac'}


class UserCreateView(LoginRequiredMixin, AdminOnlyMixin, View):
    template_name = 'accounts/user_form.html'

    def get(self, request):
        return render(request, self.template_name, {'form': UserCreateForm(), 'profile_form': UserProfileForm()})

    def post(self, request):
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(**form.cleaned_data)
            profile_form = UserProfileForm(request.POST, instance=user.profile)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Usuario creado correctamente.')
                return redirect('accounts:user-create')
            user.delete()
        else:
            profile_form = UserProfileForm(request.POST)
        messages.error(request, 'Revise los datos del formulario.')
        return render(request, self.template_name, {'form': form, 'profile_form': profile_form})
