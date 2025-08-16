from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import ProfilePictureForm
from .models import Member
from django.db.models import Count, Sum, Case, When, IntegerField
from django.contrib.auth.models import User
from submissions.models import Submission, Problem

@login_required
def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    member = get_object_or_404(Member, user=profile_user)

    # Allow profile picture update only for the logged-in user
    if request.method == 'POST' and profile_user == request.user:
        form = ProfilePictureForm(request.POST, request.FILES, instance=member)
        if form.is_valid():
            form.save()
            return redirect('profile', username=request.user.username)
    else:
        form = ProfilePictureForm(instance=member) if profile_user == request.user else None

    # Calculate success rate safely
    if member.total_submissions > 0:
        success_rate = round((member.problems_solved / member.total_submissions) * 100, 2)
    else:
        success_rate = 0.0

    context = {
        'profile_user': profile_user,
        'member': member,
        'form': form,
        'success_rate': success_rate,
    }
    return render(request, 'profiles/profile.html', context)

def leaderboard(request):
    # Distinct accepted problems
    user_problem_map = (
        Submission.objects.filter(result="Accepted")
        .values("user", "user__username", "problem")  # also pull username
        .distinct()
    )

    # Problem → points mapping
    problem_points = dict(
        Problem.objects.values_list(
            "id",
            Case(
                When(difficulty="Easy", then=10),
                When(difficulty="Medium", then=20),
                When(difficulty="Hard", then=30),
                default=0,
                output_field=IntegerField(),
            ),
        )
    )

    leaderboard_data = {}
    for entry in user_problem_map:
        uid, username, pid = entry["user"], entry["user__username"], entry["problem"]
        points = problem_points.get(pid, 0)

        if uid not in leaderboard_data:
            leaderboard_data[uid] = {
                "username": username,
                "points": 0,
                "problems_solved": 0,
            }

        leaderboard_data[uid]["points"] += points
        leaderboard_data[uid]["problems_solved"] += 1

    leaderboard = [
        {
            "username": data["username"],
            "points": data["points"],
            "problems_solved": data["problems_solved"],
        }
        for uid, data in leaderboard_data.items()
    ]

    # Sort and limit to top 10
    leaderboard = sorted(
        leaderboard,
        key=lambda x: (x["points"], x["problems_solved"]),
        reverse=True,
    )[:10]

    return render(request, "profiles/leaderboard.html", {"leaderboard": leaderboard})
