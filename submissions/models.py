from django.db import models
from django.contrib.auth.models import User
from problems.models import Problem
from django.utils import timezone
from datetime import timedelta

LANGUAGE_CHOICES = [
    ('python', 'Python'),
    ('cpp', 'C++'),
    ('java', 'Java'),
]

class Submission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    code = models.TextField()
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES)
    submitted_at = models.DateTimeField(auto_now_add=True)
    result = models.CharField(max_length=20, default='Pending')
    output = models.TextField(blank=True, null=True)
    error = models.TextField(blank=True, null=True)
    is_correct = models.BooleanField(default=False)  # ✅ track correctness

    def __str__(self):
        return f"{self.user.username} - {self.problem.title} - {self.language}"
    
class SubmissionResult(models.Model):
    submission = models.ForeignKey(
        Submission,
        related_name="results",
        on_delete=models.CASCADE
    )
    test_case = models.ForeignKey(
        "problems.TestCase",
        on_delete=models.CASCADE,
        null=True,   # ✅ allow NULLs for old rows
        blank=True   # ✅ not required in admin forms
    )
    user_output = models.TextField()
    passed = models.BooleanField(default=False)

    def __str__(self):
        return (
            f"Submission {self.submission.id} - "
            f"TestCase {self.test_case.id if self.test_case else 'N/A'} - "
            f"{'Passed' if self.passed else 'Failed'}"
        )

# submissions/models.py
class AIHintUsage(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    used_hints = models.IntegerField(default=0)
    limit = models.IntegerField(default=3)  # default 3 hints per day
    last_reset = models.DateTimeField(default=timezone.now)

    def reset_if_needed(self):
        """Reset used_hints if 24 hours have passed since last reset"""
        if timezone.now() - self.last_reset >= timedelta(hours=24):
            self.used_hints = 0
            self.last_reset = timezone.now()
            self.save()