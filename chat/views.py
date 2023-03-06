from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView
from django.contrib.auth import logout, login
from .forms import UserRegisterForm, UserLoginForm
from django.contrib.auth.decorators import login_required
from . import models, utils


def main(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse_lazy('chat:chat'))
    else:
        return HttpResponseRedirect(reverse_lazy('chat:login'))


class RegisterView(CreateView):
    """ Представление для регистрации """
    template_name = 'registration/register.html'
    form_class = UserRegisterForm
    success_url = reverse_lazy('chat:main_page')
    
    def form_valid(self, form):
        """ Сохранение зарегистрированного пользователя """
        user = form.save()
        login(self.request, user)

        return redirect('chat:chat')


class LoginUser(LoginView):
    """ Представление для входа """
    form_class = UserLoginForm


def logout_user(request):
    """Представление для выхода"""
    logout(request)
    return redirect('chat:login')


@login_required
def change_avatar(request):
    """ Представление для смены аватара, используется в AJAX"""
    if request.method == 'POST' and utils.is_ajax(request=request):
        avatar_file = request.FILES['file']
        
        profile = request.user.profile 
        profile.avatar.save(avatar_file.name, avatar_file)
        profile.save()

        return JsonResponse({'url': profile.avatar.url})
    

@login_required
def change_status(request):
    """ Представление для смены статуса, используется в AJAX"""
    if request.method == 'POST' and utils.is_ajax(request=request):
        new_status = request.POST.get('new-status', '')
        
        profile = request.user.profile
        profile.status = new_status
        profile.save()

        return JsonResponse({})


@login_required
def chat_view(request):
    user_profile = models.Profile.objects.get(user=request.user)
    return render(request, 'chat/chat.html', context={'profile': user_profile})
