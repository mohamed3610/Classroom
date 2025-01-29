# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .models import Quiz, Submission
from cms.models import Grades
from .forms import EssaySubmissionForm
import PyPDF2
import requests
import re
import logging

logger = logging.getLogger(__name__)

# API Configuration
COPILOT_API_URL = 'https://copilot5.p.rapidapi.com/copilot'
COPILOT_API_KEY = '4b8c24a644mshf0872526fa20c27p1e77c6jsn4d11578ae49c'

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file using PyPDF2"""
    try:
        text = ""
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() or ""
        return text if text.strip() else None
    except Exception as e:
        logger.error(f"PDF text extraction failed: {e}")
        return None

def extract_numeric_grade(feedback):
    """Extracts the grade from feedback text using regex"""
    match = re.search(r"Your grade is\s*(\d+\.?\d*)", feedback, re.IGNORECASE)
    return float(match.group(1)) if match else 0.0

def send_to_copilot(submission_text, topic_description, criteria):
    """Sends submission text to Copilot API for grading"""
    try:
        prompt = (
            f"Review this essay based on:\n\n{criteria}\n\n"
            f"Topic: '{topic_description}'. If off-topic, grade 0.\n\n"
            f"End feedback with 'Your grade is X'.\n\n"
            f"Submission:\n{submission_text}"
        )

        response = requests.post(
            COPILOT_API_URL,
            json={'message': prompt},
            headers={
                'X-RapidAPI-Key': COPILOT_API_KEY,
                'Content-Type': 'application/json'
            }
        )

        if response.status_code == 200:
            response_data = response.json()
            feedback = response_data.get('data', {}).get('message', 'No feedback')
            grade = extract_numeric_grade(feedback)

            if 'off-topic' in feedback.lower():
                grade = 0.0
                feedback += "\nGrade set to 0 due to off-topic content."

            return {'grade': grade, 'feedback': feedback}
        return {'error': f'API Error: {response.text}'}
    except Exception as e:
        return {'error': f'Request failed: {str(e)}'}

@login_required
def take_quiz(request, quiz_id):
    """Handle PDF submission and grading"""
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        return redirect('landing_page')

    if not student.is_enrolled:
        return redirect('landing_page')

    quiz = get_object_or_404(Quiz, id=quiz_id, is_published=True)
    existing_submission = Submission.objects.filter(student=student, quiz=quiz).first()
    
    if existing_submission:
        return redirect('quiz_result', submission_id=existing_submission.pk)

    if request.method == 'POST':
        form = EssaySubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    pdf_file = form.cleaned_data['pdf_file']
                    submission = Submission.objects.create(
                        student=student,
                        quiz=quiz,
                        image=pdf_file
                    )

                    extracted_text = extract_text_from_pdf(submission.image.path)
                    if not extracted_text:
                        submission.feedback = "Failed to extract text from PDF"
                        submission.save()
                        return render(request, 'take_quiz.html', {
                            'quiz': quiz,
                            'form': form,
                            'error': "Failed to extract text from PDF"
                        })

                    grading_result = send_to_copilot(
                        extracted_text,
                        quiz.description,
                        quiz.instructions
                    )

                    submission.extracted_text = extracted_text
                    submission.grade = grading_result.get('grade', 0)
                    submission.feedback = grading_result.get('feedback', '')
                    submission.is_graded = True
                    submission.save()

                    Grades.objects.create(
                        student=student,
                        subject=quiz.title,
                        score=submission.grade
                    )

                    return redirect('quiz_result', submission_id=submission.pk)

            except Exception as e:
                logger.error(f"Submission error: {e}")
                return render(request, 'take_quiz.html', {
                    'quiz': quiz,
                    'form': form,
                    'error': "Submission processing failed"
                })
    else:
        form = EssaySubmissionForm()

    return render(request, 'take_quiz.html', {'quiz': quiz, 'form': form})