from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.urls import reverse
from problems.models import Problem, Tag
from problems.forms import ProblemForm, TestCaseFormSet
from submissions.models import Submission
from django.contrib.auth.decorators import login_required
from submissions.models import AIHintUsage
from django.db.models import Count, Q

from django.utils import timezone
from datetime import timedelta


def _get_recommendations(user, limit=5):
    """Suggest problems based on tags from the user's solved problems.

    Strategy: rank unsolved problems by how many tags they share with
    problems the user has already solved. Prefer similar or slightly
    harder difficulty tiers to keep the user progressing.
    """
    solved_problem_ids = set(
        Submission.objects.filter(user=user, result='Accepted')
        .values_list('problem_id', flat=True).distinct()
    )

    if not solved_problem_ids:
        # Cold start: surface easy problems with the most tag coverage
        return (
            Problem.objects.filter(difficulty='Easy')
            .annotate(tag_count=Count('tags'))
            .order_by('-tag_count', 'title')[:limit]
        )

    solved_tag_ids = list(
        Tag.objects.filter(problems__id__in=solved_problem_ids)
        .values_list('id', flat=True).distinct()
    )

    if not solved_tag_ids:
        return Problem.objects.exclude(id__in=solved_problem_ids).order_by('difficulty', 'title')[:limit]

    # Count shared tags per unsolved problem
    return (
        Problem.objects.exclude(id__in=solved_problem_ids)
        .filter(tags__id__in=solved_tag_ids)
        .annotate(shared_tags=Count('tags', filter=Q(tags__id__in=solved_tag_ids)))
        .order_by('-shared_tags', 'difficulty', 'title')[:limit]
    )


@login_required
def problem_list(request):
    problems = Problem.objects.all().prefetch_related('tags').order_by('difficulty', 'title')

    # Search functionality
    search_query = request.GET.get('search', '').strip()
    if search_query:
        problems = problems.filter(title__icontains=search_query)

    # Difficulty filter
    difficulty_filter = request.GET.get('difficulty', '').strip()
    if difficulty_filter in ('Easy', 'Medium', 'Hard'):
        problems = problems.filter(difficulty=difficulty_filter)

    # Tag filter (by slug)
    tag_filter = request.GET.get('tag', '').strip()
    if tag_filter:
        problems = problems.filter(tags__slug=tag_filter).distinct()

    # Track which problems the user has solved
    solved_problem_ids = set(
        Submission.objects.filter(user=request.user, result='Accepted')
        .values_list('problem_id', flat=True)
        .distinct()
    )

    # Tag sidebar (with counts)
    all_tags = Tag.objects.annotate(num=Count('problems')).filter(num__gt=0).order_by('-num', 'name')

    # Recommendations (only when no filters applied, so list page still feels clean)
    recommendations = None
    if not (search_query or difficulty_filter or tag_filter):
        recommendations = _get_recommendations(request.user)

    context = {
        'problems': problems,
        'search_query': search_query,
        'difficulty_filter': difficulty_filter,
        'tag_filter': tag_filter,
        'all_tags': all_tags,
        'solved_problem_ids': solved_problem_ids,
        'recommendations': recommendations,
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
        "submitted_code": submitted_code,
    })


# ===== Staff-only problem authoring UI =====

@staff_member_required
def admin_problem_list(request):
    problems = (
        Problem.objects.all()
        .prefetch_related('tags', 'test_cases')
        .annotate(tc_count=Count('test_cases'))
        .order_by('-created_at')
    )
    return render(request, 'problems/admin/problem_list.html', {'problems': problems})


@staff_member_required
def admin_problem_create(request):
    if request.method == 'POST':
        form = ProblemForm(request.POST)
        formset = TestCaseFormSet(request.POST, instance=Problem())
        if form.is_valid() and formset.is_valid():
            problem = form.save()
            formset.instance = problem
            formset.save()
            messages.success(request, f'Problem "{problem.title}" created.')
            return redirect('admin_problem_list')
        messages.error(request, 'Please fix the errors below.')
    else:
        form = ProblemForm()
        formset = TestCaseFormSet(instance=Problem())
    return render(request, 'problems/admin/problem_form.html', {
        'form': form, 'formset': formset, 'mode': 'create',
    })


@staff_member_required
def admin_problem_update(request, problem_id):
    problem = get_object_or_404(Problem, id=problem_id)
    if request.method == 'POST':
        form = ProblemForm(request.POST, instance=problem)
        formset = TestCaseFormSet(request.POST, instance=problem)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, f'Problem "{problem.title}" updated.')
            return redirect('admin_problem_list')
        messages.error(request, 'Please fix the errors below.')
    else:
        form = ProblemForm(instance=problem)
        formset = TestCaseFormSet(instance=problem)
    return render(request, 'problems/admin/problem_form.html', {
        'form': form, 'formset': formset, 'mode': 'edit', 'problem': problem,
    })


@staff_member_required
def admin_problem_delete(request, problem_id):
    problem = get_object_or_404(Problem, id=problem_id)
    if request.method == 'POST':
        title = problem.title
        problem.delete()
        messages.success(request, f'Problem "{title}" deleted.')
        return redirect('admin_problem_list')
    return render(request, 'problems/admin/problem_confirm_delete.html', {'problem': problem})
