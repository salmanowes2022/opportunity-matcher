import os
import google.generativeai as genai
from typing import Optional, Dict
import streamlit as st
import json

def setup_gemini():
    """Initialize Gemini with API key"""
    # Try environment variable first, then Streamlit secrets
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key and hasattr(st, 'secrets'):
        api_key = st.secrets.get("GEMINI_API_KEY")
    
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found. Please add it to your .env file or Streamlit secrets")
    
    genai.configure(api_key=api_key)
    # Use the latest stable flash model that supports vision
    return genai.GenerativeModel('models/gemini-2.0-flash')

def extract_opportunity_from_image(image_bytes: bytes) -> Optional[Dict]:
    """
    Extract opportunity details from an image of a poster, flyer, or announcement
    Returns dict with: title, type, description, requirements, deadline
    """
    
    try:
        model = setup_gemini()
        
        # Create image part for Gemini
        image_part = {
            "mime_type": "image/jpeg",
            "data": image_bytes
        }
        
        # Detailed extraction prompt
        prompt = """You are analyzing an image that contains information about a scholarship, job posting, academic program, fellowship, or other opportunity.

Your task: Extract key information and return it as a JSON object.

Extract these fields:
1. **title**: The opportunity name/title
2. **type**: One of: "Scholarship", "Job", "Academic Program", "Fellowship", "Internship", "Other"
3. **description**: 2-3 sentence summary of what this opportunity offers
4. **requirements**: List ALL eligibility criteria, qualifications, requirements you can see
5. **deadline**: Application deadline in YYYY-MM-DD format if visible (or null)
6. **provider**: Organization/institution offering this
7. **funding**: Amount or salary range if mentioned
8. **location**: Where the opportunity is based
9. **link**: Any URL, email, or contact information visible

Return ONLY valid JSON with this exact structure:
{
    "title": "string",
    "type": "Scholarship" | "Job" | "Academic Program" | "Fellowship" | "Internship" | "Other",
    "description": "string",
    "requirements": "string",
    "deadline": "YYYY-MM-DD or null",
    "provider": "string or null",
    "funding": "string or null", 
    "location": "string or null",
    "link": "string or null"
}

Rules:
- If text is unclear, write "Not clearly visible" rather than guessing
- If this is NOT an opportunity announcement, return: {"error": "This image does not appear to be an opportunity announcement"}
- Be thorough - extract ALL visible requirements
- Preserve exact wording where important
"""
        
        # Generate content
        response = model.generate_content([prompt, image_part])
        
        # Parse JSON response
        response_text = response.text.strip()
        
        # Clean markdown code blocks if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        elif response_text.startswith("```"):
            response_text = response_text[3:]
        
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        # Parse JSON
        extracted = json.loads(response_text)
        
        # Check for error
        if "error" in extracted:
            return None
        
        # Validate required fields
        if not extracted.get("title") or not extracted.get("description"):
            return None
        
        return extracted
        
    except json.JSONDecodeError as e:
        st.error(f"Failed to parse AI response as JSON: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Error extracting opportunity from image: {str(e)}")
        return None