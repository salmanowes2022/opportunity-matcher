from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel
from typing import Optional
import os
import requests
from bs4 import BeautifulSoup

class ScrapedOpportunity(BaseModel):
    title: str
    opp_type: str  # "Scholarship", "Fellowship", "Job", etc.
    description: str
    requirements: str
    deadline: Optional[str] = None
    provider: Optional[str] = None
    funding: Optional[str] = None
    location: Optional[str] = None
    link: str
    eligibility: Optional[str] = None
    benefits: Optional[str] = None

def scrape_opportunity_from_url(url: str) -> ScrapedOpportunity:
    """
    Scrapes a scholarship/opportunity URL and extracts structured information using AI
    """

    try:
        # Fetch webpage content
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract text content (remove scripts and styles)
        for script in soup(["script", "style"]):
            script.decompose()

        text = soup.get_text(separator='\n', strip=True)

        # Limit text length for AI processing (first 8000 chars usually contain key info)
        text = text[:8000]

        # Use AI to extract structured information
        system_prompt = """You are an expert at extracting scholarship and opportunity information from web pages.
Your task is to analyze the text content and extract key structured information.

Focus on:
- Scholarship/program name
- Type (Scholarship, Fellowship, Job, etc.)
- Clear description (2-3 sentences)
- Specific requirements and eligibility
- Deadline (in YYYY-MM-DD format if possible)
- Provider/organization
- Funding amount or salary
- Location
- Benefits offered

Be thorough but concise. Extract exact information from the text."""

        human_prompt = """Extract structured information from this webpage content:

URL: {url}

CONTENT:
{content}

Return structured data with all available fields. If information is not found, use "Not specified" or null."""

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", human_prompt)
        ])

        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            api_key=os.environ.get("OPENAI_API_KEY")
        )

        chain = prompt | llm.with_structured_output(ScrapedOpportunity, method="function_calling")

        result = chain.invoke({
            "url": url,
            "content": text
        })

        # Ensure link is set
        result.link = url

        return result

    except requests.RequestException as e:
        # Return error result
        return ScrapedOpportunity(
            title="Error: Could not fetch URL",
            opp_type="Scholarship",
            description=f"Failed to scrape URL: {str(e)}",
            requirements="N/A",
            deadline=None,
            provider=None,
            funding=None,
            location=None,
            link=url
        )
    except Exception as e:
        return ScrapedOpportunity(
            title="Error: Extraction failed",
            opp_type="Scholarship",
            description=f"Failed to extract information: {str(e)}",
            requirements="N/A",
            deadline=None,
            provider=None,
            funding=None,
            location=None,
            link=url
        )
