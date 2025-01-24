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

def grade_essay(essay_text, topic_description):
    if not essay_text.strip():
        return {'grade': 0.0, 'feedback': 'No text extracted for grading'}
    
    conn = http.client.HTTPSConnection("ai-language-tutor-learn-english-spanish-arabic-hindi.p.rapidapi.com")
    payload = json.dumps({
        "topic": topic_description,
        "nativeLanguage": "en",
        "targetLanguage": "en",
        "level": "intermediate",
        "situationType": "casual"
    })
    
    headers = {
        'x-rapidapi-key': AI_TUTOR_API_KEY,
        'x-rapidapi-host': "ai-language-tutor-learn-english-spanish-arabic-hindi.p.rapidapi.com",
        'Content-Type': "application/json"
    }
    
    try:
        conn.request("POST", "/conversation?noqueue=1", payload, headers)
        res = conn.getresponse()
        data = json.loads(res.read().decode("utf-8"))
        feedback = data.get("response", "No feedback available")
        
        # Simplified grading logic
        grade = min(len(feedback) / 100, 1.0) * 100
        if 'off-topic' in feedback.lower():
            grade = 0.0
            feedback += "\nGrade set to 0 due to off-topic content."
            
        return {'grade': round(grade, 2), 'feedback': feedback}
    except Exception as e:
        logger.error(f"Grading API failed: {e}")
        return {'grade': 0.0, 'feedback': f'Grading system error {e}'}