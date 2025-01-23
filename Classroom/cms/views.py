from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import CourseMaterial
from Users.models import Student

@login_required
def student_cms(request):
    try:
        # Get the student profile
        student = request.user.student_profile
    except Student.DoesNotExist:
        return redirect('landing_page')  # Redirect if the student profile doesn't exist

    # Check if the student is enrolled
    if not student.is_enrolled:
        return redirect('landing_page')  # Redirect unenrolled students to the landing page

    # Get the student's class
    student_class = student.student_class

    # Get course materials for the student's class
    if student_class:
        course_materials = CourseMaterial.objects.filter(group=student_class)
    else:
        course_materials = CourseMaterial.objects.none()  # Return an empty QuerySet

    # Check if course materials are empty
    no_course_materials = not course_materials.exists()

    context = {
        'student': student,
        'course_materials': course_materials,
        'no_course_materials': no_course_materials,
    }

    return render(request, 'cms/student_cms.html', context)