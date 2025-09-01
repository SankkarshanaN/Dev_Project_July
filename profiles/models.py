# profiles/models.py
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

def user_profile_path(instance, filename):
    """Generate upload path for profile pictures"""
    ext = filename.split('.')[-1].lower()
    filename = f'user_{instance.user.id}_profile.{ext}'
    return f'profile_pics/user_{instance.user_id}_{uuid.uuid4().hex}.{ext}'

class Member(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='member')
    join_date = models.DateTimeField(default=timezone.now)
    profile_picture = models.ImageField(
        upload_to=user_profile_path, 
        blank=True, 
        null=True,
        # Remove default here - handle in template logic
    )
    problems_solved = models.PositiveIntegerField(default=0)
    total_submissions = models.PositiveIntegerField(default=0)

    FAVORITE_LANGUAGES = [
        ('Python', 'Python'),
        ('C++', 'C++'),
        ('Java', 'Java'),
        ('JavaScript', 'JavaScript'),
        ('C', 'C'),
        ('Go', 'Go'),
        ('Rust', 'Rust'),
        ('Other', 'Other'),
    ]
    favorite_language = models.CharField(max_length=20, choices=FAVORITE_LANGUAGES, blank=True, null=True)

    def __str__(self):
        return self.user.username
    
    @property
    def profile_picture_url(self):
        """Return profile picture URL or default avatar"""
        if self.profile_picture and hasattr(self.profile_picture, 'url'):
            return self.profile_picture.url
        return '/static/images/default_avatar.png'