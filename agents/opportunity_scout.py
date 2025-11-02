from langchain_openai import ChatOpenAI
from models import UserProfile, Opportunity
from pydantic import BaseModel
from typing import List
import os

class SearchQuery(BaseModel):
    query: str
    reasoning: str
    priority: str  # "high", "medium", "low"

class SimilarOpportunity(BaseModel):
    title: str
    type: str
    why_similar: str
    relevance_score: float  # 0.0 to 1.0

class OpportunityScoutResult(BaseModel):
    search_queries: List[SearchQuery]
    similar_opportunities: List[SimilarOpportunity]
    hidden_opportunities: List[str]
    recommendation: str

def generate_search_strategies(profile: UserProfile, top_matches: List[Opportunity] = None) -> OpportunityScoutResult:
    """
    Generates intelligent search strategies based on profile and existing matches
    """

    system_prompt = """You are an expert opportunity scout specializing in scholarships, fellowships, and academic programs.
Your role is to help users discover opportunities they might have missed.

You analyze:
- User profile strengths
- Existing high-match opportunities
- Niche programs aligned with specific skills
- Hidden opportunities in user's field

Generate smart, specific search queries and suggest similar opportunities."""

    top_matches_str = ""
    if top_matches:
        top_matches_str = "\n".join([f"- {opp.title} ({opp.opp_type}): {opp.description[:200]}" for opp in top_matches[:3]])

    human_prompt = """Based on this profile, generate intelligent opportunity search strategies:

PROFILE:
Education: {education_level} in {field_of_study}
Skills: {skills}
Experience: {experience_years} years
Languages: {languages}
Goals: {goals}

TOP MATCHES SO FAR:
{top_matches}

Generate:

1. SEARCH QUERIES: 5-7 specific, actionable search queries
   - Exact query to use (e.g., "PhD scholarships computer science machine learning 2025")
   - Reasoning why this query is relevant
   - Priority level (high/medium/low)

2. SIMILAR OPPORTUNITIES: Suggest 3-5 opportunities similar to top matches
   - Title
   - Type (Scholarship/Fellowship/Program)
   - Why it's similar
   - Relevance score (0.0 to 1.0)

3. HIDDEN OPPORTUNITIES: 3-5 niche opportunities user might not know about
   - Specific program names or categories
   - Based on unique profile combinations (e.g., "Arabic-speaking AI researchers")

4. OVERALL RECOMMENDATION: Strategic search advice

Be specific with program names, organizations, and search terms."""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", human_prompt)
    ])

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.5,
        api_key=os.environ.get("OPENAI_API_KEY")
    )

    chain = prompt | llm.with_structured_output(OpportunityScoutResult, method="function_calling")

    try:
        result = chain.invoke({
            "education_level": profile.education_level,
            "field_of_study": profile.field_of_study,
            "skills": profile.skills,
            "experience_years": profile.experience_years,
            "languages": profile.languages,
            "goals": profile.goals,
            "top_matches": top_matches_str or "No matches yet"
        })
        return result
    except Exception as e:
        return OpportunityScoutResult(
            search_queries=[],
            similar_opportunities=[],
            hidden_opportunities=[],
            recommendation=f"Error generating search strategies: {str(e)}"
        )
