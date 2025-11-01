from models import UserProfile, Opportunity
from typing import List, Dict
import asyncio
from concurrent.futures import ThreadPoolExecutor
from pydantic import BaseModel

class UnifiedActionPlan(BaseModel):
    profile_optimization: Dict = {}
    search_strategies: Dict = {}
    application_strategy: Dict = {}
    priority_actions: List[str] = []
    success_probability: float = 0.0
    time_investment_hours: int = 0
    recommended_next_steps: List[str] = []

def run_agent_sync(agent_func, *args):
    """Helper to run agent function synchronously"""
    try:
        return agent_func(*args)
    except Exception as e:
        return None

async def orchestrate_ai_analysis(
    profile: UserProfile,
    opportunities: List[Dict] = None
) -> UnifiedActionPlan:
    """
    Coordinates all AI agents to run in parallel and synthesize results
    """

    # Import agents
    from agents.profile_optimizer import analyze_profile
    from agents.opportunity_scout import generate_search_strategies
    from agents.application_strategist import create_application_strategy

    # Run agents in parallel using ThreadPoolExecutor
    loop = asyncio.get_event_loop()
    executor = ThreadPoolExecutor(max_workers=3)

    # Start all agents concurrently
    profile_task = loop.run_in_executor(executor, run_agent_sync, analyze_profile, profile)

    scout_task = None
    if opportunities:
        top_opps = [item['opportunity'] for item in opportunities[:3]]
        scout_task = loop.run_in_executor(executor, run_agent_sync, generate_search_strategies, profile, top_opps)

    strategy_task = None
    if opportunities:
        strategy_task = loop.run_in_executor(executor, run_agent_sync, create_application_strategy, profile, opportunities)

    # Wait for all to complete
    profile_result = await profile_task
    scout_result = await scout_task if scout_task else None
    strategy_result = await strategy_task if strategy_task else None

    # Synthesize results
    priority_actions = []
    recommended_next_steps = []

    if profile_result:
        # Add top 3 quick wins
        priority_actions.extend([qw.action for qw in profile_result.quick_wins[:3]])
        # Add critical gaps
        priority_actions.extend([f"Address: {gap.description}" for gap in profile_result.critical_gaps[:2]])

    if strategy_result:
        # Add top priorities
        recommended_next_steps.extend([
            f"{app.opportunity_title} - {app.priority_level} priority"
            for app in strategy_result.prioritized_applications[:3]
        ])

    # Calculate overall metrics
    success_probability = 0.0
    if profile_result and strategy_result:
        # Average of profile strength and top application probabilities
        avg_app_prob = sum([app.success_probability for app in strategy_result.prioritized_applications[:5]]) / 5 if strategy_result.prioritized_applications else 0
        success_probability = (profile_result.profile_strength_score / 10 + avg_app_prob) / 2

    time_investment = strategy_result.effort_estimate_total_hours if strategy_result else 0

    return UnifiedActionPlan(
        profile_optimization=profile_result.dict() if profile_result else {},
        search_strategies=scout_result.dict() if scout_result else {},
        application_strategy=strategy_result.dict() if strategy_result else {},
        priority_actions=priority_actions[:5],
        success_probability=success_probability,
        time_investment_hours=time_investment,
        recommended_next_steps=recommended_next_steps[:5]
    )
