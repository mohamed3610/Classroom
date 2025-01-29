
# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .models import Quiz, Submission
from cms.models import Grades
from Users.models import Student
from .forms import EssaySubmissionForm
import PyPDF2
import requests
import re
import logging
import tempfile
from pdf2image import convert_from_path
from django.conf import settings
import pytesseract

logger = logging.getLogger(__name__)

# OCR Configuration
OCR_API_URL = "https://image-to-text30.p.rapidapi.com/api/rapidapi/image-to-text"
OCR_API_KEY = "4b8c24a644mshf0872526fa20c27p1e77c6jsn4d11578ae49c"

COPILOT_API_URL = 'https://copilot5.p.rapidapi.com/copilot'
COPILOT_API_KEY = '4b8c24a644mshf0872526fa20c27p1e77c6jsn4d11578ae49c'
# views.py
def extract_text_from_pdf(pdf_path):
    """Extract text from PDF using OCR API"""
    try:
        text = ""
        headers = {
            'X-RapidAPI-Key': OCR_API_KEY,
            'X-RapidAPI-Host': 'image-to-text30.p.rapidapi.com'
        }

        # Convert PDF to images
        images = convert_from_path(
            pdf_path,
            poppler_path=settings.POPPLER_PATH,
            dpi=300
        )

        for image in images:
            with tempfile.NamedTemporaryFile(suffix='.jpg') as temp_image:
                image.save(temp_image.name, 'JPEG')
                
                # Send to OCR API
                with open(temp_image.name, 'rb') as image_file:
                    files = {'image': image_file}
                    response = requests.post(OCR_API_URL, headers=headers, files=files)
                
                if response.status_code == 200:
                    text += response.json().get('text', '') + "\n"
                else:
                    logger.error(f"OCR API Error: {response.text}")

        return text.strip() if text else None

    except Exception as e:
        logger.error(f"OCR Processing failed: {e}")
        return None

@login_required
def take_quiz(request, quiz_id):
    """Handle PDF submission and grading"""
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
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
                    
                    # Create submission with PDF
                    submission = Submission.objects.create(
                        student=student,
                        quiz=quiz,
                        image=pdf_file  # Ensure model has pdf_file field
                    )

                    # Extract text using OCR API
                    extracted_text = extract_text_from_pdf(submission.image.path)
                    
                    if not extracted_text:
                        submission.feedback = "Failed to extract text from PDF"
                        submission.save()
                        return render(request, 'take_quiz.html', {
                            'quiz': quiz,
                            'form': form,
                            'error': "Could not read PDF content. Please ensure: "
                                     "1. Clear text in PDF\n2. PDF is not scanned\n"
                                     "3. File size <5MB"
                        })

                    # Rest of grading logic remains the same...
                    # [Keep the Copilot grading and result handling code]

            except Exception as e:
                logger.error(f"Submission error: {e}")
                return render(request, 'take_quiz.html', {
                    'quiz': quiz,
                    'form': form,
                    'error': "Error processing submission. Please try again."
                })
    
    return render(request, 'take_quiz.html', {'quiz': quiz, 'form': EssaySubmissionForm()})
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