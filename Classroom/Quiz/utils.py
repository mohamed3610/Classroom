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

def grade_essay(essay_text, topic_description):
    """
    Grade an essay using the Copilot API.
    """
    if not essay_text.strip():
        return {'grade': 0.0, 'feedback': 'No text extracted for grading'}

    conn = http.client.HTTPSConnection("copilot5.p.rapidapi.com")

    # Prepare the payload for the Copilot API
    payload = json.dumps({
        "message": essay_text,
        "conversation_id": None,  # Optional: Add a conversation ID if needed
        "tone": "BALANCED",       # Tone of the response (e.g., BALANCED, FORMAL, INFORMAL)
        "markdown": False,        # Set to True if you want markdown formatting
        "photo_url": None         # Optional: Add a photo URL if needed
    })

    headers = {
        'x-rapidapi-key': "4b8c24a644mshf0872526fa20c27p1e77c6jsn4d11578ae49c",  # Replace with your API key
        'x-rapidapi-host': "copilot5.p.rapidapi.com",
        'Content-Type': "application/json"
    }

    try:
        # Make the API request
        conn.request("POST", "/copilot", payload, headers)
        res = conn.getresponse()

        # Check if the request was successful
        if res.status == 200:
            data = json.loads(res.read().decode("utf-8"))
            feedback = data.get("response", "No feedback available")

            # Simplified grading logic
            grade = min(len(feedback) / 100, 1.0) * 100
            if 'off-topic' in feedback.lower():
                grade = 0.0
                feedback += "\nGrade set to 0 due to off-topic content."

            return {'grade': round(grade, 2), 'feedback': feedback}
        else:
            logger.error(f"API Error: {res.status} - {res.reason}")
            return {'grade': 0.0, 'feedback': f'Grading system error: {res.reason}'}

    except http.client.HTTPException as e:
        logger.error(f"HTTP Error: {e}")
        return {'grade': 0.0, 'feedback': 'Connection to grading system failed'}
    except json.JSONDecodeError as e:
        logger.error(f"JSON Decode Error: {e}")
        return {'grade': 0.0, 'feedback': 'Invalid response from grading system'}
    except Exception as e:
        logger.error(f"Unexpected Error: {e}")
        return {'grade': 0.0, 'feedback': f'Grading system error: {str(e)}'}
    finally:
        conn.close()  # Ensure the connection is closed