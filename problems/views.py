from django.shortcuts import render, get_object_or_404
from problems.models import Problem
from submissions.models import Submission  
from django.contrib.auth.decorators import login_required
from submissions.models import AIHintUsage

from django.utils import timezone
from datetime import timedelta

@login_required
def problem_list(request):
    problems = Problem.objects.all().order_by('difficulty', 'title')
    
    # Search functionality
    search_query = request.GET.get('search', '').strip()
    if search_query:
        problems = problems.filter(title__icontains=search_query)
    
    # Difficulty filter
    difficulty_filter = request.GET.get('difficulty', '').strip()
    if difficulty_filter in ('Easy', 'Medium', 'Hard'):
        problems = problems.filter(difficulty=difficulty_filter)
    
    # Track which problems the user has solved
    solved_problem_ids = set(
        Submission.objects.filter(user=request.user, result='Accepted')
        .values_list('problem_id', flat=True)
        .distinct()
    )
    
    context = {
        'problems': problems,
        'search_query': search_query,
        'difficulty_filter': difficulty_filter,
        'solved_problem_ids': solved_problem_ids,
    }
    return render(request, 'problems/problem_list.html', context)

@login_required
def problem_detail(request, problem_id):
    problem = get_object_or_404(Problem, id=problem_id)
    sample_test_cases = problem.test_cases.filter(is_sample=True)

    previous_submissions = Submission.objects.filter(
        user=request.user, problem=problem
    ).order_by('-submitted_at') if request.user.is_authenticated else []

    remaining_hints, reset_in_hours = 3, 24
    if request.user.is_authenticated:
        usage, _ = AIHintUsage.objects.get_or_create(user=request.user)
        if timezone.now() - usage.last_reset >= timedelta(hours=24):
            usage.used_hints = 0
            usage.last_reset = timezone.now()
            usage.save()
        remaining_hints = max(usage.limit - usage.used_hints, 0)
        reset_in_hours = 24 - int((timezone.now() - usage.last_reset).total_seconds() // 3600)

    # 🟢 new: preserve submitted code
    submitted_code = ""
    if request.method == "POST":
        submitted_code = request.POST.get("code", "")

    return render(request, "problems/problem_detail.html", {
        "problem": problem,
        "sample_test_cases": sample_test_cases,
        "previous_submissions": previous_submissions,
        "remaining_hints": remaining_hints,
        "reset_in_hours": reset_in_hours,
        "submitted_code": submitted_code,  # ✅ pass to template
    })
