import streamlit as st
from models import UserProfile, Opportunity, MatchResult
import os
from datetime import datetime

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Set up API key for deployment
if 'OPENAI_API_KEY' not in os.environ:
    if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
        os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']

# Page configuration
st.set_page_config(
    page_title="Opportunity Matching Assistant",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Title and description
st.title("🎯 Opportunity Matching Assistant")
st.markdown("*AI-powered tool to evaluate how well you match scholarships, jobs, and programs*")

# Initialize session state
if 'profile' not in st.session_state:
    st.session_state.profile = None
if 'evaluation_history' not in st.session_state:
    st.session_state.evaluation_history = []

# Create main tabs
tab1, tab2, tab3 = st.tabs(["📝 Your Profile", "🔍 Check Match", "📊 History"])

# TAB 1: Profile Creation
with tab1:
    st.header("Create Your Profile")
    st.markdown("Fill out your information once, then use it to evaluate multiple opportunities.")
    
    with st.form("profile_form"):
        # Basic Information
        st.subheader("Basic Information")
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name*", help="Your full name")
            education = st.selectbox(
                "Education Level*",
                ["High School", "Bachelor's", "Master's", "PhD", "Other"],
                help="Your highest completed or current education level"
            )
            field = st.text_input(
                "Field of Study*",
                help="Your major, specialization, or field of expertise"
            )
        
        with col2:
            gpa = st.number_input(
                "GPA (optional)",
                min_value=0.0,
                max_value=4.0,
                step=0.1,
                help="Your GPA on a 4.0 scale (leave 0 if not applicable)"
            )
            experience = st.number_input(
                "Years of Experience*",
                min_value=0,
                max_value=50,
                value=0,
                help="Years of relevant work or research experience"
            )
            languages = st.text_input(
                "Languages*",
                placeholder="English, Arabic, Spanish",
                help="Languages you speak (comma separated)"
            )
        
        # Skills and Experience
        st.subheader("Skills & Experience")
        skills = st.text_area(
            "Skills*",
            placeholder="Python, Data Analysis, Research, Project Management, etc.",
            help="Your technical and soft skills (comma separated)"
        )
        
        achievements = st.text_area(
            "Key Achievements*",
            placeholder="Awards, publications, certifications, notable projects, leadership roles...",
            help="Your most significant accomplishments"
        )
        
        goals = st.text_area(
            "Your Goals*",
            placeholder="What are you looking for? Career change? Further education? Research opportunities?",
            help="Describe what you're hoping to achieve"
        )
        
        # Submit button
        submitted = st.form_submit_button("💾 Save Profile", use_container_width=True)
        
        if submitted:
            # Validation
            required_fields = [name, field, skills, languages, achievements, goals]
            if not all(required_fields):
                st.error("Please fill all required fields marked with *")
            else:
                # Create and save profile
                st.session_state.profile = UserProfile(
                    name=name,
                    education_level=education,
                    field_of_study=field,
                    gpa=gpa if gpa > 0 else None,
                    skills=skills,
                    experience_years=experience,
                    languages=languages,
                    achievements=achievements,
                    goals=goals
                )
                st.success(f"✅ Profile saved successfully for {name}!")
                st.rerun()

    # Display saved profile
    if st.session_state.profile:
        st.divider()
        st.subheader("Your Saved Profile")
        
        with st.expander("View Profile Details", expanded=False):
            profile = st.session_state.profile
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Name:** {profile.name}")
                st.write(f"**Education:** {profile.education_level}")
                st.write(f"**Field:** {profile.field_of_study}")
                st.write(f"**GPA:** {profile.gpa or 'Not provided'}")
            
            with col2:
                st.write(f"**Experience:** {profile.experience_years} years")
                st.write(f"**Languages:** {profile.languages}")
                st.write(f"**Skills:** {profile.skills}")
            
            st.write(f"**Achievements:** {profile.achievements}")
            st.write(f"**Goals:** {profile.goals}")

# TAB 2: Match Evaluation
with tab2:
    st.header("Evaluate an Opportunity")
    
    if not st.session_state.profile:
        st.warning("⚠️ Please create your profile first in the 'Your Profile' tab")
    else:
        st.success(f"Profile loaded: {st.session_state.profile.name}")
        
        with st.form("opportunity_form"):
            # Opportunity Details
            col1, col2 = st.columns([2, 1])
            
            with col1:
                opp_title = st.text_input(
                    "Opportunity Title*",
                    placeholder="e.g., Fulbright Scholarship, Data Analyst Position, Master's Program"
                )
            
            with col2:
                opp_type = st.selectbox(
                    "Type*",
                    ["Scholarship", "Job", "Academic Program", "Fellowship", "Internship", "Other"]
                )
            
            opp_description = st.text_area(
                "Description*",
                height=150,
                placeholder="Paste the full opportunity description here...",
                help="Copy and paste the complete description from the opportunity posting"
            )
            
            opp_requirements = st.text_area(
                "Requirements*",
                height=150,
                placeholder="Paste eligibility criteria and requirements here...",
                help="Copy and paste the requirements, qualifications, and eligibility criteria"
            )
            
            opp_deadline = st.text_input(
                "Deadline (optional)",
                placeholder="e.g., 2024-12-31 or March 15, 2024"
            )
            
            # Submit button
            evaluate = st.form_submit_button("🔍 Evaluate Match", use_container_width=True)
            
            if evaluate:
                if not opp_title or not opp_description or not opp_requirements:
                    st.error("Please fill all required fields marked with *")
                else:
                    # Create opportunity object
                    opportunity = Opportunity(
                        title=opp_title,
                        opp_type=opp_type,
                        description=opp_description,
                        requirements=opp_requirements,
                        deadline=opp_deadline if opp_deadline else None
                    )
                    
                    # Check if API key is available
                    if not os.environ.get('OPENAI_API_KEY'):
                        st.error("OpenAI API key not found. Please check your configuration.")
                        st.info("Make sure you have set up your OPENAI_API_KEY in your .env file or Streamlit secrets.")
                    else:
                        # AI Evaluation
                        with st.spinner("Analyzing match with AI... This may take a few seconds."):
                            try:
                                from ai_evaluator import evaluate_match
                                result = evaluate_match(st.session_state.profile, opportunity)
                                
                                # Display Results
                                st.success("Analysis Complete!")
                                st.divider()
                                
                                # Score display
                                col1, col2 = st.columns([1, 2])
                                
                                with col1:
                                    score_color = "green" if result.compatibility_score >= 0.7 else "orange" if result.compatibility_score >= 0.5 else "red"
                                    st.metric(
                                        "Compatibility Score",
                                        f"{result.compatibility_score:.1%}",
                                        help="AI-evaluated compatibility score"
                                    )
                                
                                with col2:
                                    if result.compatibility_score >= 0.7:
                                        st.success("🎉 Strong Match - Highly Recommended")
                                    elif result.compatibility_score >= 0.5:
                                        st.info("👍 Good Match - Worth Applying")
                                    else:
                                        st.warning("⚠️ Partial Match - Review Gaps First")
                                
                                # Detailed analysis
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.subheader("💪 Your Strengths")
                                    st.write(result.strengths)
                                
                                with col2:
                                    st.subheader("🔍 Areas to Address")
                                    st.write(result.gaps)
                                
                                st.subheader("💡 Recommendation")
                                st.write(result.recommendation)
                                
                                # Save to history
                                evaluation_record = {
                                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    "opportunity": opportunity,
                                    "result": result
                                }
                                st.session_state.evaluation_history.append(evaluation_record)
                                
                                st.success(f"Evaluation saved! Check your history for past evaluations.")
                                
                            except Exception as e:
                                st.error(f"Error during evaluation: {str(e)}")
                                st.info("This could be due to:")
                                st.write("• Invalid or missing OpenAI API key")
                                st.write("• Network connectivity issues")
                                st.write("• API rate limits")
                                st.write("• Insufficient OpenAI credits")

# TAB 3: History
with tab3:
    st.header("Evaluation History")
    
    if not st.session_state.evaluation_history:
        st.info("No evaluations yet. Go to 'Check Match' to evaluate your first opportunity!")
    else:
        st.write(f"You have evaluated {len(st.session_state.evaluation_history)} opportunities:")
        
        for i, record in enumerate(reversed(st.session_state.evaluation_history)):
            with st.expander(f"{record['opportunity'].title} - {record['timestamp']}", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Type:** {record['opportunity'].opp_type}")
                    st.write(f"**Score:** {record['result'].compatibility_score:.1%}")
                    if record['opportunity'].deadline:
                        st.write(f"**Deadline:** {record['opportunity'].deadline}")
                
                with col2:
                    if record['result'].compatibility_score >= 0.7:
                        st.success("Strong Match")
                    elif record['result'].compatibility_score >= 0.5:
                        st.info("Good Match")
                    else:
                        st.warning("Partial Match")
                
                st.write("**Recommendation:**")
                st.write(record['result'].recommendation)
        
        # Clear history button
        if st.button("🗑️ Clear History", type="secondary"):
            st.session_state.evaluation_history = []
            st.rerun()

# Footer
st.divider()
st.markdown("*Built with Streamlit and OpenAI • Made for finding your perfect opportunities*")