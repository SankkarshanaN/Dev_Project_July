from django.contrib import admin
from .models import Problem, TestCase


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ('title', 'difficulty', 'created_at')
    search_fields = ('title',)
    list_filter = ('difficulty', 'created_at')
    # 🚫 Removed inlines = [TestCaseInline]


@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = ('problem', 'is_sample')
    search_fields = ('problem__title',)
    list_filter = ('is_sample',)
