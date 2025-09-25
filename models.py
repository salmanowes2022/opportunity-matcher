from pydantic import BaseModel
from typing import List, Optional

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
    """AI evaluation result with structured output"""
    compatibility_score: float  # 0.0 to 1.0
    strengths: str  # What makes them a good fit
    gaps: str  # What they might be missing
    recommendation: str  # Should they apply and how to improve