from django.urls import path
from . import views
from .views import CustomLoginView

urlpatterns = [
   path('login/', CustomLoginView.as_view(), name='login'),   # your custom login
    path('logout/', views.custom_logout, name='logout'),            # custom logout
    path('register/', views.register, name='register'),             # optional
    path('dashboard/', views.dashboard, name='dashboard'),
    
]