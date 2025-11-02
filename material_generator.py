from langchain_openai import ChatOpenAI
from models import UserProfile, Opportunity, ApplicationMaterial
import os

def generate_application_material(
    profile: UserProfile, 
    opportunity: Opportunity, 
    material_type: str,
    target_word_count: int = 500
) -> ApplicationMaterial:
    """
    Generate application materials like cover letters, personal statements
    """
    
    # Different prompts for different material types
    prompts = {
        "cover_letter": {
            "system": """You are an expert career counselor specializing in writing compelling cover letters. 
            Your task is to create a professional, personalized cover letter that:
            - Shows clear connection between candidate's background and opportunity
            - Demonstrates genuine interest and research about the opportunity
            - Highlights most relevant experiences and achievements
            - Uses professional but engaging tone
            - Follows standard business letter format""",
            
            "structure": "formal business letter with clear introduction, body paragraphs showing fit, and strong conclusion"
        },
        
        "personal_statement": {
            "system": """You are an expert admissions counselor who writes compelling personal statements.
            Your task is to create a narrative that:
            - Tells the candidate's story with clear progression
            - Shows motivation and passion for the field
            - Demonstrates self-reflection and growth
            - Connects past experiences to future goals
            - Shows fit with the specific program/opportunity""",
            
            "structure": "narrative essay with engaging opening, development of themes, and clear conclusion"
        },
        
        "motivation_letter": {
            "system": """You are an expert in writing motivation letters for academic and professional opportunities.
            Your task is to create a letter that:
            - Clearly states motivation for applying
            - Shows deep understanding of the opportunity
            - Demonstrates preparedness and qualifications
            - Explains how opportunity fits career goals
            - Shows what candidate can contribute""",
            
            "structure": "structured letter with clear motivation, qualifications, and mutual benefit"
        }
    }
    
    prompt_config = prompts.get(material_type, prompts["cover_letter"])
    
    system_prompt = prompt_config["system"]
    
    human_prompt = f"""
CANDIDATE PROFILE:
Name: {profile.name}
Education: {profile.education_level} in {profile.field_of_study}
GPA: {profile.gpa or "Not provided"}
Experience: {profile.experience_years} years
Skills: {profile.skills}
Languages: {profile.languages}
Achievements: {profile.achievements}
Goals: {profile.goals}

OPPORTUNITY:
Title: {opportunity.title}
Type: {opportunity.opp_type}
Description: {opportunity.description}
Requirements: {opportunity.requirements}

TASK:
Write a {material_type.replace('_', ' ')} following this structure: {prompt_config["structure"]}

Target length: approximately {target_word_count} words

Requirements:
1. Be specific and personalized - reference actual details from both profile and opportunity
2. Show clear research and understanding of the opportunity
3. Highlight most relevant experiences that match requirements
4. Use professional but engaging tone
5. Include specific examples and achievements
6. Show genuine enthusiasm and fit

Also provide:
- Key points you highlighted in the material
- Suggestions for how the candidate could improve or customize further
"""

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.5,  # Slightly higher for more creative writing
        api_key=os.environ.get("OPENAI_API_KEY")
    )

    chain = llm.with_structured_output(ApplicationMaterial)

    # Format the messages
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": human_prompt.format(
            name=profile.name,
            education_level=profile.education_level,
            field_of_study=profile.field_of_study,
            gpa=profile.gpa or "Not provided",
            experience_years=profile.experience_years,
            skills=profile.skills,
            languages=profile.languages,
            achievements=profile.achievements,
            goals=profile.goals,
            opp_title=opportunity.title,
            opp_type=opportunity.opp_type,
            opp_description=opportunity.description,
            opp_requirements=opportunity.requirements,
            material_type=material_type,
            target_words=target_words
        )}
    ]

    try:
        result = chain.invoke(messages)
        
        # Count words in the generated content
        word_count = len(result.content.split())
        result.word_count = word_count
        result.material_type = material_type
        
        return result
        
    except Exception as e:
        return ApplicationMaterial(
            material_type=material_type,
            content=f"Error generating material: {str(e)}",
            word_count=0,
            key_points_highlighted=[],
            suggestions_for_improvement="Please check your API configuration and try again."
        )