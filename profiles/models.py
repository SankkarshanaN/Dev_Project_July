from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

def user_profile_path(instance, filename):
    return f'profile_pics/user_{instance.user.id}/{filename}'

class Member(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    join_date = models.DateTimeField(default=timezone.now)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
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
