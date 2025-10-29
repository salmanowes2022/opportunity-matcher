import os
import google.generativeai as genai
from models import Opportunity
from typing import Optional
import streamlit as st

def setup_gemini():
    """Initialize Gemini with API key"""
    api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment or secrets")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-flash')

def extract_opportunity_from_image(image_bytes: bytes) -> Optional[dict]:
    """
    Extract opportunity details from an uploaded image using Gemini
    Returns a dict that can populate the Opportunity form
    """
    
    model = setup_gemini()
    
    # Upload the image to Gemini
    image_parts = [
        {
            "mime_type": "image/jpeg",
            "data": image_bytes
        }
    ]
    
    # Craft the prompt to extract structured data
    prompt = """
You are analyzing an image of a scholarship, job posting, or program announcement.

Extract the following information and return it in a structured format:

1. **Title**: The name of the opportunity
2. **Type**: Is this a "scholarship", "job", or "program"?
3. **Description**: Brief summary of what this opportunity is about
4. **Requirements**: List of eligibility criteria, qualifications, or requirements
5. **Deadline**: Application deadline if mentioned (format: YYYY-MM-DD if possible)
6. **Provider**: Organization or institution offering this
7. **Amount**: Funding amount or salary if mentioned
8. **Link**: Application URL or contact information if visible

Return ONLY a JSON object with these exact keys:
{
    "title": "...",
    "opp_type": "scholarship" or "job" or "program",
    "description": "...",
    "requirements": "...",
    "deadline": "..." or null,
    "provider": "...",
    "amount": "..." or null,
    "link": "..." or null
}

If you cannot clearly see the image or extract information, return:
{"error": "Could not extract information from this image"}

Be accurate. If information is unclear, mark it as "Not clearly visible" rather than guessing.
"""
    
    try:
        response = model.generate_content([prompt, image_parts[0]])
        
        # Parse the response
        import json
        
        # Clean up the response text (remove markdown code blocks if present)
        response_text = response.text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        # Parse JSON
        extracted_data = json.loads(response_text)
        
        # Check for error
        if "error" in extracted_data:
            return None
            
        return extracted_data
        
    except Exception as e:
        st.error(f"Error extracting data from image: {str(e)}")
        return None