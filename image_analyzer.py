from langchain_openai import ChatOpenAI
from models import DocumentAnalysis
import os
import base64
from io import BytesIO
from PIL import Image

def encode_image(image_bytes):
    """Convert image bytes to base64 string for API"""
    return base64.b64encode(image_bytes).decode('utf-8')

def analyze_document_image(image_bytes, document_type_hint=None):
    """
    Analyze uploaded document image and extract relevant information
    """
    
    # Encode image for API
    base64_image = encode_image(image_bytes)
    
    system_prompt = """You are an expert document analyzer specializing in academic and professional documents.

Your task is to:
1. Read and transcribe all text from the image accurately
2. Identify what type of document this is (CV/Resume, Transcript, Certificate, Cover Letter, etc.)
3. Extract key structured information relevant for job/scholarship applications
4. Assess the quality and completeness of the document
5. Provide suggestions for how this information could be used

Focus on extracting:
- Personal information (name, contact, education)
- Skills and qualifications
- Work experience
- Academic achievements
- Certifications and awards
- GPA or grades (if transcript)
- Dates and durations

Be thorough but only extract information that's clearly visible and readable."""

    human_prompt = f"""
Please analyze this document image and provide a comprehensive analysis.

Document type hint: {document_type_hint or "Unknown - please identify"}

Provide:
1. Full text transcription of what you can read
2. Document type identification
3. Key structured information extracted
4. Confidence score (0.0-1.0) based on image quality and readability
5. Suggestions for how to use this information in applications

Be specific and accurate. If text is unclear or partially obscured, note that in your analysis.
"""

    # Create the model with vision capabilities
    llm = ChatOpenAI(
        model="gpt-4o-mini",  # Supports vision
        temperature=0.1,  # Low temperature for accuracy
        api_key=os.environ.get("OPENAI_API_KEY")
    )

    try:
        # Create message with image
        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": human_prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                            "detail": "high"
                        }
                    }
                ]
            }
        ]

        # Get structured response
        chain = llm.with_structured_output(DocumentAnalysis)
        
        # For vision models, we need to call invoke differently
        response = llm.invoke(messages)
        
        # Parse the response into our structure
        # Since vision models might not support structured output directly,
        # we'll need to parse the text response
        
        # For now, let's create a simpler approach
        result = DocumentAnalysis(
            document_type=document_type_hint or "Unknown",
            extracted_text=response.content,
            key_information={},
            suggestions="Document analyzed. Review the extracted text and update your profile accordingly.",
            confidence_score=0.8
        )
        
        return result
        
    except Exception as e:
        return DocumentAnalysis(
            document_type="Error",
            extracted_text=f"Error analyzing document: {str(e)}",
            key_information={},
            suggestions="Please try uploading a clearer image or check your API configuration.",
            confidence_score=0.0
        )

def extract_profile_info_from_text(extracted_text: str, current_profile=None):
    """
    Use AI to extract profile information from document text
    """
    
    system_prompt = """You are an expert at extracting structured profile information from document text.

Extract the following information if available:
- Name
- Education level and field
- GPA (convert to 4.0 scale if needed)
- Skills (technical and soft skills)
- Years of experience
- Languages
- Key achievements
- Contact information

Return structured data that can be used to populate a user profile."""

    human_prompt = f"""
From this document text, extract profile information:

DOCUMENT TEXT:
{extracted_text}

CURRENT PROFILE (if any):
{current_profile.model_dump() if current_profile else "No existing profile"}

Extract and structure the information. If current profile exists, suggest updates/additions.
Provide specific, actionable data that can be used to enhance the user's profile.
"""

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.2,
        api_key=os.environ.get("OPENAI_API_KEY")
    )

    try:
        response = llm.invoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": human_prompt}
        ])
        
        return response.content
        
    except Exception as e:
        return f"Error extracting profile information: {str(e)}"