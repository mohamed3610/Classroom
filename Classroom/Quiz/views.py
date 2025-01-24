import requests
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from Users.models import Student
import cms
# from .models import WritingQuiz, WritingSubmission , CourseMaterial, StudentProfile 
# from .forms import WritingQuizForm
# import pytesseract
# from PIL import Image
# import cv2
# import numpy as np
# from django.core.files.storage import default_storage
# from django.conf import settings
# import cv2

# # Define your Copilot API endpoint
# import requests

# def extract_text_from_image(image_path):
#     url = "https://image-to-text30.p.rapidapi.com/api/rapidapi/image-to-text"  # OCR API endpoint

#     headers = {
#         'X-RapidAPI-Key': "4b8c24a644mshf0872526fa20c27p1e77c6jsn4d11578ae49c",  # Replace with your actual RapidAPI key
#         # No need to set 'Content-Type' explicitly; requests will handle it.
#     }

#     try:
#         with open(image_path, 'rb') as image_file:
#             files = {
#                 'image': image_file  # The image will be sent here
#             }

#             response = requests.post(url, headers=headers, files=files)

#             if response.status_code == 200:
#                 data = response.json()
#                 extracted_text = data.get('text', '')
#                 return extracted_text
#             else:
#                 # Debugging: print full error message if status code isn't 200
#                 print(f"Error extracting text. Status Code: {response.status_code}, Response: {response.text}")
#                 return None
#     except Exception as e:
#         print(f"An error occurred: {e}")
#         return None



    

# def overlay_feedback_on_image(image_path, corrections):
#     """
#     Annotates the uploaded image with feedback corrections.
#     corrections: List of tuples (original_text, corrected_text, coordinates)
#     """
#     img = cv2.imread(image_path)
#     font = cv2.FONT_HERSHEY_SIMPLEX
#     font_scale = 0.6
#     color = (0, 0, 255)  # Red for corrections
#     thickness = 2

#     for correction in corrections:
#         original, corrected, coord = correction
#         x, y = coord
#         text = f"{original} -> {corrected}"

#         # Get the text size to draw a background rectangle
#         (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
        
#         # Draw a filled rectangle behind the text for readability
#         cv2.rectangle(img, (x, y - text_height - baseline), (x + text_width, y + baseline), (0, 0, 0), -1)
        
#         # Place the text on top of the rectangle
#         cv2.putText(img, text, (x, y), font, font_scale, color, thickness)

#     output_path = image_path.replace('.jpg', '_annotated.jpg')
#     cv2.imwrite(output_path, img)
#     return output_path

# COPILOT_API_URL = 'https://copilot5.p.rapidapi.com/copilot'  # Replace with actual Copilot API URL
# COPILOT_API_KEY = '4b8c24a644mshf0872526fa20c27p1e77c6jsn4d11578ae49c'  # Your RapidAPI key
# TEXT_DETECTION_API_URL = "https://ocr-text-detection.p.rapidapi.com/text-detection"  # Replace with actual endpoint
# TEXT_DETECTION_API_KEY = "4b8c24a644mshf0872526fa20c27p1e77c6jsn4d11578ae49c"
# def chunk_text(text, chunk_size=2000):
#     """
#     Splits the text into smaller chunks of a specified size.
#     """
#     return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

# import spacy

# nlp = spacy.load("en_core_web_md")  # Make sure this model is installed

# def is_submission_on_topic(submission_text, quiz_title, quiz_description, threshold=1):
#     """
#     Checks if the submission is relevant to the quiz title and description using semantic similarity.
#     Returns a tuple (is_relevant, similarity_score).
#     """
#     submission_doc = nlp(submission_text)
#     topic_doc = nlp(quiz_title + " " + quiz_description)

#     similarity_score = submission_doc.similarity(topic_doc)

#     is_relevant = similarity_score >= threshold
#     return is_relevant, similarity_score


# import re

# # Define extract_numeric_grade first
# def extract_numeric_grade(feedback):
#     """
#     Extracts the grade from the feedback using a regular expression.
#     """
#     match = re.search(r"Your grade is\s*(\d+\.?\d*)", feedback, re.IGNORECASE)
#     if match:
#         return float(match.group(1))
#     return 0.0




# def send_to_copilot(submission_text, criteria, topic_description):
#     try:
#         # Form the prompt to check for topic relevance
#         prompt = (
#             f"Please review the student's essay based on the following grading criteria:\n\n"
#             f"{criteria}\n\n"
#             f"Also, check if the essay is aligned with the topic description: '{topic_description}'.\n"
#             f"If the essay is off-topic, provide feedback and give a grade of 0.\n\n"
#             f"At the end of your feedback, include the sentence 'Your grade is X' where X is the grade you assign.\n\n"
#             f"Student's Submission:\n{submission_text}\n"
#         )

#         response = requests.post(COPILOT_API_URL, json={
#             'message': prompt,
#         }, headers={
#             'X-RapidAPI-Key': COPILOT_API_KEY,
#             'Content-Type': 'application/json',
#         })

#         if response.status_code == 200:
#             response_data = response.json()
#             feedback = response_data.get('data', {}).get('message', 'No feedback provided')
#             grade = extract_numeric_grade(feedback)  # Extract grade as usual

#             # Check for off-topic feedback
#             if 'off-topic' in feedback.lower():
#                 grade = 0.0
#                 feedback += "\nGrade set to 0 due to off-topic content."

#             return {'grade': grade, 'feedback': feedback}
#         else:
#             return {'error': f'Failed to grade the submission. API Response: {response.text}'}
#     except requests.exceptions.RequestException as e:
#         return {'error': f'API request failed: {str(e)}'}

# @login_required
# def take_quiz(request, quiz_id):
#     quiz = get_object_or_404(WritingQuiz, id=quiz_id)

#     if request.method == 'POST':
#         form = WritingQuizForm(request.POST, request.FILES)
#         if form.is_valid():
#             submission = form.save(commit=False)
#             submission.student = request.user
#             submission.quiz = quiz

#             if 'image' in request.FILES:
#                 submission.image = request.FILES['image']
#                 submission.save()

#                 # Extract text from image
#                 extracted_text = extract_text_from_image(submission.image.path)
#                 print(f'{extracted_text} hell no')
#                 if extracted_text:
#                     # Check relevance
                   
#                     grading_result = send_to_copilot(
#                     extracted_text, quiz.criteria, quiz.description
#                         )
#                     submission.grade = grading_result.get('grade', 0)
#                     submission.feedback = grading_result.get('feedback', '')
                    
#                 submission.is_graded = True
#                 submission.save()

#                 return redirect('quiz_result', submission_id=submission.id)
#             else:
#                 return render(request, 'take_quiz.html', {
#                     'quiz': quiz,
#                     'form': form,
#                     'error': "Please upload an image of your essay."
#                 })

#     else:
#         form = WritingQuizForm()

#     return render(request, 'take_quiz.html', {'quiz': quiz, 'form': form})

# @login_required
# def quiz_result(request, submission_id):
#     submission = WritingSubmission.objects.get(id=submission_id)
#     return render(request, 'quiz_result.html', {'submission': submission})


# @login_required
# def course_material(request):
#     # Check if the student is approved
#     try:
#         student_profile = StudentProfile.objects.get(user=request.user)
#         if not student_profile.approved:
#             return render(request, 'error.html', {'error': "You are not approved to access course materials."})
#     except StudentProfile.DoesNotExist:
#         return render(request, 'error.html', {'error': "Student profile not found."})

#     # Fetch all course materials for the student
#     course_materials = CourseMaterial.objects.all()
#     return render(request, 'course_material.html', {'course_materials': course_materials})


# @login_required
# def grades(request):
#     # Check if the student is approved
#     try:
#         student_profile = StudentProfile.objects.get(user=request.user)
#         if not student_profile.approved:
#             return render(request, 'error.html', {'error': "You are not approved to view grades."})
#     except StudentProfile.DoesNotExist:
#         return render(request, 'error.html', {'error': "Student profile not found."})

#     # Fetch grades for the logged-in student
#     grades = WritingSubmission.objects.filter(student=request.user).order_by('-submission_date')
#     return render(request, 'grades.html', {'grades': grades})

# def beautify_text(original_text):
#     # Replace this with the actual request to Copilot or another API
#     response = requests.post(
#         'https://copilot5.p.rapidapi.com/copilot',  # Example API endpoint for beautifying text
#         json={'text': original_text}
#     )
#     if response.status_code == 200:
#         return response.json()['beautified_text']  # Assuming the response contains the beautified text
#     return original_text

# def essay_detail(request, quiz_id):
#     quiz = get_object_or_404(WritingSubmission, id=quiz_id)
    
#     # Get the feedback as one block (if stored as a single string in the 'feedback' field)
#     feedback_data = quiz.feedback  # Assuming feedback is a single string
    
#     # Get the original essay text
#     essay_text = quiz.submission_text
    
#     # Loop through feedback data and highlight the mistakes in the essay text
#     highlighted_essay = essay_text
#     feedback_list = feedback_data.split(",")  # Split feedback into a list
    
#     # Highlight the mistakes in the essay
#     for mistake in feedback_list:
#         mistake = mistake.strip()
        
#         if mistake:
#             # Use regex to find the mistake and highlight it
#             highlighted_essay = re.sub(
#                 rf"({re.escape(mistake)})",
#                 r'<span class="highlight">\1</span>',
#                 highlighted_essay
#             )
    
#     # Handle beautify request (if any)
#     beautified_text = None
#     if request.method == 'POST' and 'beautify_text' in request.POST:
#         selected_text = request.POST.get('selected_text')
#         if selected_text:
#             beautified_text = beautify_text(selected_text)
#             # Optionally, you can save the beautified text to the database, but we're just passing it for now
    
#     return render(request, 'essay_detail.html', {
#         'quiz_title': quiz.quiz.title,
#         'submission_text': highlighted_essay,  # Highlighted essay
#         'feedback': feedback_data,  # Single block of feedback
#         'beautified_text': beautified_text,  # Pass the beautified text if requested
#     })


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