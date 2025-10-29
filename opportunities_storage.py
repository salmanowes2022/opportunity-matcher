import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import streamlit as st

OPPORTUNITIES_FILE = Path("opportunities_database.json")

def initialize_database():
    """Create empty database file if it doesn't exist"""
    if not OPPORTUNITIES_FILE.exists():
        with open(OPPORTUNITIES_FILE, 'w') as f:
            json.dump([], f)

def load_all_opportunities() -> List[Dict]:
    """Load all opportunities from JSON file"""
    try:
        initialize_database()
        with open(OPPORTUNITIES_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading opportunities: {str(e)}")
        return []

def save_opportunity(opp_data: Dict) -> bool:
    """
    Save a new opportunity to database
    Returns True if successful
    """
    try:
        opportunities = load_all_opportunities()
        
        # Add metadata
        opp_data['saved_at'] = datetime.now().isoformat()
        opp_data['id'] = len(opportunities) + 1
        
        opportunities.append(opp_data)
        
        with open(OPPORTUNITIES_FILE, 'w') as f:
            json.dump(opportunities, f, indent=2)
        
        return True
    except Exception as e:
        st.error(f"Error saving opportunity: {str(e)}")
        return False

def delete_opportunity(opp_id: int) -> bool:
    """Delete opportunity by ID"""
    try:
        opportunities = load_all_opportunities()
        opportunities = [opp for opp in opportunities if opp.get('id') != opp_id]
        
        with open(OPPORTUNITIES_FILE, 'w') as f:
            json.dump(opportunities, f, indent=2)
        
        return True
    except Exception as e:
        st.error(f"Error deleting opportunity: {str(e)}")
        return False

def search_opportunities(query: str) -> List[Dict]:
    """Search opportunities by title or type"""
    opportunities = load_all_opportunities()
    query_lower = query.lower()
    
    return [
        opp for opp in opportunities
        if query_lower in opp.get('title', '').lower()
        or query_lower in opp.get('type', '').lower()
    ]

def get_opportunity_by_id(opp_id: int) -> Optional[Dict]:
    """Get specific opportunity by ID"""
    opportunities = load_all_opportunities()
    for opp in opportunities:
        if opp.get('id') == opp_id:
            return opp
    return None