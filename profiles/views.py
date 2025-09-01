from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import ProfilePictureForm
from .models import Member
from django.db.models import Count, Sum, Case, When, IntegerField
from django.contrib import messages
from django.contrib.auth.models import User
from submissions.models import Submission, Problem
from django.db.models import Count

@login_required
def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)

    # Get or create member profile (important for new users)
    member, created = Member.objects.get_or_create(user=profile_user)

    # Handle profile picture update
    if request.method == 'POST' and profile_user == request.user:
        form = ProfilePictureForm(request.POST, request.FILES, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile picture updated successfully! 🎉')
            return redirect('profile', username=request.user.username)
        else:
            messages.error(request, 'Error updating profile picture. Please try again.')
    else:
        form = ProfilePictureForm(instance=member) if profile_user == request.user else None

    # Get favorite language from submissions
    favorite_lang = (
        Submission.objects.filter(user=profile_user)
        .values("language")
        .annotate(total=Count("id"))
        .order_by("-total")
        .first()
    )

    # Update member stats
    if created or member.total_submissions == 0:
        member.total_submissions = Submission.objects.filter(user=profile_user).count()
        member.problems_solved = (
            Submission.objects.filter(user=profile_user, result="Accepted")
            .values("problem")
            .distinct()
            .count()
        )
        member.save()

    context = {
        'profile_user': profile_user,
        'member': member,
        'form': form,
        'favorite_language': favorite_lang["language"] if favorite_lang else None,
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