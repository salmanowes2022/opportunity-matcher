from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from models import UserProfile, Opportunity
from pydantic import BaseModel
from typing import List, Dict
import os
from datetime import datetime

class ApplicationPriority(BaseModel):
    opportunity_title: str
    priority_level: str  # "High", "Medium", "Low"
    match_score: float
    deadline: str
    reasoning: str
    estimated_effort_hours: int
    success_probability: float  # 0.0 to 1.0
    roi_score: float  # 0.0 to 1.0

class WeeklyTask(BaseModel):
    week: str  # "Week 1", "Week 2", etc.
    tasks: List[str]
    deadline_focus: List[str]

class ApplicationStrategyResult(BaseModel):
    prioritized_applications: List[ApplicationPriority]
    weekly_timeline: List[WeeklyTask]
    strategy_summary: str
    effort_estimate_total_hours: int
    recommended_focus: List[str]

def create_application_strategy(
    profile: UserProfile,
    opportunities: List[Dict]  # List of {opportunity: Opportunity, score: float}
) -> ApplicationStrategyResult:
    """
    Creates optimal application strategy based on deadlines, scores, and effort
    """

    system_prompt = """You are an expert application strategist for scholarships and fellowships.
Your role is to help applicants maximize success by prioritizing applications strategically.

You consider:
- Match scores and success probability
- Application deadlines and timeline conflicts
- Effort required vs. potential return
- Portfolio diversification (different types, locations)
- Strategic positioning

Create actionable weekly plans with specific tasks."""

    # Prepare opportunities data
    opps_data = []
    for item in opportunities:
        opp = item['opportunity']
        score = item['score']
        opps_data.append(f"""
Title: {opp.title}
Type: {opp.opp_type}
Match Score: {score:.0%}
Deadline: {opp.deadline or 'Rolling'}
Requirements: {opp.requirements[:200]}...
""")

    human_prompt = """Create an optimal application strategy for this profile and opportunities:

PROFILE:
Education: {education_level} in {field_of_study}
Experience: {experience_years} years
Goals: {goals}

OPPORTUNITIES:
{opportunities_data}

Create a comprehensive strategy with:

1. PRIORITIZED APPLICATIONS: Rank all opportunities
   - Priority Level (High/Medium/Low) with reasoning
   - Match score
   - Deadline
   - Estimated effort (hours)
   - Success probability (0.0 to 1.0)
   - ROI score (0.0 to 1.0) - balance of effort vs. success probability

2. WEEKLY TIMELINE: Break down next 8-12 weeks
   - Week-by-week tasks
   - Which applications to focus on each week
   - Account for deadlines

3. STRATEGY SUMMARY: Overall approach and priorities

4. TOTAL EFFORT ESTIMATE: Sum of all application hours

5. RECOMMENDED FOCUS: Top 3-5 applications to prioritize

Consider:
- Don't overcommit - quality over quantity
- Balance "reach" and "safety" applications
- Diversify across types and locations
- Account for preparation time (tests, documents, recommendations)"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", human_prompt)
    ])

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.3,
        api_key=os.environ.get("OPENAI_API_KEY")
    )

    chain = prompt | llm.with_structured_output(ApplicationStrategyResult, method="function_calling")

    try:
        result = chain.invoke({
            "education_level": profile.education_level,
            "field_of_study": profile.field_of_study,
            "experience_years": profile.experience_years,
            "goals": profile.goals,
            "opportunities_data": "\n---\n".join(opps_data[:10])  # Limit to top 10
        })
        return result
    except Exception as e:
        return ApplicationStrategyResult(
            prioritized_applications=[],
            weekly_timeline=[],
            strategy_summary=f"Error creating strategy: {str(e)}",
            effort_estimate_total_hours=0,
            recommended_focus=[]
        )
