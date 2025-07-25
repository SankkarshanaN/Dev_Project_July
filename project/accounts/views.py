from django.contrib import messages
from .forms import CustomUserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Registration successful.")
            login(request, user)  # optional: auto-login after registration
            return redirect('dashboard')  # or any route you prefer
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Logged in successfully!")
            return redirect('dashboard')  # or homepage
        else:
            messages.error(request, "Invalid credentials")
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    messages.info(request, "Logged out.")
    return redirect('accounts:login')

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

def dashboard_view(request):
    return render(request, 'registration/dashboard.html', {'user': request.user}) # or 'accounts/dashboard.html' if you prefer
