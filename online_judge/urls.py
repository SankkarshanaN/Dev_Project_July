"""
URL configuration for online_judge project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import CustomLoginView, custom_logout, dashboard
from django.shortcuts import redirect


urlpatterns = [
    path('admin/', admin.site.urls),

    # Custom auth routes first — so they override defaults
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', custom_logout, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),

    path('accounts/', include('accounts.urls')),
    path('problems/', include('problems.urls')),
    path('profiles/', include('profiles.urls')),
    path('submissions/', include('submissions.urls')),

    path('', lambda request: redirect('login')),  # 👈 Redirect base URL to login

    # ❌ Remove or comment this out to stop Django from using its default /login/ route
    # path('', include('django.contrib.auth.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
