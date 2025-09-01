from .models import Member

def member_context(request):
    """Add member data to template context globally"""
    if request.user.is_authenticated:
        try:
            member, created = Member.objects.get_or_create(user=request.user)
            return {'current_member': member}
        except:
            return {'current_member': None}
    return {'current_member': None}
