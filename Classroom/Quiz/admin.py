from django.contrib import admin
from .models import Quiz, Submission

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'group', 'created_at', 'due_date', 'is_published', 'is_active')
    list_filter = ('group', 'is_published', 'created_at')
    search_fields = ('title', 'description', 'instructions')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    def is_active(self, obj):
        return obj.is_active()
    is_active.boolean = True  # Display as a boolean icon (checkmark/cross)
    is_active.short_description = 'Is Active'  # Column header

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'quiz', 'submitted_at', 'grade', 'is_graded')
    list_filter = ('quiz', 'is_graded', 'submitted_at')
    search_fields = ('student__user__username', 'quiz__title', 'extracted_text')
    date_hierarchy = 'submitted_at'
    ordering = ('-submitted_at',)
    readonly_fields = ('submitted_at',)  # Prevent editing of submission time

    # Custom action to mark submissions as graded
    actions = ['mark_as_graded']

    def mark_as_graded(self, request, queryset):
        queryset.update(is_graded=True)
    mark_as_graded.short_description = "Mark selected submissions as graded"