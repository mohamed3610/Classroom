from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import CourseMaterial, Grades
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
        return redirect('application_under_review')  # Redirect unenrolled students to the landing page

    # Get the student's class
    student_class = student.student_class

    # Get course materials for the student's class
    if student_class:
        course_materials = CourseMaterial.objects.filter(group=student_class)
    else:
        course_materials = CourseMaterial.objects.none()  # Return an empty QuerySet

    # Get quizzes for the student's class (assuming you have a Quiz model)
    quizzes = []  # Replace with your logic to fetch quizzes

    # Get the student's grades
    grades = Grades.objects.filter(student=student)

    # Check if any of the data is empty
    no_course_materials = not course_materials.exists()  # Now this will work
    no_quizzes = not quizzes
    no_grades = not grades.exists()

    context = {
        'student': student,
        'course_materials': course_materials,
        'quizzes': quizzes,
        'grades': grades,
        'no_course_materials': no_course_materials,
        'no_quizzes': no_quizzes,
        'no_grades': no_grades,
    }

    return render(request, 'cms/student_cms.html', context)