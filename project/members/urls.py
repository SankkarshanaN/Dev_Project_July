from django.urls import path
from . import views

app_name = 'members'

urlpatterns = [
    path('', views.show_members, name='show_members'),
    path('detail/<int:id>/', views.member_detail, name='member_detail'),
    path('dashboard/', views.dashboard_view, name='dashboard'),  # ✅ Add this
]
