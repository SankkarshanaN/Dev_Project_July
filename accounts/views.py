from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from .forms import CustomRegisterForm
from django.contrib import messages
from submissions.models import Submission, Problem
from django.contrib.auth.views import LoginView
from django.db.models import Sum, Case, When, IntegerField
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True  # skips login if already logged in
    success_url = reverse_lazy('dashboard')

    def get(self, request, *args, **kwargs):
        # If redirected from logout, show the message
        if request.GET.get("logged_out") == "1":
            messages.success(request, "You have successfully logged out.")
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        list(messages.get_messages(self.request))  # clear previous messages
        messages.success(self.request, f"Welcome back, {self.request.user.username}!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password.")
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('dashboard')


@login_required
def dashboard(request):
    user = request.user
    submissions = Submission.objects.filter(user=user).order_by("-submitted_at")

    accepted_problems = (
        submissions.filter(result="Accepted")
        .values_list("problem", flat=True)
        .distinct()
    )
    problems_solved = accepted_problems.count()

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


def register(request):
    if request.method == "POST":
        form = CustomRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome {user.username}, your account has been created!")
            return redirect("dashboard")  # make sure you have a 'dashboard' url
        else:
            messages.error(request, "There was an error creating your account. Please check the form.")
    else:
        form = CustomRegisterForm()
    return render(request, "accounts/register.html", {"form": form})


def custom_logout(request):
    logout(request)
    return redirect(f"{reverse_lazy('login')}?logged_out=1")
