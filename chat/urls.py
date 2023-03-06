from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.main, name='main_page'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('chat/', views.chat_view, name='chat'),
    path('chat/change_avatar/', views.change_avatar, name='change_avatar'),
    path('chat/change_status/', views.change_status, name='change_status'),
]
