from django.db import models

class Member(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    join_date_timestamp = models.DateTimeField(auto_now_add=True)

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50, unique=True)
    bio = models.TextField(max_length=500, blank=True)
    
    # Programming related fields
    favorite_language = models.CharField(
        max_length=20,
        choices=[
            ('python', 'Python'),
            ('java', 'Java'),
            ('cpp', 'C++'),
            ('javascript', 'JavaScript'),
        ],
        default='python'
    )
    
    # Stats
    problems_solved = models.IntegerField(default=0)
    total_submissions = models.IntegerField(default=0)
    
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def success_rate(self):
        """Return success rate as a percentage"""
        if self.total_submissions == 0:
            return 0
        return (self.problems_solved / self.total_submissions) * 100
