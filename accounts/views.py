from django.shortcuts import render, redirect
from django.contrib.auth import login,logout
from .forms import RegisterForm
from django.contrib import messages
from submissions.models import Submission, Problem
from django.contrib.auth.views import LoginView
from django.db.models import Sum, Case, When, IntegerField
from django.contrib.auth.decorators import login_required


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'

    def form_valid(self, form):
        messages.success(self.request, f"Welcome back, {self.request.user.username}!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password.")
        return super().form_invalid(form)

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def dashboard(request):
    user = request.user
    submissions = Submission.objects.filter(user=user).order_by("-submitted_at")

    # Accepted distinct problems
    accepted_problems = (
        submissions.filter(result="Accepted")
        .values_list("problem", flat=True)
        .distinct()
    )

    problems_solved = accepted_problems.count()

    # Calculate points based on distinct accepted problems
    points = (
        Problem.objects.filter(id__in=accepted_problems)
        .aggregate(
            total_points=Sum(
                Case(
                    When(difficulty="Easy", then=10),
                    When(difficulty="Medium", then=20),
                    When(difficulty="Hard", then=30),
                    default=0,
                    output_field=IntegerField(),
                )
            )
        )["total_points"]
        or 0
    )

    # Recent activity (last submission)
    recent_activity = None
    if submissions.exists():
        last = submissions.first()
        recent_activity = f"Last solved: {last.problem.title} ({last.result})"

    context = {
        "problems_solved": problems_solved,
        "points": points,
        "recent_activity": recent_activity,
    }
    return render(request, "accounts/dashboard.html", context)

def custom_logout(request):
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect('login')
