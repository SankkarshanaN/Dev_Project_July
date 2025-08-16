from django.db import models
from django.contrib.auth.models import User
from problems.models import Problem

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
