from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Member

def show_members(request):
    """Public page: Show all members"""
    all_members = Member.objects.all()
    return render(request, 'members/members.html', {'all_members': all_members})

@login_required
def member_detail(request, id):
    """Private page: Member detail only if logged in"""
    member = get_object_or_404(Member, id=id)
    return render(request, 'members/member_detail.html', {'member': member})

@login_required
def dashboard_view(request):
    return render(request, 'dashboard.html')
