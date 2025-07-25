from django.contrib import admin
from members.models import Member
from problems.models import Problem


class ProblemAdmin(admin.ModelAdmin):
    list_display = ('title', 'difficulty', 'points', 'time_limit', 'created_at')
    list_filter = ('difficulty', 'created_at')
    search_fields = ('title', 'description')
    ordering = ('difficulty', '-created_at')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Problem Details', {
            'fields': ('title', 'description', 'difficulty', 'points')
        }),
        ('Constraints', {
            'fields': ('time_limit', 'memory_limit')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

# Register models
admin.site.register(Member)
admin.site.register(Problem, ProblemAdmin)