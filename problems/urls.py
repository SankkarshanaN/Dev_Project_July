from django.urls import path
from . import views

urlpatterns = [
    path('', views.problem_list, name='problem_list'),
    path("<int:problem_id>/", views.problem_detail, name="problem_detail"),

    # Staff-only problem authoring UI
    path('manage/', views.admin_problem_list, name='admin_problem_list'),
    path('manage/new/', views.admin_problem_create, name='admin_problem_create'),
    path('manage/<int:problem_id>/edit/', views.admin_problem_update, name='admin_problem_update'),
    path('manage/<int:problem_id>/delete/', views.admin_problem_delete, name='admin_problem_delete'),
]
