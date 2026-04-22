from django import forms
from django.forms import inlineformset_factory
from .models import Problem, TestCase, Tag


class ProblemForm(forms.ModelForm):
    tags_text = forms.CharField(
        required=False,
        help_text="Comma-separated tags (e.g. 'arrays, dp, greedy'). New tags are auto-created.",
        widget=forms.TextInput(attrs={'placeholder': 'arrays, dp, greedy'}),
    )

    class Meta:
        model = Problem
        fields = [
            'title', 'difficulty', 'description',
            'input_format', 'output_format', 'constraints',
            'sample_input', 'sample_output',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 6}),
            'input_format': forms.Textarea(attrs={'rows': 3}),
            'output_format': forms.Textarea(attrs={'rows': 3}),
            'constraints': forms.Textarea(attrs={'rows': 3}),
            'sample_input': forms.Textarea(attrs={'rows': 3, 'class': 'font-mono'}),
            'sample_output': forms.Textarea(attrs={'rows': 3, 'class': 'font-mono'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['tags_text'].initial = ', '.join(t.name for t in self.instance.tags.all())

    def save(self, commit=True):
        problem = super().save(commit=commit)
        if commit:
            self._save_tags(problem)
        return problem

    def _save_tags(self, problem):
        raw = self.cleaned_data.get('tags_text', '') or ''
        names = [n.strip() for n in raw.split(',') if n.strip()]
        tags = []
        for name in names:
            tag, _ = Tag.objects.get_or_create(name=name)
            tags.append(tag)
        problem.tags.set(tags)


TestCaseFormSet = inlineformset_factory(
    Problem, TestCase,
    fields=('input_data', 'output_data', 'is_sample'),
    widgets={
        'input_data': forms.Textarea(attrs={'rows': 3, 'class': 'font-mono'}),
        'output_data': forms.Textarea(attrs={'rows': 3, 'class': 'font-mono'}),
    },
    extra=1,
    can_delete=True,
)
