from django.db import models
from django.utils.text import slugify


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Problem(models.Model):
    DIFFICULTY_CHOICES = [
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard')
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    input_format = models.TextField()
    output_format = models.TextField()
    constraints = models.TextField()
    sample_input = models.TextField()
    sample_output = models.TextField()
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    tags = models.ManyToManyField(Tag, related_name='problems', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_points(self):
        return {
            'Easy': 10,
            'Medium': 20,
            'Hard': 30
        }[self.difficulty]

    def __str__(self):
        return self.title


class TestCase(models.Model):
    problem = models.ForeignKey(
        Problem,
        related_name="test_cases",
        on_delete=models.CASCADE
    )
    input_data = models.TextField()
    output_data = models.TextField()
    is_sample = models.BooleanField(default=False)  # For showing in statement

    def __str__(self):
        return f"TestCase for {self.problem.title}"
