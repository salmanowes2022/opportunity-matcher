from datetime import datetime
from typing import Dict, List

class IntelligenceMetrics:
    """Track AI system performance and value metrics"""

    @staticmethod
    def calculate_time_saved(num_scholarships: int, num_materials: int = 0) -> Dict:
        """
        Calculate time saved vs manual process

        Manual process estimates:
        - Research 1 scholarship: 30 minutes
        - Evaluate match manually: 20 minutes
        - Write application material: 2 hours
        """

        research_time_saved = num_scholarships * 30  # minutes
        evaluation_time_saved = num_scholarships * 20  # minutes
        material_time_saved = num_materials * 120  # minutes

        total_minutes = research_time_saved + evaluation_time_saved + material_time_saved
        total_hours = total_minutes / 60

        return {
            "total_minutes": total_minutes,
            "total_hours": round(total_hours, 1),
            "research_saved_minutes": research_time_saved,
            "evaluation_saved_minutes": evaluation_time_saved,
            "material_saved_minutes": material_time_saved
        }

    @staticmethod
    def calculate_profile_improvement(initial_score: float, current_score: float) -> Dict:
        """Calculate profile improvement metrics"""

        improvement = current_score - initial_score
        improvement_pct = (improvement / initial_score * 100) if initial_score > 0 else 0

        return {
            "initial_score": initial_score,
            "current_score": current_score,
            "improvement": improvement,
            "improvement_percentage": round(improvement_pct, 1)
        }

    @staticmethod
    def calculate_ai_confidence(
        profile_strength: float,
        avg_match_score: float,
        completeness_pct: float
    ) -> float:
        """
        Calculate overall AI confidence score

        Factors:
        - Profile strength (0-10)
        - Average match score (0-1)
        - Profile completeness (0-100)
        """

        # Normalize all to 0-1 scale
        normalized_strength = profile_strength / 10
        normalized_completeness = completeness_pct / 100

        # Weighted average
        confidence = (
            normalized_strength * 0.4 +
            avg_match_score * 0.4 +
            normalized_completeness * 0.2
        )

        return round(confidence * 100, 1)  # Return as percentage

    @staticmethod
    def calculate_roi_metrics(
        effort_hours: int,
        success_probability: float,
        funding_amount: str = None
    ) -> Dict:
        """Calculate return on investment for applications"""

        # Parse funding if provided
        funding_value = 0
        if funding_amount:
            # Simple extraction of numbers
            import re
            numbers = re.findall(r'\d+', funding_amount.replace(',', ''))
            if numbers:
                funding_value = int(numbers[0])

        expected_value = funding_value * success_probability if funding_value else 0
        value_per_hour = expected_value / effort_hours if effort_hours > 0 else 0

        return {
            "effort_hours": effort_hours,
            "success_probability": success_probability,
            "funding_value": funding_value,
            "expected_value": round(expected_value, 2),
            "value_per_hour": round(value_per_hour, 2)
        }

    @staticmethod
    def generate_dashboard_metrics(
        profile_strength: float,
        num_scholarships_evaluated: int,
        num_materials_generated: int,
        avg_match_score: float,
        completeness_pct: float
    ) -> Dict:
        """Generate comprehensive dashboard metrics"""

        time_saved = IntelligenceMetrics.calculate_time_saved(
            num_scholarships_evaluated,
            num_materials_generated
        )

        ai_confidence = IntelligenceMetrics.calculate_ai_confidence(
            profile_strength,
            avg_match_score,
            completeness_pct
        )

        return {
            "ai_confidence_percentage": ai_confidence,
            "time_saved_hours": time_saved["total_hours"],
            "actions_suggested": num_scholarships_evaluated * 3,  # Avg 3 actions per scholarship
            "profile_strength": profile_strength,
            "scholarships_analyzed": num_scholarships_evaluated,
            "materials_generated": num_materials_generated,
            "avg_match_score_percentage": round(avg_match_score * 100, 1)
        }
