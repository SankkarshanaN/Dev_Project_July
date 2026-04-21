from django.contrib import admin
from .models import Member


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'problems_solved', 'total_submissions', 'favorite_language', 'join_date')
    search_fields = ('user__username',)
    list_filter = ('favorite_language',)
