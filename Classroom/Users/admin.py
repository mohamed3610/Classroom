# users/admin.py
from django.contrib import admin
from .models import CustomUser, Student, Class, CourseMaterial, Grades, Device
from django.db.models import Exists, OuterRef

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_teacher', 'is_ta', 'is_student')
    list_filter = ('is_teacher', 'is_ta', 'is_student')
    search_fields = ('username', 'email')

# users/admin.py

class HasLoggedInFilter(admin.SimpleListFilter):
    title = 'has logged in'
    parameter_name = 'has_logged_in'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Yes'),
            ('no', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(Exists(Device.objects.filter(user=OuterRef('user'))))
        if self.value() == 'no':
            return queryset.exclude(Exists(Device.objects.filter(user=OuterRef('user'))))

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'guardian_name', 'student_class', 'is_bank_statement_submitted', 'is_enrolled')
    list_filter = ('student_class', 'is_bank_statement_submitted', 'is_enrolled', HasLoggedInFilter)
    search_fields = ('user__username', 'guardian_name')
    actions = ['enroll_students']
    readonly_fields = ('bank_statement',)


    def enroll_students(self, request, queryset):
        queryset.update(is_enrolled=True)
    enroll_students.short_description = "Enroll selected students"

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(CourseMaterial)
class CourseMaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')
    search_fields = ('title', 'description')

@admin.register(Grades)
class GradesAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'score')
    list_filter = ('subject',)
    search_fields = ('student__user__username', 'subject')

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('user', 'device_id', 'last_login')
    list_filter = ('user',)
    search_fields = ('user__username', 'device_id')