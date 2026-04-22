from django.contrib import admin
from .models import Problem, TestCase, Tag


class TestCaseInline(admin.TabularInline):
    model = TestCase
    extra = 1
    fields = ('input_data', 'output_data', 'is_sample')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'problem_count')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

    def problem_count(self, obj):
        return obj.problems.count()
    problem_count.short_description = '# Problems'


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ('title', 'difficulty', 'tag_list', 'created_at')
    search_fields = ('title', 'tags__name')
    list_filter = ('difficulty', 'tags', 'created_at')
    filter_horizontal = ('tags',)
    inlines = [TestCaseInline]

    def tag_list(self, obj):
        return ', '.join(t.name for t in obj.tags.all()[:5])
    tag_list.short_description = 'Tags'


@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = ('problem', 'is_sample')
    search_fields = ('problem__title',)
    list_filter = ('is_sample',)
