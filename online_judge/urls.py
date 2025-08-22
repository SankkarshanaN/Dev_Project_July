from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import CustomLoginView, custom_logout, dashboard
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),

    # Custom auth routes
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', custom_logout, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),

    path('accounts/', include('accounts.urls')),
    path('problems/', include('problems.urls')),
    path('profiles/', include('profiles.urls')),
    path('submissions/', include('submissions.urls')),

    # Base URL redirect
    path('', lambda request: redirect('dashboard') if request.user.is_authenticated else redirect('login')),
]

# Serve media files only in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
