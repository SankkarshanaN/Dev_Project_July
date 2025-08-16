from django.shortcuts import render, get_object_or_404
from .models import Problem
from django.contrib.auth.decorators import login_required

@login_required
def problem_list(request):
    problems = Problem.objects.all()
    return render(request, 'problems/problem_list.html', {'problems': problems})

@login_required
def problem_detail(request, pk):
    problem = get_object_or_404(Problem, pk=pk)
    sample_test_cases = problem.test_cases.filter(is_sample=True)  # only samples
    return render(request, "problems/problem_detail.html", {
        "problem": problem,
        "sample_test_cases": sample_test_cases,
    })