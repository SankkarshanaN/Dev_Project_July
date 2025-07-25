from django.urls import path
from . import views

app_name = 'problems'

urlpatterns = [
    path('', views.problem_list, name='problem_list'),
    path('<int:id>/', views.problem_detail, name='problem_detail'),
    path('submission/<int:id>/', views.submission_detail, name='submission_detail'),
    
]
