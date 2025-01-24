import requests
import json
import http.client
import logging
import os
from PIL import Image, ImageEnhance

logger = logging.getLogger(__name__)

# API Configuration
OCR_API_URL = "https://image-to-text30.p.rapidapi.com/api/rapidapi/image-to-text"
OCR_API_KEY = "4b8c24a644mshf0872526fa20c27p1e77c6jsn4d11578ae49c"
AI_TUTOR_API_KEY = "4b8c24a644mshf0872526fa20c27p1e77c6jsn4d11578ae49c"

def preprocess_image(image_path):
    try:
        image = Image.open(image_path)
        image = image.resize((800, 800))
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        processed_image_path = f"processed_{os.path.basename(image_path)}"
        image.save(processed_image_path)
        return processed_image_path
    except Exception as e:
        logger.error(f"Image preprocessing failed: {e}")
        return None

def extract_text_from_image(image_path):
    processed_path = preprocess_image(image_path)
    if not processed_path:
        return None

    headers = {'X-RapidAPI-Key': OCR_API_KEY}
    
    try:
        with open(processed_path, 'rb') as f:
            files = {'image': f}
            response = requests.post(OCR_API_URL, headers=headers, files=files)
            if response.status_code == 200:
                return response.json().get('text', '')
            else:
                logger.error(f"OCR API Error: {response.status_code} - {response.text}")
                return None
    except Exception as e:
        logger.error(f"OCR extraction failed: {e}")
        return None
    finally:
        if os.path.exists(processed_path):
            os.remove(processed_path)


# Configure logging
logger = logging.getLogger(__name__)

def grade_easy(essay_text, topic_description):
    """
    Grade an essay using a simplified approach with the Copilot API.
    """
    if not essay_text.strip():
        return {'grade': 0.0, 'feedback': 'No text extracted for grading'}

    conn = http.client.HTTPSConnection("copilot5.p.rapidapi.com")

    # Prepare payload with explicit topic context and simpler instructions
    payload = json.dumps({
        "message": f"Provide a simple grade and brief feedback for this essay on '{topic_description}':\n{essay_text}",
        "conversation_id": "easy_grading",
        "tone": "INFORMAL",
        "markdown": False,
        "photo_url": None
    })

    headers = {
        'x-rapidapi-key': "4b8c24a644mshf0872526fa20c27p1e77c6jsn4d11578ae49c",
        'x-rapidapi-host': "copilot5.p.rapidapi.com",
        'Content-Type': "application/json"
    }

    try:
        conn.request("POST", "/copilot", payload, headers)
        res = conn.getresponse()

        if res.status == 200:
            data = json.loads(res.read().decode("utf-8"))
            feedback = data.get("response", "No feedback available")

            # Simplified grading based on positive keywords
            grade = 85.0  # Base passing grade
            if 'excellent' in feedback.lower():
                grade = 95.0
            elif 'needs improvement' in feedback.lower():
                grade = 70.0
                
            return {'grade': round(grade, 2), 'feedback': feedback}
        else:
            logger.error(f"API Error: {res.status} - {res.reason}")
            return {'grade': 0.0, 'feedback': f'Grading system error: {res.reason}'}

    except Exception as e:
        logger.error(f"Error in grade_easy: {e}")
        return {'grade': 0.0, 'feedback': 'Grading error occurred'}
    finally:
        conn.close()