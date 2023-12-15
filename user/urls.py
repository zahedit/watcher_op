from django.urls import path, re_path
from .views import RegisterView, LoginView, logout_view, activate
from django.contrib.auth.views import LogoutView
from . import views

from django.contrib.auth.views import (
    LogoutView, 
    PasswordResetView, 
    PasswordResetDoneView, 
    PasswordResetConfirmView,
    PasswordResetCompleteView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth-register'),
    path('login/', LoginView.as_view(), name='auth-login'),
    path('logout/', logout_view, name='auth-logout'),
    # path('profile/', ProfileUpdateView.as_view(), name='auth-profile'),
    path('activate/<uidb64>/<token>/', views.activate, name='confirm_registration'),
    path('password/', views.change_password, name='change_password'),


    path('password-reset/', PasswordResetView.as_view(template_name='user/reset-password-main.html'),name='password-reset'),
    path('password-reset/done/', PasswordResetDoneView.as_view(template_name='user/password_reset_done.html'),name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='user/password_reset_confirm.html'),name='password_reset_confirm'),
    path('password-reset-complete/',PasswordResetCompleteView.as_view(template_name='user/password_reset_complete.html'),name='password_reset_complete'),
]