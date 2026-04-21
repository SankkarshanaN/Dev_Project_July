from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import CustomLoginView, custom_logout, dashboard
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Custom auth routes
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', custom_logout, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),

    # Password reset flow
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='accounts/password_reset.html',
        email_template_name='accounts/password_reset_email.html',
        subject_template_name='accounts/password_reset_subject.txt',
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html',
    ), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html',
    ), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html',
    ), name='password_reset_complete'),

    path('accounts/', include('accounts.urls')),
    path('problems/', include('problems.urls')),
    path('profiles/', include('profiles.urls')),
    path('submissions/', include('submissions.urls')),

    # Base URL redirect
    path('', lambda request: redirect('dashboard') if request.user.is_authenticated else redirect('login')),
]

# Serve media files (uploaded profile pics, etc.)
# In production with a real web server (nginx/caddy), these would be served directly
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
