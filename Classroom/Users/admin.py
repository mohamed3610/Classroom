from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Student, Device

class StudentInline(admin.StackedInline):
    model = Student
    can_delete = False
    verbose_name_plural = 'Student Profiles'

class CustomUserAdmin(UserAdmin):
    inlines = (StudentInline,)
    list_display = ('username', 'email', 'is_student', 'is_teacher', 'is_ta')
    list_filter = ('is_student', 'is_teacher', 'is_ta')

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Device)