from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .models import Quiz, Submission
from Users.models import Student
from cms.models import Grades
from .forms import EssaySubmissionForm
from .utils import extract_text_from_image, send_to_copilot
import logging
from django.urls import reverse

logger = logging.getLogger(__name__)

@login_required
def take_quiz(request, quiz_id):
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        return redirect('landing_page')

    if not student.is_enrolled:
        return redirect('landing_page')

    quiz = get_object_or_404(Quiz, id=quiz_id, is_published=True)

    # Check if the student has already submitted this quiz
    existing_submission = Submission.objects.filter(student=student, quiz=quiz).first()
    if existing_submission:
        return redirect('already_submitted')  # Redirect to a page indicating they've already submitted

    if request.method == 'POST':
        form = EssaySubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    images = form.cleaned_data['images']
                    for image in images:
                        submission = Submission(
                            student=student,
                            quiz=quiz,
                            image=image
                        )
                        submission.save()

                        # Extract text from the image
                        extracted_text = extract_text_from_image(submission.image.path)
                        if extracted_text:
                            # Grade the essay
                            grading_result = send_to_copilot(extracted_text, quiz.description, quiz.instructions)
                            submission.extracted_text = extracted_text
                            submission.grade = grading_result.get('grade', 0)
                            submission.feedback = grading_result.get('feedback', '')
                            submission.is_graded = True
                            submission.save()

                            # Save the grade to the Grades model
                            Grades.objects.create(
                                student=student,
                                subject=quiz.title,
                                score=submission.grade
                            )
                        else:
                            submission.feedback = "Failed to extract text from image"
                            submission.save()

                    # Redirect to the submission success page
                    return redirect(reverse('quiz_result' ,submission.pk ))
            except Exception as e:
                logger.error(f"Error processing submission: {e}")
                return render(request, 'take_quiz.html', {
                    'quiz': quiz,
                    'form': form,
                    'error': "An error occurred while processing your submission. Please try again."
                })
    else:
        form = EssaySubmissionForm()

    return render(request, 'take_quiz.html', {
        'quiz': quiz,
        'form': form,
    })
@login_required
def quiz_result(request, submission_id):
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        return redirect('landing_page')

    if not student.is_enrolled:
        return redirect('landing_page')

    submission = get_object_or_404(Submission, id=submission_id, student=student)

    # Only show the grade if the submission is confirmed by the TA
    if not submission.is_confirmed:
        return render(request, 'quiz_result.html', {
            'submission': submission,
            'message': 'Your submission is getting graded. Please check back later.'
        })

    return render(request, 'quiz_result.html', {
        'submission': submission,
    })
def index(request):
    # Check if the user is authenticated
    if request.user.is_authenticated:
        try:
            # Get the student profile
            student = request.user.student_profile
            # Check if the student is enrolled
            if student.is_enrolled:
                return redirect('cms:student_cms')  # Redirect enrolled students to the CMS page
        except Student.DoesNotExist:
            pass  # Not a student, show the landing page

    # Show the landing page for unauthenticated users or unenrolled students
    return render(request, 'index.html')

