from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Problem, Submission

def problem_list(request):
    """Display all problems with optional filtering and pagination"""
    problems = Problem.objects.all().order_by('difficulty', '-created_at')
    
    difficulty = request.GET.get('difficulty')
    if difficulty in ['easy', 'medium', 'hard']:
        problems = problems.filter(difficulty=difficulty)
    
    paginator = Paginator(problems, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'problems': page_obj,
        'current_difficulty': difficulty,
        'total_count': Problem.objects.count(),
        'filtered_count': problems.count(),
        'difficulties': Problem.DIFFICULTY_CHOICES
    }
    return render(request, 'problems/problem_list.html', context)

@login_required
def problem_detail(request, id):
    """Display a single problem and handle code submission"""
    problem = get_object_or_404(Problem, id=id)
    
    if request.method == 'POST':
        code = request.POST.get('code')
        language = request.POST.get('language')
        
        if code and language:
            submission = Submission.objects.create(
                problem=problem,
                user=request.user,
                code=code,
                language=language
            )
            messages.success(request, 'Your solution has been submitted!')
            return redirect('problems:submission_detail', submission.id)
    
    context = {
        'problem': problem,
        'submission_count': problem.submission_set.count(),
        'user_submissions': problem.submission_set.filter(user=request.user) if request.user.is_authenticated else None,
    }
    return render(request, 'problems/problem_detail.html', context)

@login_required
def submission_detail(request, id):
    """Display a single submission result"""
    submission = get_object_or_404(Submission, id=id, user=request.user)
    return render(request, 'problems/submission_detail.html', {'submission': submission})
