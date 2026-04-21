from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import ProfilePictureForm
from .models import Member
from django.db.models import Count, Sum, Case, When, IntegerField
from django.contrib import messages
from django.contrib.auth.models import User
from submissions.models import Submission, Problem
from django.core.paginator import Paginator

@login_required
def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    member, created = Member.objects.get_or_create(user=profile_user)

    # Handle profile picture update
    if request.method == 'POST' and profile_user == request.user:
        form = ProfilePictureForm(request.POST, request.FILES, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile picture updated successfully!')
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

    # Only update member stats if values have changed (avoid unnecessary DB writes)
    new_total = Submission.objects.filter(user=profile_user).count()
    new_solved = (
        Submission.objects.filter(user=profile_user, result="Accepted")
        .values("problem")
        .distinct()
        .count()
    )
    new_lang = favorite_lang["language"] if favorite_lang else member.favorite_language

    if (
        member.total_submissions != new_total
        or member.problems_solved != new_solved
        or member.favorite_language != new_lang
    ):
        member.total_submissions = new_total
        member.problems_solved = new_solved
        member.favorite_language = new_lang
        member.save()

    # All submissions, paginated
    all_submissions = (
        Submission.objects.filter(user=profile_user)
        .select_related('problem')
        .order_by('-submitted_at')
    )
    paginator = Paginator(all_submissions, 20)
    page_number = request.GET.get('page')
    submissions_page = paginator.get_page(page_number)

    # Calculate points
    accepted_problems = (
        Submission.objects.filter(user=profile_user, result="Accepted")
        .values_list("problem", flat=True)
        .distinct()
    )
    points = (
        Problem.objects.filter(id__in=accepted_problems)
        .aggregate(
            total=Sum(
                Case(
                    When(difficulty="Easy", then=10),
                    When(difficulty="Medium", then=20),
                    When(difficulty="Hard", then=30),
                    default=0,
                    output_field=IntegerField(),
                )
            )
        )["total"] or 0
    )

    context = {
        'profile_user': profile_user,
        'member': member,
        'form': form,
        'favorite_language': favorite_lang["language"] if favorite_lang else None,
        'submissions_page': submissions_page,
        'points': points,
    }
    return render(request, 'profiles/profile.html', context)

def leaderboard(request):
    # Fetch distinct accepted (user, problem, difficulty) pairs in a single query
    # joining problem difficulty avoids a second query for problem points
    distinct_accepted = (
        Submission.objects.filter(result="Accepted")
        .values("user_id", "user__username", "problem_id", "problem__difficulty")
        .distinct()
    )

    POINTS = {"Easy": 10, "Medium": 20, "Hard": 30}

    leaderboard_data = {}
    for entry in distinct_accepted:
        uid = entry["user_id"]
        if uid not in leaderboard_data:
            leaderboard_data[uid] = {
                "username": entry["user__username"],
                "points": 0,
                "problems_solved": 0,
            }
        leaderboard_data[uid]["points"] += POINTS.get(entry["problem__difficulty"], 0)
        leaderboard_data[uid]["problems_solved"] += 1

    leaderboard_list = sorted(
        leaderboard_data.values(),
        key=lambda x: (x["points"], x["problems_solved"]),
        reverse=True,
    )

    # Add rank
    for i, entry in enumerate(leaderboard_list):
        entry["rank"] = i + 1

    # Pagination
    paginator = Paginator(leaderboard_list, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "profiles/leaderboard.html", {
        "leaderboard": page_obj,
        "page_obj": page_obj,
        "total_users": len(leaderboard_list),
    })