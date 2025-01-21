# from django.contrib import admin
# from .models import WritingQuiz , WritingSubmission
# from .models import StudentProfile

# @admin.register(StudentProfile)
# class StudentProfileAdmin(admin.ModelAdmin):
#     list_display = ('user', 'approved')
#     actions = ['approve_students']

#     def approve_students(self, request, queryset):
#         queryset.update(approved=True)
#         self.message_user(request, "Selected students have been approved.")
#     approve_students.short_description = "Approve selected students"

# admin.site.register(WritingQuiz)
# admin.site.register(WritingSubmission)
