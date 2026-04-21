from django.contrib import admin
from .models import Submission, SubmissionResult, AIHintUsage


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'problem', 'language', 'result', 'is_correct', 'submitted_at')
    list_filter = ('result', 'language', 'is_correct')
    search_fields = ('user__username', 'problem__title')
    readonly_fields = ('submitted_at',)


@admin.register(SubmissionResult)
class SubmissionResultAdmin(admin.ModelAdmin):
    list_display = ('submission', 'test_case', 'passed')
    list_filter = ('passed',)


@admin.register(AIHintUsage)
class AIHintUsageAdmin(admin.ModelAdmin):
    list_display = ('user', 'used_hints', 'limit', 'last_reset')
    search_fields = ('user__username',)
