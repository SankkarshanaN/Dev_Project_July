# submissions/urls.py
from django.urls import path
from . import views

app_name = 'submissions'

urlpatterns = [
    # Submissions list - NEW
    path('', views.submission_list, name='submission_list'),
    
    # Submit code for a specific problem
    path('<int:problem_id>/submit/', views.submit_code, name='submit_code'),
    
    # Individual submission detail
    path('<int:submission_id>/', views.submission_detail, name='submission_detail'),
    
    # Custom Input/Output runner
    path('problems/<int:problem_id>/run-custom/', views.run_custom, name='run_custom'),
    
    # AI hint (AJAX endpoint)
    path("ai-hint/<int:problem_id>/", views.ai_hint, name="ai_hint"),
]