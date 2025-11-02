from langchain_openai import ChatOpenAI
from models import UserProfile
from pydantic import BaseModel, Field
from typing import List, Dict
import os

class GapAnalysis(BaseModel):
    category: str
    severity: str  # "critical", "moderate", "minor"
    description: str
    impact: str

class QuickWin(BaseModel):
    action: str
    impact: str
    time_estimate: str
    priority: str  # "high", "medium", "low"

class ImprovementSuggestion(BaseModel):
    area: str
    current_state: str
    target_state: str
    action_steps: List[str]
    timeline: str
    impact_score: float  # 0.0 to 1.0

class DayPlan(BaseModel):
    period: str  # "Next 30 Days", "Days 31-60", "Days 61-90"
    goals: List[str]
    tasks: List[str]
    success_metrics: List[str]

class ProfileOptimizationResult(BaseModel):
    profile_strength_score: float  # 0.0 to 10.0
    completeness_percentage: float  # 0.0 to 100.0
    match_potential_increase: float  # Expected improvement percentage
    critical_gaps: List[GapAnalysis]
    quick_wins: List[QuickWin]
    high_impact_improvements: List[ImprovementSuggestion]
    action_plan_30_days: DayPlan
    action_plan_60_days: DayPlan
    action_plan_90_days: DayPlan
    overall_recommendation: str

def analyze_profile(profile: UserProfile) -> ProfileOptimizationResult:
    """
    Analyzes user profile and provides comprehensive optimization recommendations
    """

    system_prompt = """You are an expert career counselor and scholarship advisor with 20+ years of experience.
Your role is to analyze candidate profiles and provide actionable, high-impact recommendations.

You evaluate:
- Profile completeness and quality
- Competitive positioning for scholarships
- Gaps that could hurt applications
- Quick wins for immediate improvement
- Strategic long-term improvements

Be specific, actionable, and encouraging. Focus on practical steps."""

    human_prompt = """Analyze this profile and provide comprehensive optimization recommendations:

PROFILE:
Name: {name}
Education: {education_level} in {field_of_study}
GPA: {gpa}
Experience: {experience_years} years
Skills: {skills}
Languages: {languages}
Achievements: {achievements}
Goals: {goals}

Provide a detailed analysis with:

1. PROFILE STRENGTH SCORE (0-10): Overall competitiveness
2. COMPLETENESS PERCENTAGE (0-100): How complete the profile is
3. MATCH POTENTIAL INCREASE: Expected improvement % if recommendations followed

4. CRITICAL GAPS: Issues that could disqualify from top scholarships
   - Category (e.g., "Missing Leadership", "Weak Achievements")
   - Severity (critical/moderate/minor)
   - Description
   - Impact on applications

5. QUICK WINS: Actions achievable in 1-2 weeks with high impact
   - Specific action
   - Expected impact
   - Time estimate
   - Priority level

6. HIGH IMPACT IMPROVEMENTS: Strategic improvements (30-90 days)
   - Area to improve
   - Current state
   - Target state
   - Step-by-step action plan
   - Timeline
   - Impact score (0.0 to 1.0)

7. 90-DAY ACTION PLAN:
   - Next 30 Days: Immediate priorities
   - Days 31-60: Medium-term development
   - Days 61-90: Strategic positioning

   Each period needs:
   - Goals
   - Specific tasks
   - Success metrics

8. OVERALL RECOMMENDATION: Encouraging summary with key priorities

Be specific with numbers, timelines, and actionable steps. This analysis will guide their scholarship success."""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", human_prompt)
    ])

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.3,
        api_key=os.environ.get("OPENAI_API_KEY")
    )

    chain = prompt | llm.with_structured_output(ProfileOptimizationResult, method="function_calling")

    try:
        result = chain.invoke({
            "name": profile.name,
            "education_level": profile.education_level,
            "field_of_study": profile.field_of_study,
            "gpa": profile.gpa or "Not provided",
            "experience_years": profile.experience_years,
            "skills": profile.skills,
            "languages": profile.languages,
            "achievements": profile.achievements,
            "goals": profile.goals
        })
        return result
    except Exception as e:
        # Fallback result
        return ProfileOptimizationResult(
            profile_strength_score=0.0,
            completeness_percentage=0.0,
            match_potential_increase=0.0,
            critical_gaps=[],
            quick_wins=[],
            high_impact_improvements=[],
            action_plan_30_days=DayPlan(period="Next 30 Days", goals=[], tasks=[], success_metrics=[]),
            action_plan_60_days=DayPlan(period="Days 31-60", goals=[], tasks=[], success_metrics=[]),
            action_plan_90_days=DayPlan(period="Days 61-90", goals=[], tasks=[], success_metrics=[]),
            overall_recommendation=f"Error analyzing profile: {str(e)}"
        )
