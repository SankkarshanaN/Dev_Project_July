from django.db import models

class Problem(models.Model):
    DIFFICULTY_CHOICES = [('Easy', 'Easy'), ('Medium', 'Medium'), ('Hard', 'Hard')]

    title = models.CharField(max_length=255)
    description = models.TextField()
    input_format = models.TextField()
    output_format = models.TextField()
    constraints = models.TextField()
    sample_input = models.TextField()
    sample_output = models.TextField()
    test_cases = models.JSONField()  # [{"input": ..., "output": ...}]
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_points(self):
        return {'Easy': 10, 'Medium': 20, 'Hard': 30}[self.difficulty]
    
    def __str__(self):
        return self.title
