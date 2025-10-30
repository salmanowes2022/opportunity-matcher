from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class UserProfile(BaseModel):
    """Stores user information for matching against opportunities"""
    name: str
    education_level: str
    field_of_study: str
    gpa: Optional[float] = None
    skills: str  # Comma separated for simplicity
    experience_years: int
    languages: str  # Comma separated
    achievements: str
    goals: str

class Opportunity(BaseModel):
    """Stores opportunity details for evaluation"""
    title: str
    opp_type: str  # scholarship, job, program, etc.
    description: str
    requirements: str
    deadline: Optional[str] = None

class MatchResult(BaseModel):
    """AI evaluation result with structured output - ONLY for opportunity matching"""
    compatibility_score: float  # 0.0 to 1.0
    strengths: str  # What makes them a good fit
    gaps: str  # What they might be missing
    recommendation: str  # Should they apply and how to improve

class ApplicationMaterial(BaseModel):
    """Generated application material - ONLY for material generation"""
    material_type: str  # "cover_letter", "personal_statement", "motivation_letter"
    content: str
    word_count: int
    key_points_highlighted: List[str]
    suggestions_for_improvement: str

class DocumentAnalysis(BaseModel):
    """Analysis result from uploaded document images - ONLY for document analysis"""
    document_type: str  # "cv", "transcript", "certificate", "other"
    extracted_text: str
    key_information: Dict[str, str] = Field(default_factory=dict)  # Structured data extracted
    suggestions: str  # How to use this info
    confidence_score: float  # 0.0 to 1.0

    class Config:
        extra = "forbid"