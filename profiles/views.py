from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import ProfilePictureForm
from .models import Member
from django.contrib.auth.models import User

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
    members = Member.objects.all().order_by('-problems_solved', '-total_submissions')
    return render(request, 'profiles/leaderboard.html', {'members': members})
