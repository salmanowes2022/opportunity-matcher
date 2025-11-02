from langchain_openai import ChatOpenAI
from models import UserProfile, Opportunity, MatchResult  # Only import what you need
import os

def evaluate_match(profile: UserProfile, opportunity: Opportunity) -> MatchResult:
    """
    Uses AI to evaluate how well a profile matches an opportunity
    """
    
    # System prompt - defines the AI's role
    system_prompt = """You are an expert career and opportunity advisor with years of experience 
in matching candidates to scholarships, jobs, and academic programs.

Your task is to:
1. Analyze the candidate's qualifications against the opportunity requirements
2. Identify strengths (what makes them a strong candidate)
3. Identify gaps (what they might be missing)
4. Provide an honest compatibility score (0.0 to 1.0)
5. Give actionable recommendations

Be encouraging but realistic. If there are gaps, suggest how to address them.
Focus on practical advice the candidate can act on."""

    # Human prompt - the actual data to analyze
    human_prompt = """
CANDIDATE PROFILE:
Name: {name}
Education: {education_level} in {field_of_study}
GPA: {gpa}
Experience: {experience_years} years
Skills: {skills}
Languages: {languages}
Achievements: {achievements}
Goals: {goals}

OPPORTUNITY DETAILS:
Title: {opp_title}
Type: {opp_type}
Description: {opp_description}
Requirements: {opp_requirements}

Please evaluate this match and provide:
1. A compatibility score (0.0 to 1.0, where 1.0 is perfect match)
2. Key strengths that make them a good fit
3. Potential gaps or areas for improvement
4. Your recommendation on whether they should apply and how to improve their chances

Be specific and actionable in your feedback."""

    # Create the prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", human_prompt)
    ])

    # Initialize the LLM
    llm = ChatOpenAI(
        model="gpt-4o-mini",  # Cheaper and faster
        temperature=0.3,  # Lower = more consistent
        api_key=os.environ.get("OPENAI_API_KEY")
    )

    # Create chain with structured output - ONLY MatchResult
    chain = prompt | llm.with_structured_output(MatchResult)

    # Prepare the data
    input_data = {
        "name": profile.name,
        "education_level": profile.education_level,
        "field_of_study": profile.field_of_study,
        "gpa": profile.gpa or "Not provided",
        "experience_years": profile.experience_years,
        "skills": profile.skills,
        "languages": profile.languages,
        "achievements": profile.achievements,
        "goals": profile.goals,
        "opp_title": opportunity.title,
        "opp_type": opportunity.opp_type,
        "opp_description": opportunity.description,
        "opp_requirements": opportunity.requirements
    }

    # Run the chain
    try:
        result = chain.invoke(input_data)
        return result
    except Exception as e:
        # Return a fallback result if something goes wrong
        return MatchResult(
            compatibility_score=0.0,
            strengths="Error occurred during evaluation. Please check your API key and try again.",
            gaps="Unable to analyze at this time.",
            recommendation=f"Error: {str(e)}"
        )