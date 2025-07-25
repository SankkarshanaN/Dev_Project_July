from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Problem(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard')
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    points = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)])
    time_limit = models.IntegerField(help_text="Time limit in seconds", default=1)
    memory_limit = models.IntegerField(help_text="Memory limit in MB", default=256)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    input_format = models.TextField(blank=True, help_text="Describe the input format")
    output_format = models.TextField(blank=True, help_text="Describe the output format")
    constraints = models.TextField(blank=True, help_text="List the constraints")
    sample_input = models.TextField(help_text="Example input for this problem")
    sample_output = models.TextField(help_text="Expected output for the above input")

    class Meta:
        ordering = ['difficulty', 'points']

    def __str__(self):
        return f"{self.title} ({self.get_difficulty_display()})"

class Submission(models.Model):
    LANGUAGE_CHOICES = [
        ('python', 'Python'),
        ('java', 'Java'),
        ('cpp', 'C++'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('accepted', 'Accepted'),
        ('wrong', 'Wrong Answer'),
        ('error', 'Runtime Error'),
        ('timeout', 'Time Limit Exceeded'),
    ]

    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.TextField()
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    execution_time = models.FloatField(null=True, blank=True)
    memory_used = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}'s submission for {self.problem.title}"
