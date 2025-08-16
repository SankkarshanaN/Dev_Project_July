# profiles/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Placeholder route to avoid import error
    path("leaderboard/", views.leaderboard, name="leaderboard"),
    path('<str:username>/', views.profile_view, name='profile'),
    
]
