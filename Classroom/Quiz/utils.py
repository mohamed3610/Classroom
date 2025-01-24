from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Quiz, Submission
from .forms import EssaySubmissionForm
import requests
import re
import logging

logger = logging.getLogger(__name__)

# API Configuration
COPILOT_API_URL = 'https://copilot5.p.rapidapi.com/copilot'  # Replace with actual Copilot API URL
COPILOT_API_KEY = '4b8c24a644mshf0872526fa20c27p1e77c6jsn4d11578ae49c'  # Your RapidAPI key
OCR_API_URL = "https://image-to-text30.p.rapidapi.com/api/rapidapi/image-to-text"  # OCR API endpoint
OCR_API_KEY = "4b8c24a644mshf0872526fa20c27p1e77c6jsn4d11578ae49c"  # Replace with your actual RapidAPI key

# Load spaCy model for topic relevance checking

def extract_text_from_image(image_path):
    """
    Extracts text from an image using the OCR API.
    """
    headers = {
        'X-RapidAPI-Key': OCR_API_KEY,
    }

    try:
        with open(image_path, 'rb') as image_file:
            files = {
                'image': image_file  # The image will be sent here
            }

            response = requests.post(OCR_API_URL, headers=headers, files=files)

            if response.status_code == 200:
                data = response.json()
                extracted_text = data.get('text', '')
                return extracted_text
            else:
                logger.error(f"Error extracting text. Status Code: {response.status_code}, Response: {response.text}")
                return None
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return None

def extract_numeric_grade(feedback):
    """
    Extracts the grade from the feedback using a regular expression.
    """
    match = re.search(r"Your grade is\s*(\d+\.?\d*)", feedback, re.IGNORECASE)
    if match:
        return float(match.group(1))
    return 0.0


def send_to_copilot(submission_text, , topic_description , criteria):
    """
    Sends the submission text to the Copilot API for grading and feedback.
    """
    try:
        # Form the prompt to check for topic relevance
        prompt = (
            f"Please review the student's essay based on the following grading criteria:\n\n"
            f"{criteria}\n\n"
            f"Also, check if the essay is aligned with the topic description: '{topic_description}'.\n"
            f"If the essay is off-topic, provide feedback and give a grade of 0.\n\n"
            f"At the end of your feedback, include the sentence 'Your grade is X' where X is the grade you assign.\n\n"
            f"Student's Submission:\n{submission_text}\n"
        )

        response = requests.post(COPILOT_API_URL, json={
            'message': prompt,
        }, headers={
            'X-RapidAPI-Key': COPILOT_API_KEY,
            'Content-Type': 'application/json',
        })

        if response.status_code == 200:
            response_data = response.json()
            feedback = response_data.get('data', {}).get('message', 'No feedback provided')
            grade = extract_numeric_grade(feedback)  # Extract grade as usual

            # Check for off-topic feedback
            if 'off-topic' in feedback.lower():
                grade = 0.0
                feedback += "\nGrade set to 0 due to off-topic content."

            return {'grade': grade, 'feedback': feedback}
        else:
            return {'error': f'Failed to grade the submission. API Response: {response.text}'}
    except requests.exceptions.RequestException as e:
        return {'error': f'API request failed: {str(e)}'}

@login_required
def take_quiz(request, quiz_id):
    """
    View for students to take a quiz and submit their answers.
    """
    quiz = get_object_or_404(Quiz, id=quiz_id)

    if request.method == 'POST':
        form = Quiz(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.student = request.user
            submission.quiz = quiz

            if 'image' in request.FILES:
                submission.image = request.FILES['image']
                submission.save()

                # Extract text from image
                extracted_text = extract_text_from_image(submission.image.path)
                logger.info(f"Extracted text: {extracted_text}")

                if extracted_text:
                    # Check relevance
                    is_relevant, similarity_score = is_submission_on_topic(extracted_text, quiz.title, quiz.description)
                    logger.info(f"Relevance check: {is_relevant}, Similarity Score: {similarity_score}")

                    if not is_relevant:
                        submission.grade = 0.0
                        submission.feedback = "The submission is off-topic."
                    else:
                        # Send to Copilot for grading
                        grading_result = send_to_copilot(extracted_text, quiz.criteria, quiz.description)
                        submission.grade = grading_result.get('grade', 0)
                        submission.feedback = grading_result.get('feedback', '')

                    submission.is_graded = True
                    submission.save()

                    return redirect('quiz_result', submission_id=submission.id)
                else:
                    return render(request, 'take_quiz.html', {
                        'quiz': quiz,
                        'form': form,
                        'error': "Failed to extract text from the image. Please upload a clear image."
                    })
            else:
                return render(request, 'take_quiz.html', {
                    'quiz': quiz,
                    'form': form,
                    'error': "Please upload an image of your essay."
                })
    else:
        form = EssaySubmissionForm()

    return render(request, 'take_quiz.html', {'quiz': quiz, 'form': form})