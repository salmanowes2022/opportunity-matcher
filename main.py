import streamlit as st
from models import UserProfile, Opportunity, MatchResult
import os
from datetime import datetime
from enhanced_ui import apply_custom_css, create_metric_card, create_status_indicator

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Set up API keys for deployment
if 'OPENAI_API_KEY' not in os.environ:
    if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
        os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']

if 'GEMINI_API_KEY' not in os.environ:
    if hasattr(st, 'secrets') and 'GEMINI_API_KEY' in st.secrets:
        os.environ['GEMINI_API_KEY'] = st.secrets['GEMINI_API_KEY']

# Validate API keys
def validate_api_keys():
    """Check if required API keys are configured"""
    errors = []
    if not os.environ.get('OPENAI_API_KEY'):
        errors.append("❌ OPENAI_API_KEY is missing")
    if not os.environ.get('GEMINI_API_KEY'):
        errors.append("❌ GEMINI_API_KEY is missing")
    return errors

# Page configuration
st.set_page_config(
    page_title="Opportunity Matching Assistant",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply custom CSS styling
apply_custom_css()

# Title and description with enhanced styling
st.markdown('<h1 class="custom-title">Opportunity Matching Assistant</h1>', unsafe_allow_html=True)
st.markdown('<p class="custom-subtitle">AI-powered tool to evaluate how well you match scholarships, jobs, and programs</p>', unsafe_allow_html=True)

# Check API keys and show warning if missing
api_errors = validate_api_keys()
if api_errors:
    st.error("⚠️ **API Configuration Issues Detected:**")
    for error in api_errors:
        st.warning(error)
    st.info("💡 **To fix:** Add your API keys to the `.env` file in the project root directory.")
    with st.expander("📖 How to get API keys"):
        st.markdown("""
        **OpenAI API Key:**
        1. Go to https://platform.openai.com/api-keys
        2. Create a new API key
        3. Add to `.env` file as: `OPENAI_API_KEY=your-key-here`

        **Google Gemini API Key:**
        1. Go to https://makersuite.google.com/app/apikey
        2. Create a new API key
        3. Add to `.env` file as: `GEMINI_API_KEY=your-key-here`
        """)
    st.markdown("---")

# Initialize session state
if 'profile' not in st.session_state:
    st.session_state.profile = None
if 'evaluation_history' not in st.session_state:
    # Try to load from file
    import pickle
    import os
    if os.path.exists("matched_opportunities.pkl"):
        try:
            with open("matched_opportunities.pkl", "rb") as f:
                st.session_state.evaluation_history = pickle.load(f)
        except:
            st.session_state.evaluation_history = []
    else:
        st.session_state.evaluation_history = []
if 'extracted_opportunity_data' not in st.session_state:
    st.session_state.extracted_opportunity_data = {}
if 'selected_opportunity_for_materials' not in st.session_state:
    st.session_state.selected_opportunity_for_materials = None
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 0

# Create all tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📝 Your Profile",
    "🔍 Check Match",
    "📊 History",
    "✍️ Generate Materials",
    "📄 Upload Documents",
    "🗄️ Opportunity Database",
    "🤖 AI Strategy"
])

# TAB 1: Profile Creation
with tab1:
    st.header("Create Your Profile")
    st.markdown("Fill out your information once, then use it to evaluate multiple opportunities.")

    # Quick action buttons
    # Check if CV data is available in session state
    has_cv_data = 'document_analysis' in st.session_state and st.session_state.document_analysis

    if has_cv_data and not st.session_state.profile:
        # Show auto-create button when CV is uploaded but no profile exists
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("⚡ Auto-Create Profile from CV", use_container_width=True, type="primary", help="Automatically create your profile from uploaded CV"):
                cv_data = st.session_state.document_analysis
                with st.spinner("Creating profile from CV..."):
                    try:
                        from langchain_openai import ChatOpenAI
                        import json

                        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

                        prompt = f"""Extract profile information from this CV/Resume text and return ONLY a valid JSON object.

CV Text:
{cv_data.extracted_text}

Return this exact JSON structure (no extra text, no markdown):
{{
    "name": "extracted full name",
    "education_level": "Bachelor's" or "Master's" or "PhD" or "High School",
    "field_of_study": "major/field extracted from education section",
    "gpa": 3.5 or null if not mentioned,
    "skills": "comma separated list of all technical and soft skills",
    "experience_years": total years of work experience as integer,
    "languages": "comma separated languages spoken",
    "achievements": "key achievements, awards, publications, certifications",
    "goals": "inferred career goals based on CV content and trajectory"
}}

Rules:
- Use exact values from CV where possible
- If information is missing, use null or reasonable default
- Keep it concise and accurate
- Return ONLY the JSON, no other text"""

                        response = llm.invoke(prompt)
                        content = response.content.strip()

                        # Clean up if it has markdown code blocks
                        if content.startswith("```json"):
                            content = content[7:]
                        elif content.startswith("```"):
                            content = content[3:]
                        if content.endswith("```"):
                            content = content[:-3]
                        content = content.strip()

                        profile_data = json.loads(content)

                        # Create profile directly
                        st.session_state.profile = UserProfile(
                            name=profile_data.get('name') or 'From CV',
                            education_level=profile_data.get('education_level') or 'Bachelor\'s',
                            field_of_study=profile_data.get('field_of_study') or 'Not specified',
                            gpa=profile_data.get('gpa'),
                            skills=profile_data.get('skills') or 'Not specified',
                            experience_years=profile_data.get('experience_years') or 0,
                            languages=profile_data.get('languages') or 'English',
                            achievements=profile_data.get('achievements') or 'See CV for details',
                            goals=profile_data.get('goals') or 'See CV for details'
                        )
                        st.success("✅ Profile created from CV!")
                        st.balloons()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error creating profile: {str(e)}")
        with col_btn2:
            if st.button("📝 Create Manually Instead", use_container_width=True, type="secondary"):
                st.info("Scroll down to fill the form manually")
    else:
        # Original buttons layout
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        with col_btn1:
            if st.button("📄 Upload CV to Auto-fill", use_container_width=True, type="secondary"):
                st.session_state.active_tab = "tab5"
                st.info("👉 Go to 'Upload Documents' tab to upload your CV")
        with col_btn2:
            if st.button("🚀 Load Demo Profile", use_container_width=True, help="Quick load a sample profile for testing"):
                demo_profile = UserProfile(
                    name="Sarah Ahmed",
                    education_level="Master's",
                    field_of_study="Computer Science",
                    gpa=3.8,
                    skills="Python, Machine Learning, Data Analysis, Natural Language Processing, Research, Technical Writing, Problem Solving",
                    experience_years=3,
                    languages="English, Arabic, French",
                    achievements="Published 2 research papers on AI ethics, Won university hackathon 2023, Teaching Assistant for 2 years, Google Summer of Code participant, Dean's List all semesters",
                    goals="Seeking PhD opportunities in AI research, particularly interested in ethical AI and NLP applications. Looking to contribute to cutting-edge research while developing teaching experience."
                )
                st.session_state.profile = demo_profile
                st.success("✅ Demo profile loaded! Scroll down to see details.")
                st.rerun()
        with col_btn3:
            if st.session_state.profile and st.button("🎯 Go to Batch Match", use_container_width=True, type="primary"):
                st.info("👉 Go to 'Check Match' tab and scroll to Batch Match section")

    st.markdown("---")

    # Show manual form in expander if profile already exists, otherwise show it normally
    if not st.session_state.profile:
        # Show form normally when no profile exists
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
    else:
        # Hide form when profile exists, show in collapsed expander
        with st.expander("📝 Edit Profile Manually (Optional)", expanded=False):
            with st.form("profile_form_edit"):
                # Basic Information
                st.subheader("Basic Information")
                col1, col2 = st.columns(2)

                with col1:
                    name = st.text_input("Full Name*", value=st.session_state.profile.name, help="Your full name")
                    education = st.selectbox(
                        "Education Level*",
                        ["High School", "Bachelor's", "Master's", "PhD", "Other"],
                        index=["High School", "Bachelor's", "Master's", "PhD", "Other"].index(st.session_state.profile.education_level) if st.session_state.profile.education_level in ["High School", "Bachelor's", "Master's", "PhD", "Other"] else 1,
                        help="Your highest completed or current education level"
                    )
                    field = st.text_input(
                        "Field of Study*",
                        value=st.session_state.profile.field_of_study,
                        help="Your major, specialization, or field of expertise"
                    )

                with col2:
                    gpa = st.number_input(
                        "GPA (optional)",
                        min_value=0.0,
                        max_value=4.0,
                        step=0.1,
                        value=float(st.session_state.profile.gpa or 0),
                        help="Your GPA on a 4.0 scale (leave 0 if not applicable)"
                    )
                    experience = st.number_input(
                        "Years of Experience*",
                        min_value=0,
                        max_value=50,
                        value=st.session_state.profile.experience_years,
                        help="Years of relevant work or research experience"
                    )
                    languages = st.text_input(
                        "Languages*",
                        value=st.session_state.profile.languages,
                        placeholder="English, Arabic, Spanish",
                        help="Languages you speak (comma separated)"
                    )

                # Skills and Experience
                st.subheader("Skills & Experience")
                skills = st.text_area(
                    "Skills*",
                    value=st.session_state.profile.skills,
                    placeholder="Python, Data Analysis, Research, Project Management, etc.",
                    help="Your technical and soft skills (comma separated)"
                )

                achievements = st.text_area(
                    "Key Achievements*",
                    value=st.session_state.profile.achievements,
                    placeholder="Awards, publications, certifications, notable projects, leadership roles...",
                    help="Your most significant accomplishments"
                )

                goals = st.text_area(
                    "Your Goals*",
                    value=st.session_state.profile.goals,
                    placeholder="What are you looking for? Career change? Further education? Research opportunities?",
                    help="Describe what you're hoping to achieve"
                )

                # Submit button
                submitted = st.form_submit_button("💾 Update Profile", use_container_width=True)

                if submitted:
                    # Validation
                    required_fields = [name, field, skills, languages, achievements, goals]
                    if not all(required_fields):
                        st.error("Please fill all required fields marked with *")
                    else:
                        # Update profile
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
                        st.success(f"✅ Profile updated successfully!")
                        st.rerun()

    # Display saved profile with enhanced styling
    if st.session_state.profile:
        st.divider()
        st.subheader("Your Saved Profile")

        # Next step button
        st.markdown("""
        <div class="success-card">
            <strong>✅ Profile Ready!</strong><br>
            You can now match against all scholarships in the database.
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚀 Match Against All Scholarships", type="primary", use_container_width=True, key="goto_batch_match"):
            st.info("👉 Go to 'Check Match' tab and scroll down to 'Batch Match' section")

        st.markdown("---")

        # Profile summary cards
        col1, col2, col3 = st.columns(3)
        with col1:
            create_metric_card("Education", st.session_state.profile.education_level)
        with col2:
            create_metric_card("Experience", f"{st.session_state.profile.experience_years} years")
        with col3:
            create_metric_card("Applications", len(st.session_state.evaluation_history))
        
        with st.expander("View Full Profile Details", expanded=False):
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
            
            # Generate Profile PDF
            try:
                from pdf_generator import generate_profile_summary_pdf
                profile_pdf = generate_profile_summary_pdf(st.session_state.profile)
                
                st.download_button(
                    label="📄 Download Profile Summary (PDF)",
                    data=profile_pdf.getvalue(),
                    file_name=f"profile_summary_{st.session_state.profile.name.replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.info("PDF export feature requires all dependencies to be installed.")

# TAB 2: Match Evaluation WITH IMAGE UPLOAD
# TAB 2: Match Evaluation WITH IMAGE UPLOAD
with tab2:
    st.header("Evaluate an Opportunity")
    
    if not st.session_state.profile:
        st.markdown("""
        <div class="warning-card">
            <strong>⚠️ Profile Required</strong><br>
            Please create your profile first in the 'Your Profile' tab to start evaluating opportunities.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="success-card">
            <strong>✅ Profile Loaded</strong><br>
            Ready to evaluate opportunities for: <strong>{st.session_state.profile.name}</strong>
        </div>
        """, unsafe_allow_html=True)
        
        # IMAGE UPLOAD SECTION
        st.subheader("📸 Upload Opportunity Image (Optional)")
        st.markdown("Have a photo of a scholarship poster or job announcement? Upload it and we'll extract the details automatically!")
        
        uploaded_opportunity_image = st.file_uploader(
            "Upload opportunity flyer/poster/screenshot",
            type=['png', 'jpg', 'jpeg'],
            key="opportunity_image_uploader",
            help="Upload a clear photo of the opportunity announcement"
        )
        
        if uploaded_opportunity_image is not None:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.image(uploaded_opportunity_image, caption="Uploaded Opportunity Image", use_container_width=True)
            
            with col2:
                if st.button("🔍 Extract Opportunity Details", type="primary", key="extract_opp_btn"):
                    # Check for Gemini API key
                    gemini_key = os.getenv("GEMINI_API_KEY")
                    if not gemini_key and hasattr(st, 'secrets'):
                        gemini_key = st.secrets.get("GEMINI_API_KEY")
                    
                    if not gemini_key:
                        st.error("⚠️ Gemini API key not found")
                        st.markdown("""
                        <div class="warning-card">
                            <strong>Setup Required:</strong><br>
                            • Get API key from: https://aistudio.google.com/apikey<br>
                            • Add GEMINI_API_KEY to your .env file<br>
                            • Or add to Streamlit secrets for deployment
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        with st.spinner("🤖 Analyzing image with AI... This may take 10-15 seconds"):
                            try:
                                from opportunity_image_extractor import extract_opportunity_from_image
                                
                                image_bytes = uploaded_opportunity_image.getvalue()
                                extracted = extract_opportunity_from_image(image_bytes)
                                
                                if extracted:
                                    st.success("✅ Successfully extracted opportunity details!")
                                    
                                    # Store in session state
                                    st.session_state.extracted_opportunity_data = extracted
                                    
                                    # Show what was extracted
                                    with st.expander("📋 Extracted Information", expanded=True):
                                        st.json(extracted)
                                    
                                    st.info("👇 The form below has been pre-filled with extracted data. Review and edit before evaluating.")
                                    st.rerun()
                                else:
                                    st.error("❌ Could not extract opportunity details from this image")
                                    st.warning("Please ensure the image is clear and contains opportunity information (scholarship, job, program announcement)")
                                    
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
                                with st.expander("Debug Info"):
                                    st.write(f"Error type: {type(e).__name__}")
                                    st.write(f"Error details: {str(e)}")
        
        st.divider()
        
        # Get pre-fill data from extracted image
        prefill = st.session_state.extracted_opportunity_data
        
        if prefill:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.success("📸 Form pre-filled from image extraction. Review and edit as needed below.")
            with col2:
                if st.button("🗑️ Clear Pre-fill", key="clear_prefill_top"):
                    st.session_state.extracted_opportunity_data = {}
                    st.rerun()
        
        # OPPORTUNITY FORM (with prefill support)
        with st.form("opportunity_form"):
            # Opportunity Details
            col1, col2 = st.columns([2, 1])
            
            with col1:
                opp_title = st.text_input(
                    "Opportunity Title*",
                    value=prefill.get('title', ''),
                    placeholder="e.g., Fulbright Scholarship, Data Analyst Position, Master's Program"
                )
            
            with col2:
                # Get type index for selectbox
                type_options = ["Scholarship", "Job", "Academic Program", "Fellowship", "Internship", "Other"]
                default_type = prefill.get('type', 'Scholarship')
                type_index = type_options.index(default_type) if default_type in type_options else 0
                
                opp_type = st.selectbox(
                    "Type*",
                    type_options,
                    index=type_index
                )
            
            opp_description = st.text_area(
                "Description*",
                value=prefill.get('description', ''),
                height=150,
                placeholder="Paste the full opportunity description here...",
                help="Copy and paste the complete description from the opportunity posting"
            )
            
            opp_requirements = st.text_area(
                "Requirements*",
                value=prefill.get('requirements', ''),
                height=150,
                placeholder="Paste eligibility criteria and requirements here...",
                help="Copy and paste the requirements, qualifications, and eligibility criteria"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                opp_deadline = st.text_input(
                    "Deadline (optional)",
                    value=prefill.get('deadline', '') if prefill.get('deadline') and prefill.get('deadline') != 'null' else '',
                    placeholder="e.g., 2024-12-31 or March 15, 2024"
                )
            
            with col2:
                # Show additional extracted info if available (read-only display)
                if prefill.get('provider'):
                    st.text_input("Provider (extracted)", value=prefill['provider'], disabled=True, help="Organization offering this opportunity")
            
            # Show funding and location if extracted
            if prefill.get('funding') or prefill.get('location'):
                col1, col2 = st.columns(2)
                if prefill.get('funding') and prefill.get('funding') != 'null':
                    with col1:
                        st.text_input("Funding/Salary (extracted)", value=prefill['funding'], disabled=True)
                if prefill.get('location') and prefill.get('location') != 'null':
                    with col2:
                        st.text_input("Location (extracted)", value=prefill['location'], disabled=True)
            
            if prefill.get('link') and prefill.get('link') != 'null':
                st.text_input("Application Link (extracted)", value=prefill['link'], disabled=True)
            
            # Submit button - ONLY this button in the form
            evaluate = st.form_submit_button("🔍 Evaluate Match", use_container_width=True)
        
        # Handle form submission - OUTSIDE the form
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
                api_key = os.environ.get('OPENAI_API_KEY')
                if not api_key:
                    st.error("OpenAI API key not found. Please check your configuration.")
                    st.markdown("""
                    <div class="warning-card">
                        <strong>Setup Required:</strong><br>
                        • Make sure you have set up your OPENAI_API_KEY in your .env file<br>
                        • For Streamlit Cloud: Add the key to your app secrets<br>
                        • Verify your OpenAI account has credits
                    </div>
                    """, unsafe_allow_html=True)
                elif not api_key.startswith(('sk-', 'sk-proj-')):
                    st.error("Invalid API key format. Please check your OpenAI API key.")
                else:
                    # AI Evaluation
                    with st.spinner("🤖 Analyzing match with AI... This may take a few seconds."):
                        try:
                            from ai_evaluator import evaluate_match
                            result = evaluate_match(st.session_state.profile, opportunity)
                            
                            # Check if we got a valid result
                            if result.compatibility_score == 0.0 and "Error" in result.strengths:
                                st.error("❌ Evaluation failed - API key issue detected")
                                st.markdown("""
                                <div class="warning-card">
                                    <strong>API Key Problem:</strong><br>
                                    • Go to https://platform.openai.com/api-keys<br>
                                    • Create a new API key<br>
                                    • Make sure your account has credits<br>
                                    • Update your .env file or Streamlit secrets
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                # Display Results with enhanced styling
                                st.success("✅ Analysis Complete!")
                                st.divider()
                                
                                # Enhanced score display
                                create_status_indicator(result.compatibility_score)
                                
                                # Detailed analysis with enhanced cards
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.markdown("""
                                    <div class="success-card">
                                        <h4>💪 Your Strengths</h4>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    st.write(result.strengths)
                                
                                with col2:
                                    st.markdown("""
                                    <div class="info-card">
                                        <h4>🔍 Areas to Address</h4>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    st.write(result.gaps)
                                
                                st.markdown("""
                                <div class="info-card">
                                    <h4>💡 Recommendation</h4>
                                </div>
                                """, unsafe_allow_html=True)
                                st.write(result.recommendation)
                                
                                # Actions section - OUTSIDE the form
                                st.divider()
                                st.subheader("📋 Next Steps")
                                
                                col1, col2, col3, col4 = st.columns(4)
                                
                                with col1:
                                    # Generate evaluation PDF
                                    try:
                                        from pdf_generator import generate_evaluation_pdf
                                        pdf_buffer = generate_evaluation_pdf(st.session_state.profile, opportunity, result)
                                        
                                        st.download_button(
                                            label="📄 Download PDF",
                                            data=pdf_buffer.getvalue(),
                                            file_name=f"evaluation_{opportunity.title.replace(' ', '_')}.pdf",
                                            mime="application/pdf",
                                            help="Download a professional PDF report"
                                        )
                                    except Exception as e:
                                        st.button(
                                            "📄 PDF Export",
                                            disabled=True,
                                            help="PDF export requires reportlab library"
                                        )
                                
                                with col2:
                                    # Link to materials generation
                                    if st.button("✍️ Generate Materials", key="gen_mat_btn"):
                                        st.info("💡 Switch to the 'Generate Materials' tab to create personalized cover letters and personal statements!")
                                
                                with col3:
                                    # Save evaluation to history
                                    if st.button("💾 Save to History", key="save_hist_btn"):
                                        evaluation_record = {
                                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                            "opportunity": opportunity,
                                            "result": result
                                        }
                                        st.session_state.evaluation_history.append(evaluation_record)
                                        st.success("✅ Evaluation saved to history!")
                                        st.rerun()
                                
                                with col4:
                                    # Save opportunity to database
                                    if st.button("🗄️ Save to Database", key="save_db_btn", help="Save this opportunity for future use"):
                                        try:
                                            from opportunities_storage import save_opportunity
                                            
                                            opp_data = {
                                                "title": opportunity.title,
                                                "type": opportunity.opp_type,
                                                "description": opportunity.description,
                                                "requirements": opportunity.requirements,
                                                "deadline": opportunity.deadline,
                                                "provider": prefill.get('provider') if prefill and prefill.get('provider') != 'null' else None,
                                                "funding": prefill.get('funding') if prefill and prefill.get('funding') != 'null' else None,
                                                "link": prefill.get('link') if prefill and prefill.get('link') != 'null' else None
                                            }
                                            
                                            if save_opportunity(opp_data):
                                                st.success("✅ Saved to database!")
                                                st.info("👉 View in 'Opportunity Database' tab")
                                            else:
                                                st.error("Failed to save to database")
                                        except Exception as e:
                                            st.error(f"Error saving: {str(e)}")
                                
                                # Auto-save to history (silent)
                                if not any(record['opportunity'].title == opportunity.title for record in st.session_state.evaluation_history):
                                    evaluation_record = {
                                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                        "opportunity": opportunity,
                                        "result": result
                                    }
                                    st.session_state.evaluation_history.append(evaluation_record)
                                
                        except Exception as e:
                            st.error(f"❌ Error during evaluation: {str(e)}")
                            
                            # Detailed error information
                            if "401" in str(e) or "invalid_api_key" in str(e):
                                st.markdown("""
                                <div class="warning-card">
                                    <strong>🔑 API Key Issue:</strong><br>
                                    • Your OpenAI API key is invalid or expired<br>
                                    • Go to https://platform.openai.com/api-keys<br>
                                    • Generate a new key and update your configuration<br>
                                    • Make sure your account has billing set up
                                </div>
                                """, unsafe_allow_html=True)
                            elif "insufficient_quota" in str(e):
                                st.markdown("""
                                <div class="warning-card">
                                    <strong>💳 Billing Issue:</strong><br>
                                    • Your OpenAI account is out of credits<br>
                                    • Go to https://platform.openai.com/account/billing<br>
                                    • Add credits to your account<br>
                                    • Wait a few minutes for the credits to activate
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.markdown("""
                                <div class="warning-card">
                                    <strong>🔧 Technical Issue:</strong><br>
                                    • Network connectivity problems<br>
                                    • API service temporarily unavailable<br>
                                    • Rate limits exceeded (wait a minute and try again)<br>
                                    • Invalid request format
                                </div>
                                """, unsafe_allow_html=True)
                            
                            # Debug information
                            with st.expander("🐛 Debug Information", expanded=False):
                                st.write(f"Error type: {type(e).__name__}")
                                st.write(f"Error message: {str(e)}")
                                st.write(f"API key status: {'Set' if api_key else 'Not set'}")
                                st.write(f"API key format: {'Valid' if api_key and api_key.startswith(('sk-', 'sk-proj-')) else 'Invalid'}")
        
        # Quick API test section (for debugging)
        if st.session_state.profile:
            with st.expander("🔧 API Connection Test", expanded=False):
                st.write("Use this to test if your OpenAI API key is working:")
                
                if st.button("Test API Connection", key="test_api_btn"):
                    api_key = os.environ.get('OPENAI_API_KEY')
                    if not api_key:
                        st.error("No API key found")
                    else:
                        try:
                            from langchain_openai import ChatOpenAI
                            llm = ChatOpenAI(
                                model="gpt-4o-mini",
                                api_key=api_key,
                                temperature=0
                            )
                            response = llm.invoke("Respond with exactly: 'API test successful'")
                            st.success(f"✅ API Working: {response.content}")
                        except Exception as e:
                            st.error(f"❌ API Test Failed: {str(e)}")

        # SPECIFIC SCHOLARSHIP MATCHING
        st.divider()
        st.header("🎯 Match with Specific Scholarship")
        st.markdown("Select a specific scholarship from the database to evaluate your match.")

        # Load all opportunities for selection
        from opportunities_storage import load_all_opportunities
        all_opps_for_selection = load_all_opportunities()

        if all_opps_for_selection:
            # Create a selectbox with scholarship titles
            scholarship_titles = [f"{opp.get('title', 'Untitled')} - {opp.get('provider', 'N/A')}" for opp in all_opps_for_selection]

            selected_scholarship_idx = st.selectbox(
                "Choose a scholarship to evaluate:",
                range(len(scholarship_titles)),
                format_func=lambda i: scholarship_titles[i],
                help="Select a scholarship from the database"
            )

            col_spec1, col_spec2 = st.columns([2, 1])
            with col_spec1:
                selected_opp_data = all_opps_for_selection[selected_scholarship_idx]
                st.markdown(f"""
                **Type:** {selected_opp_data.get('type', 'Scholarship')}
                **Provider:** {selected_opp_data.get('provider', 'N/A')}
                **Deadline:** {selected_opp_data.get('deadline', 'N/A')}
                **Funding:** {selected_opp_data.get('funding', 'N/A')}
                """)

                with st.expander("📄 View Full Details"):
                    st.write(f"**Description:** {selected_opp_data.get('description', 'N/A')}")
                    st.write(f"**Requirements:** {selected_opp_data.get('requirements', 'N/A')}")
                    if selected_opp_data.get('link'):
                        st.markdown(f"[🔗 Application Link]({selected_opp_data.get('link')})")

            with col_spec2:
                if st.button("🔍 Evaluate This Scholarship", type="primary", use_container_width=True, key="eval_specific"):
                    with st.spinner("Evaluating match..."):
                        try:
                            # Create Opportunity object
                            opportunity = Opportunity(
                                title=selected_opp_data.get('title', ''),
                                opp_type=selected_opp_data.get('type', 'Scholarship'),
                                description=selected_opp_data.get('description', ''),
                                requirements=selected_opp_data.get('requirements', ''),
                                deadline=selected_opp_data.get('deadline')
                            )

                            # Evaluate match
                            from ai_evaluator import evaluate_match
                            result = evaluate_match(st.session_state.profile, opportunity)

                            # OPTIMIZED ANALYTICS-STYLE RESULTS DISPLAY
                            st.balloons()

                            # Header with scholarship title
                            st.markdown(f"""
                            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                        padding: 25px; border-radius: 15px; margin-bottom: 20px;">
                                <h2 style="color: white; margin: 0; text-align: center;">
                                    📊 Match Analysis Complete
                                </h2>
                                <p style="color: rgba(255,255,255,0.9); text-align: center; margin: 10px 0 0 0; font-size: 18px;">
                                    {selected_opp_data.get('title', 'Scholarship')}
                                </p>
                            </div>
                            """, unsafe_allow_html=True)

                            # KEY METRICS ROW with enhanced design
                            col_m1, col_m2, col_m3, col_m4 = st.columns(4)

                            with col_m1:
                                score_color = "#4CAF50" if result.compatibility_score >= 0.7 else "#FF9800" if result.compatibility_score >= 0.4 else "#F44336"
                                st.markdown(f"""
                                <div style="background: white; padding: 20px; border-radius: 12px;
                                            border-left: 5px solid {score_color}; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                                    <p style="color: #666; margin: 0; font-size: 12px; text-transform: uppercase; letter-spacing: 1px;">Match Score</p>
                                    <h2 style="color: {score_color}; margin: 5px 0; font-size: 36px; font-weight: bold;">{result.compatibility_score:.0%}</h2>
                                </div>
                                """, unsafe_allow_html=True)

                            with col_m2:
                                match_label = "Strong" if result.compatibility_score >= 0.7 else "Moderate" if result.compatibility_score >= 0.4 else "Weak"
                                match_emoji = "🟢" if result.compatibility_score >= 0.7 else "🟡" if result.compatibility_score >= 0.4 else "🔴"
                                st.markdown(f"""
                                <div style="background: white; padding: 20px; border-radius: 12px;
                                            box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                                    <p style="color: #666; margin: 0; font-size: 12px; text-transform: uppercase; letter-spacing: 1px;">Match Level</p>
                                    <h3 style="color: #333; margin: 5px 0; font-size: 24px;">{match_emoji} {match_label}</h3>
                                </div>
                                """, unsafe_allow_html=True)

                            with col_m3:
                                st.markdown(f"""
                                <div style="background: white; padding: 20px; border-radius: 12px;
                                            box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                                    <p style="color: #666; margin: 0; font-size: 12px; text-transform: uppercase; letter-spacing: 1px;">Type</p>
                                    <h3 style="color: #333; margin: 5px 0; font-size: 20px;">🎓 {selected_opp_data.get('type', 'N/A')}</h3>
                                </div>
                                """, unsafe_allow_html=True)

                            with col_m4:
                                st.markdown(f"""
                                <div style="background: white; padding: 20px; border-radius: 12px;
                                            box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                                    <p style="color: #666; margin: 0; font-size: 12px; text-transform: uppercase; letter-spacing: 1px;">Provider</p>
                                    <h3 style="color: #333; margin: 5px 0; font-size: 18px;">🏛️ {selected_opp_data.get('provider', 'N/A')[:20]}</h3>
                                </div>
                                """, unsafe_allow_html=True)

                            st.markdown("<br>", unsafe_allow_html=True)

                            # DETAILED ANALYSIS SECTION with tabs
                            analysis_tab1, analysis_tab2, analysis_tab3 = st.tabs(["💪 Strengths", "⚠️ Gaps", "💡 Recommendation"])

                            with analysis_tab1:
                                st.markdown("""
                                <div style="background: linear-gradient(135deg, #667eea22 0%, #764ba222 100%);
                                            padding: 25px; border-radius: 12px; margin: 15px 0;">
                                """, unsafe_allow_html=True)
                                st.markdown("#### What Makes You a Great Candidate")
                                st.write(result.strengths)
                                st.markdown("</div>", unsafe_allow_html=True)

                            with analysis_tab2:
                                st.markdown("""
                                <div style="background: #fff3cd; padding: 25px; border-radius: 12px;
                                            border-left: 4px solid #ffc107; margin: 15px 0;">
                                """, unsafe_allow_html=True)
                                st.markdown("#### Areas for Improvement")
                                st.write(result.gaps)
                                st.markdown("</div>", unsafe_allow_html=True)

                            with analysis_tab3:
                                st.markdown("""
                                <div style="background: #d1ecf1; padding: 25px; border-radius: 12px;
                                            border-left: 4px solid #0dcaf0; margin: 15px 0;">
                                """, unsafe_allow_html=True)
                                st.markdown("#### Expert Recommendation")
                                st.write(result.recommendation)

                                st.markdown("#### 📝 Action Steps")
                                if result.compatibility_score >= 0.6:
                                    st.markdown("""
                                    - ✅ **High Priority**: Start preparing your application materials
                                    - 📚 **Research**: Deep dive into the organization/program
                                    - 🔧 **Optimize**: Address the gaps mentioned above
                                    - ⏰ **Timeline**: Begin application process immediately
                                    """)
                                else:
                                    st.markdown("""
                                    - 📚 **Skill Development**: Strengthen your profile in identified areas
                                    - 🔍 **Alternative Search**: Look for opportunities that better match your profile
                                    - 💪 **Profile Enhancement**: Focus on closing critical gaps
                                    - ⏳ **Future Consideration**: Revisit this opportunity after improvements
                                    """)
                                st.markdown("</div>", unsafe_allow_html=True)

                            # AUTOMATICALLY SAVE TO HISTORY
                            evaluation_record = {
                                "timestamp": datetime.now().isoformat(),
                                "opportunity": opportunity,
                                "opportunity_title": opportunity.title,
                                "opportunity_type": opportunity.opp_type,
                                "opportunity_data": selected_opp_data,
                                "score": result.compatibility_score,
                                "result": result
                            }

                            # Check if already in history (avoid duplicates)
                            already_exists = any(
                                rec.get('opportunity_title') == opportunity.title
                                for rec in st.session_state.evaluation_history
                            )

                            if not already_exists:
                                st.session_state.evaluation_history.append(evaluation_record)
                                # Save to local file
                                import pickle
                                try:
                                    with open("matched_opportunities.pkl", "wb") as f:
                                        pickle.dump(st.session_state.evaluation_history, f)
                                except:
                                    pass

                            # ACTION BUTTONS with enhanced design
                            st.markdown("<br>", unsafe_allow_html=True)
                            st.markdown("### 🚀 Next Actions")

                            col_act1, col_act2 = st.columns(2)

                            with col_act1:
                                if selected_opp_data.get('link'):
                                    st.markdown(f"""
                                    <a href="{selected_opp_data.get('link')}" target="_blank" style="text-decoration: none;">
                                        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                                    color: white; padding: 15px; border-radius: 10px;
                                                    text-align: center; cursor: pointer; box-shadow: 0 4px 12px rgba(102,126,234,0.4);">
                                            🔗 <strong>Apply Now</strong>
                                        </div>
                                    </a>
                                    """, unsafe_allow_html=True)
                                else:
                                    st.info("No application link available")

                            with col_act2:
                                if st.button("✍️ Generate Application Materials", use_container_width=True, type="primary", key="gen_mat_specific"):
                                    st.session_state.selected_opportunity_for_materials = opportunity
                                    st.session_state.selected_opportunity_data = selected_opp_data
                                    st.success("✅ Materials ready! Go to 'Generate Materials' tab")
                                    st.info("👉 Click on 'Generate Materials' tab above")

                        except Exception as e:
                            st.error(f"Error evaluating scholarship: {str(e)}")
        else:
            st.warning("⚠️ No scholarships found in database. Add scholarships first in the 'Opportunity Database' tab.")

        # BATCH MATCHING SECTION - Match against all scholarships in database
        st.divider()
        st.divider()
        st.header("🎯 Batch Match - Evaluate All Scholarships")
        st.markdown("Automatically evaluate your profile against **all scholarships** in the database and find your best matches!")

        col_batch1, col_batch2 = st.columns([2, 1])
        with col_batch1:
            st.info("💡 This will run AI evaluation for each scholarship in the database and show results sorted by compatibility score.")

        with col_batch2:
            if st.button("🚀 Match Against All Scholarships", type="primary", use_container_width=True):
                # Load all opportunities from database
                from opportunities_storage import load_all_opportunities
                all_opportunities = load_all_opportunities()

                if not all_opportunities:
                    st.warning("⚠️ No scholarships found in database. Add some scholarships first!")
                else:
                    st.markdown(f"""
                    <div class="info-card">
                        <strong>📊 Batch Evaluation Started</strong><br>
                        Evaluating against {len(all_opportunities)} scholarships...
                    </div>
                    """, unsafe_allow_html=True)

                    # Progress bar
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    batch_results = []

                    # Evaluate each opportunity
                    for idx, opp_data in enumerate(all_opportunities):
                        status_text.text(f"Evaluating: {opp_data.get('title', 'Unknown')} ({idx + 1}/{len(all_opportunities)})")

                        try:
                            # Create Opportunity object
                            opportunity = Opportunity(
                                title=opp_data.get('title', ''),
                                opp_type=opp_data.get('type', 'Scholarship'),
                                description=opp_data.get('description', ''),
                                requirements=opp_data.get('requirements', ''),
                                deadline=opp_data.get('deadline')
                            )

                            # Evaluate match
                            from ai_evaluator import evaluate_match
                            result = evaluate_match(st.session_state.profile, opportunity)

                            # Store result
                            batch_results.append({
                                'opportunity': opportunity,
                                'result': result,
                                'opp_data': opp_data,
                                'score': result.compatibility_score
                            })

                        except Exception as e:
                            st.warning(f"⚠️ Skipped {opp_data.get('title')}: {str(e)}")

                        # Update progress
                        progress_bar.progress((idx + 1) / len(all_opportunities))

                    status_text.empty()
                    progress_bar.empty()

                    # Sort by compatibility score (highest first)
                    batch_results.sort(key=lambda x: x['score'], reverse=True)

                    # Display results
                    st.success(f"✅ Batch evaluation complete! Evaluated {len(batch_results)} scholarships.")

                    st.markdown("---")
                    st.subheader("📊 Results - Best Matches First")

                    # Summary metrics
                    if batch_results:
                        col_m1, col_m2, col_m3, col_m4 = st.columns(4)

                        high_matches = sum(1 for r in batch_results if r['score'] >= 0.7)
                        medium_matches = sum(1 for r in batch_results if 0.4 <= r['score'] < 0.7)
                        low_matches = sum(1 for r in batch_results if r['score'] < 0.4)
                        avg_score = sum(r['score'] for r in batch_results) / len(batch_results)

                        with col_m1:
                            create_metric_card("Total Evaluated", str(len(batch_results)))
                        with col_m2:
                            create_metric_card("Strong Matches", f"{high_matches} (≥70%)", help_text="Compatibility ≥ 70%")
                        with col_m3:
                            create_metric_card("Moderate Matches", f"{medium_matches} (40-69%)", help_text="Compatibility 40-69%")
                        with col_m4:
                            create_metric_card("Average Score", f"{avg_score:.1%}")

                    st.markdown("---")

                    # Display each result
                    for idx, item in enumerate(batch_results, 1):
                        opportunity = item['opportunity']
                        result = item['result']
                        opp_data = item['opp_data']
                        score = item['score']

                        # Color-coded expander based on score
                        if score >= 0.7:
                            emoji = "🟢"
                            label = "Strong Match"
                        elif score >= 0.4:
                            emoji = "🟡"
                            label = "Moderate Match"
                        else:
                            emoji = "🔴"
                            label = "Weak Match"

                        with st.expander(f"{emoji} #{idx} - {opportunity.title} - **{score:.1%}** ({label})", expanded=(idx <= 3)):
                            col_r1, col_r2 = st.columns([2, 1])

                            with col_r1:
                                st.markdown(f"**Type:** {opportunity.opp_type}")
                                st.markdown(f"**Provider:** {opp_data.get('provider', 'N/A')}")
                                st.markdown(f"**Deadline:** {opp_data.get('deadline', 'N/A')}")
                                st.markdown(f"**Funding:** {opp_data.get('funding', 'N/A')}")

                                with st.expander("📄 Full Description"):
                                    st.write(opportunity.description)

                                with st.expander("📋 Requirements"):
                                    st.write(opportunity.requirements)

                            with col_r2:
                                st.markdown(f"### {score:.1%}")
                                st.markdown(create_status_indicator(score), unsafe_allow_html=True)

                            # Evaluation details
                            st.markdown("**💪 Your Strengths:**")
                            st.write(result.strengths)

                            st.markdown("**⚠️ Gaps to Address:**")
                            st.write(result.gaps)

                            st.markdown("**💡 Recommendation:**")
                            st.write(result.recommendation)

                            # Action buttons
                            col_a1, col_a2 = st.columns(2)
                            with col_a1:
                                if opp_data.get('link'):
                                    st.markdown(f"[🔗 Apply Here]({opp_data.get('link')})")

                            with col_a2:
                                if st.button(f"✍️ Generate Materials", key=f"gen_mat_{idx}"):
                                    st.session_state.selected_opportunity_for_materials = opportunity
                                    st.session_state.selected_opportunity_data = opp_data
                                    st.success("✅ Opportunity loaded! Go to 'Generate Materials' tab")
                                    st.rerun()


# TAB 3: History
with tab3:
    st.header("Evaluation History")
    
    if not st.session_state.evaluation_history:
        st.markdown("""
        <div class="info-card">
            <strong>📊 No Evaluations Yet</strong><br>
            Go to 'Check Match' to evaluate your first opportunity!
        </div>
        """, unsafe_allow_html=True)
    else:
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            create_metric_card("Total Evaluations", len(st.session_state.evaluation_history))
        
        with col2:
            avg_score = sum(record['result'].compatibility_score for record in st.session_state.evaluation_history) / len(st.session_state.evaluation_history)
            create_metric_card("Average Score", f"{avg_score:.1%}")
        
        with col3:
            strong_matches = sum(1 for record in st.session_state.evaluation_history if record['result'].compatibility_score >= 0.7)
            create_metric_card("Strong Matches", strong_matches)
        
        st.divider()
        st.write(f"**{len(st.session_state.evaluation_history)} opportunities evaluated:**")

        for i, record in enumerate(reversed(st.session_state.evaluation_history)):
            score = record['result'].compatibility_score

            # Color-coded header
            if score >= 0.7:
                emoji = "🟢"
                label = "Strong Match"
                color = "#28a745"
            elif score >= 0.5:
                emoji = "🟡"
                label = "Good Match"
                color = "#ffc107"
            else:
                emoji = "🔴"
                label = "Weak Match"
                color = "#dc3545"

            with st.expander(f"{emoji} {record['opportunity'].title} - {score:.1%} ({label})", expanded=False):
                # Score badge
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, {color}22 0%, {color}11 100%);
                     padding: 15px; border-radius: 10px; border-left: 4px solid {color}; margin-bottom: 15px;">
                    <h3 style="margin: 0; color: {color};">Match Score: {score:.1%}</h3>
                    <p style="margin: 5px 0 0 0; opacity: 0.8;">{label}</p>
                </div>
                """, unsafe_allow_html=True)

                col1, col2 = st.columns([2, 1])

                with col1:
                    st.markdown("**📋 Opportunity Details**")
                    st.write(f"**Type:** {record['opportunity'].opp_type}")
                    if record['opportunity'].deadline:
                        st.write(f"**Deadline:** {record['opportunity'].deadline}")
                    st.write(f"**Evaluated:** {record['timestamp']}")

                    st.markdown("**💪 Your Strengths:**")
                    st.write(record['result'].strengths)

                    st.markdown("**⚠️ Gaps to Address:**")
                    st.write(record['result'].gaps)

                    st.markdown("**💡 Recommendation:**")
                    st.write(record['result'].recommendation)

                with col2:
                    st.markdown("**Actions**")

                    # Generate Materials button
                    if st.button("✍️ Generate Materials", key=f"gen_mat_hist_{i}", use_container_width=True):
                        st.session_state.selected_opportunity_for_materials = record['opportunity']
                        if 'opportunity_data' in record:
                            st.session_state.selected_opportunity_data = record['opportunity_data']
                        st.success("✅ Go to 'Generate Materials' tab")
                        st.rerun()

                    # PDF Export
                    try:
                        from pdf_generator import generate_evaluation_pdf
                        pdf_buffer = generate_evaluation_pdf(
                            st.session_state.profile,
                            record['opportunity'],
                            record['result']
                        )

                        st.download_button(
                            label="📄 Export PDF",
                            data=pdf_buffer.getvalue(),
                            file_name=f"report_{record['opportunity'].title.replace(' ', '_')}.pdf",
                            mime="application/pdf",
                            key=f"pdf_{i}",
                            use_container_width=True
                        )
                    except:
                        pass
        
        # Clear history button
        st.divider()
        if st.button("🗑️ Clear All History", type="secondary"):
            st.session_state.evaluation_history = []
            st.rerun()

# TAB 4: Generate Materials
with tab4:
    st.header("Generate Application Materials")
    
    if not st.session_state.profile:
        st.markdown("""
        <div class="warning-card">
            <strong>⚠️ Profile Required</strong><br>
            Please create your profile first in the 'Your Profile' tab.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="info-card">
            <strong>✍️ Material Generator Ready</strong><br>
            Generating personalized materials for: <strong>{st.session_state.profile.name}</strong>
        </div>
        """, unsafe_allow_html=True)

        # Debug info
        st.write("**Debug Info:**")
        st.write(f"- Selected opportunity: {st.session_state.selected_opportunity_for_materials is not None}")
        st.write(f"- History count: {len(st.session_state.evaluation_history)}")

        # Check if opportunity was selected from batch match
        has_selected_opp = st.session_state.selected_opportunity_for_materials is not None
        has_selected_opp_data = 'selected_opportunity_data' in st.session_state and st.session_state.selected_opportunity_data

        if has_selected_opp:
            st.markdown(f"""
            <div class="success-card">
                <strong>✅ Auto-filled from selected opportunity</strong><br>
                {st.session_state.selected_opportunity_for_materials.title}
            </div>
            """, unsafe_allow_html=True)

            # Show additional details if available
            if has_selected_opp_data:
                col_info1, col_info2, col_info3 = st.columns(3)
                with col_info1:
                    if st.session_state.selected_opportunity_data.get('deadline'):
                        st.info(f"⏰ Deadline: {st.session_state.selected_opportunity_data.get('deadline')}")
                with col_info2:
                    if st.session_state.selected_opportunity_data.get('provider'):
                        st.info(f"🏢 Provider: {st.session_state.selected_opportunity_data.get('provider')}")
                with col_info3:
                    if st.session_state.selected_opportunity_data.get('funding'):
                        st.info(f"💰 Funding: {st.session_state.selected_opportunity_data.get('funding')}")

        with st.form("material_generation_form"):
            col1, col2 = st.columns(2)

            with col1:
                material_type = st.selectbox(
                    "Material Type",
                    ["cover_letter", "personal_statement", "motivation_letter"],
                    format_func=lambda x: x.replace('_', ' ').title()
                )

                target_words = st.slider(
                    "Target Word Count",
                    min_value=200,
                    max_value=1000,
                    value=500,
                    step=50
                )

            with col2:
                # Opportunity selection mode
                available_options = []
                default_index = 0

                if st.session_state.selected_opportunity_for_materials:
                    available_options.append("Selected Match")
                if st.session_state.evaluation_history:
                    if not available_options:
                        default_index = 0
                    available_options.append("History")

                if not available_options:
                    st.warning("⚠️ No opportunities available. Please match an opportunity first!")
                    use_selected = False
                    use_previous = False
                    selected_opp = None
                else:
                    opp_selection_mode = st.radio(
                        "Select Opportunity From:",
                        available_options,
                        index=default_index,
                        help="Choose where to get opportunity details"
                    )

                    use_selected = False
                    use_previous = False
                    selected_opp = None

                    if opp_selection_mode == "Selected Match":
                        use_selected = True
                    elif opp_selection_mode == "History":
                        use_previous = True
                        selected_opp = st.selectbox(
                            "Choose from evaluated opportunities:",
                            range(len(st.session_state.evaluation_history)),
                            format_func=lambda x: f"{st.session_state.evaluation_history[x]['opportunity'].title} ({st.session_state.evaluation_history[x]['result'].compatibility_score:.0%})"
                        )

            # Opportunity details
            st.divider()

            if use_selected and st.session_state.selected_opportunity_for_materials:
                st.subheader("✅ Selected Opportunity")
                col_det1, col_det2 = st.columns(2)
                with col_det1:
                    st.write(f"**Title:** {st.session_state.selected_opportunity_for_materials.title}")
                    st.write(f"**Type:** {st.session_state.selected_opportunity_for_materials.opp_type}")
                with col_det2:
                    if has_selected_opp_data:
                        if st.session_state.selected_opportunity_data.get('deadline'):
                            st.write(f"**Deadline:** {st.session_state.selected_opportunity_data.get('deadline')}")
                        if st.session_state.selected_opportunity_data.get('funding'):
                            st.write(f"**Funding:** {st.session_state.selected_opportunity_data.get('funding')}")

            elif use_previous and st.session_state.evaluation_history:
                st.subheader("✅ Selected Opportunity")
                selected_record = st.session_state.evaluation_history[selected_opp]
                st.write(f"**Title:** {selected_record['opportunity'].title}")
                st.write(f"**Type:** {selected_record['opportunity'].opp_type}")
                st.write(f"**Match Score:** {selected_record['result'].compatibility_score:.0%}")

            else:
                st.warning("⚠️ Please select an opportunity from 'Selected Match' or 'History' to generate materials.")
            
            generate_material = st.form_submit_button("✍️ Generate Material", use_container_width=True)

        # Process outside the form
        if generate_material:
            # Get opportunity data
            if use_selected and st.session_state.selected_opportunity_for_materials:
                opportunity = st.session_state.selected_opportunity_for_materials
            elif use_previous and st.session_state.evaluation_history:
                opportunity = st.session_state.evaluation_history[selected_opp]['opportunity']
            else:
                st.error("Please select an opportunity from 'Selected Match' or 'History' to generate materials.")
                st.stop()

            # Generate material
            with st.spinner(f"🤖 Generating {material_type.replace('_', ' ')}... This may take 10-15 seconds."):
                try:
                    from material_generator import generate_application_material

                    result = generate_application_material(
                        st.session_state.profile,
                        opportunity,
                        material_type,
                        target_words
                    )

                    # Display results
                    st.success(f"✅ {material_type.replace('_', ' ').title()} Generated Successfully!")

                    col1, col2 = st.columns([2, 1])

                    with col2:
                        create_metric_card("Word Count", result.word_count)
                        create_metric_card("Target", target_words)

                        if abs(result.word_count - target_words) <= 50:
                            st.success("🎯 Length on target!")
                        elif result.word_count < target_words * 0.8:
                            st.warning("📏 Consider expanding")
                        elif result.word_count > target_words * 1.2:
                            st.warning("✂️ Consider shortening")

                    with col1:
                        st.subheader("Generated Material")
                        st.text_area(
                            "Content",
                            value=result.content,
                            height=400,
                            help="Copy this content and customize as needed"
                        )

                    # Key points and suggestions
                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("""
                        <div class="success-card">
                            <h4>🎯 Key Points Highlighted</h4>
                        </div>
                        """, unsafe_allow_html=True)
                        for point in result.key_points_highlighted:
                            st.write(f"• {point}")

                    with col2:
                        st.markdown("""
                        <div class="info-card">
                            <h4>💡 Suggestions for Improvement</h4>
                        </div>
                        """, unsafe_allow_html=True)
                        st.write(result.suggestions_for_improvement)

                    # Download option (OUTSIDE FORM)
                    st.divider()
                    st.download_button(
                        label=f"📄 Download {material_type.replace('_', ' ').title()} (TXT)",
                        data=result.content,
                        file_name=f"{material_type}_{opportunity.title.replace(' ', '_')}.txt",
                        mime="text/plain"
                    )

                except Exception as e:
                    st.error(f"❌ Error generating material: {str(e)}")

# TAB 5: Document Upload and Analysis
with tab5:
    st.header("Upload and Analyze Documents")
    st.markdown("Upload your CV (PDF or image) to automatically create your profile and match against scholarships.")

    # Instructions
    st.markdown("""
    <div class="info-card">
        <h4>📋 How it works:</h4>
        <ol>
            <li>Upload your CV as PDF or image (PNG/JPG)</li>
            <li>AI extracts text and analyzes your profile</li>
            <li>Click "Auto-fill Profile" to create your profile</li>
            <li>Go to "Check Match" tab to batch match all scholarships</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # File uploader
    uploaded_file = st.file_uploader(
        "Choose a document (image or PDF)",
        type=['png', 'jpg', 'jpeg', 'pdf'],
        help="Upload clear, high-quality images or PDF files for best results"
    )
    
    if uploaded_file is not None:
        # Check if PDF or image
        is_pdf = uploaded_file.name.lower().endswith('.pdf')

        # Display the uploaded document
        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("📄 Uploaded Document")
            if not is_pdf:
                st.image(uploaded_file, caption="Uploaded Document", use_container_width=True)
            else:
                st.info(f"📄 PDF uploaded: {uploaded_file.name}")

            # Document type hint
            doc_type_hint = st.selectbox(
                "Document Type (optional hint)",
                ["Auto-detect", "CV/Resume", "Academic Transcript", "Certificate", "Cover Letter", "Other"]
            )

            # Analyze button
            if st.button("🔍 Analyze Document", type="primary"):

                if not os.environ.get('OPENAI_API_KEY'):
                    st.error("OpenAI API key not found. Please check your configuration.")
                else:
                    with st.spinner("🤖 Analyzing document... This may take 15-20 seconds."):
                        try:
                            # Handle PDF differently
                            if is_pdf:
                                import fitz  # PyMuPDF
                                from io import BytesIO

                                # Extract text from PDF
                                pdf_bytes = uploaded_file.getvalue()
                                pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")

                                extracted_text = ""
                                for page_num in range(len(pdf_document)):
                                    page = pdf_document[page_num]
                                    extracted_text += page.get_text()

                                # Create analysis object from extracted text
                                from models import DocumentAnalysis
                                from langchain_openai import ChatOpenAI

                                llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

                                doc_hint = None if doc_type_hint == "Auto-detect" else doc_type_hint

                                prompt = f"""Analyze this document text and provide structured information.

Document text:
{extracted_text}

Document type hint: {doc_hint or 'None'}

Provide:
1. Document type (CV, transcript, certificate, etc.)
2. Key information extracted (as a dictionary)
3. Suggestions for the user
4. Confidence score (0.0 to 1.0)

Return as structured data."""

                                analysis_result = llm.with_structured_output(DocumentAnalysis, method="function_calling").invoke(prompt)
                                analysis_result.extracted_text = extracted_text
                                analysis = analysis_result

                            else:
                                # Handle image
                                from image_analyzer import analyze_document_image, extract_profile_info_from_text

                                # Read image bytes
                                image_bytes = uploaded_file.getvalue()

                                # Analyze the document
                                doc_hint = None if doc_type_hint == "Auto-detect" else doc_type_hint
                                analysis = analyze_document_image(image_bytes, doc_hint)
                            
                            # Store analysis in session state for later use
                            st.session_state.document_analysis = analysis
                            
                            # Display results in second column
                            with col2:
                                st.subheader("📊 Analysis Results")
                                
                                # Document type and confidence
                                col_a, col_b = st.columns(2)
                                with col_a:
                                    create_metric_card("Document Type", analysis.document_type)
                                with col_b:
                                    create_metric_card("Confidence", f"{analysis.confidence_score:.1%}")
                                
                                # Extracted text
                                with st.expander("📄 Extracted Text", expanded=True):
                                    st.text_area(
                                        "Full Text",
                                        value=analysis.extracted_text,
                                        height=200,
                                        help="All text extracted from the document"
                                    )
                                
                                # Suggestions
                                st.markdown("""
                                <div class="info-card">
                                    <h4>💡 Suggestions</h4>
                                </div>
                                """, unsafe_allow_html=True)
                                st.write(analysis.suggestions)
                            
                            # Auto-fill profile button (for CV/Resume only)
                            if "CV" in analysis.document_type or "Resume" in analysis.document_type:
                                st.divider()
                                st.subheader("🔄 Auto-fill Profile from CV")
                                
                                col1, col2 = st.columns([2, 1])
                                with col1:
                                    st.info("This appears to be a CV/Resume. You can automatically create a profile from this document.")
                                
                                with col2:
                                    if st.button("⚡ Auto-fill Profile", type="primary", use_container_width=True):
                                        with st.spinner("Extracting profile information..."):
                                            try:
                                                from langchain_openai import ChatOpenAI
                                                
                                                llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
                                                
                                                prompt = f"""Extract profile information from this CV/Resume text and return ONLY a valid JSON object.

CV Text:
{analysis.extracted_text}

Return this exact JSON structure (no extra text, no markdown):
{{
    "name": "extracted full name",
    "education_level": "Bachelor's" or "Master's" or "PhD" or "High School",
    "field_of_study": "major/field extracted from education section",
    "gpa": 3.5 or null if not mentioned,
    "skills": "comma separated list of all technical and soft skills",
    "experience_years": total years of work experience as integer,
    "languages": "comma separated languages spoken",
    "achievements": "key achievements, awards, publications, certifications",
    "goals": "inferred career goals based on CV content and trajectory"
}}

Rules:
- Use exact values from CV where possible
- If information is missing, use null or reasonable default
- Keep it concise and accurate
- Return ONLY the JSON, no other text"""
                                                
                                                response = llm.invoke(prompt)
                                                
                                                # Parse JSON
                                                import json
                                                content = response.content.strip()
                                                
                                                # Clean up if it has markdown code blocks
                                                if content.startswith("```json"):
                                                    content = content[7:]
                                                elif content.startswith("```"):
                                                    content = content[3:]
                                                if content.endswith("```"):
                                                    content = content[:-3]
                                                content = content.strip()
                                                
                                                profile_data = json.loads(content)
                                                
                                                # Create profile
                                                st.session_state.profile = UserProfile(
                                                    name=profile_data.get('name', 'Unknown'),
                                                    education_level=profile_data.get('education_level', 'Bachelor\'s'),
                                                    field_of_study=profile_data.get('field_of_study', 'Not specified'),
                                                    gpa=profile_data.get('gpa'),
                                                    skills=profile_data.get('skills', ''),
                                                    experience_years=profile_data.get('experience_years', 0),
                                                    languages=profile_data.get('languages', 'English'),
                                                    achievements=profile_data.get('achievements', ''),
                                                    goals=profile_data.get('goals', '')
                                                )
                                                
                                                st.success("✅ Profile auto-filled from CV!")
                                                st.balloons()

                                                col_action1, col_action2 = st.columns(2)
                                                with col_action1:
                                                    if st.button("📝 Review Profile", use_container_width=True):
                                                        st.info("👉 Go to 'Your Profile' tab")
                                                with col_action2:
                                                    if st.button("🚀 Start Batch Match", type="primary", use_container_width=True):
                                                        st.info("👉 Go to 'Check Match' tab")

                                                st.rerun() 
                                                
                                            except json.JSONDecodeError as e:
                                                st.error(f"Failed to parse AI response: {str(e)}")
                                                st.write("AI Response:", response.content[:500])
                                            except Exception as e:
                                                st.error(f"Failed to extract profile: {str(e)}")
                            
                            # Extract profile information if we have a profile (enhancement suggestions)
                            if st.session_state.profile:
                                st.divider()
                                st.subheader("🔄 Profile Enhancement Suggestions")
                                
                                with st.spinner("Analyzing how to enhance your profile..."):
                                    try:
                                        profile_suggestions = extract_profile_info_from_text(
                                            analysis.extracted_text,
                                            st.session_state.profile
                                        )
                                        
                                        st.markdown("""
                                        <div class="success-card">
                                            <h4>📈 Profile Enhancement Ideas</h4>
                                        </div>
                                        """, unsafe_allow_html=True)
                                        st.write(profile_suggestions)
                                        
                                        # Option to update profile
                                        if st.button("📝 Go to Profile to Update"):
                                            st.info("Switch to the 'Your Profile' tab to update your information")
                                    except:
                                        pass
                            
                            # Download analysis
                            st.divider()
                            analysis_text = f"""
DOCUMENT ANALYSIS REPORT
========================

Document Type: {analysis.document_type}
Confidence Score: {analysis.confidence_score:.1%}

EXTRACTED TEXT:
{analysis.extracted_text}

SUGGESTIONS:
{analysis.suggestions}

Generated by Opportunity Matching Assistant
"""
                            
                            st.download_button(
                                label="📥 Download Analysis Report",
                                data=analysis_text,
                                file_name=f"document_analysis_{uploaded_file.name}.txt",
                                mime="text/plain"
                            )
                            
                        except Exception as e:
                            st.error(f"❌ Error analyzing document: {str(e)}")
                            st.markdown("""
                            <div class="warning-card">
                                <strong>This could be due to:</strong><br>
                                • Image quality too low<br>
                                • API key issues<br>
                                • Unsupported image format<br>
                                • Network connectivity problems
                            </div>
                            """, unsafe_allow_html=True)
                            
                            with st.expander("Debug Info"):
                                st.write(f"Error type: {type(e).__name__}")
                                st.write(f"Error details: {str(e)}")
    
    else:
        # Instructions when no file uploaded
        st.markdown("""
        <div class="info-card">
            <strong>👆 Upload a document image to get started</strong><br>
            Supported formats: PNG, JPG, JPEG
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📋 Supported Documents")
            st.write("**✅ What works well:**")
            st.write("• CV/Resume (can auto-fill profile)")
            st.write("• Academic transcripts")
            st.write("• Certificates and awards")
            st.write("• Recommendation letters")
            st.write("• Cover letters")
        
        with col2:
            st.subheader("💡 Tips for Best Results")
            st.write("**📸 Image Quality:**")
            st.write("• Use high-quality, clear images")
            st.write("• Ensure good lighting")
            st.write("• Avoid shadows or glare")
            st.write("• Keep text straight and readable")
            st.write("• Use formats: PNG, JPG, JPEG")
        
        st.subheader("🎯 What This Feature Does")
        st.write("• Extracts all text from your document images")
        st.write("• Identifies document types automatically")
        st.write("• Auto-fills profile from CV/Resume")
        st.write("• Suggests profile enhancements")
        st.write("• Saves time on manual data entry")

# TAB 6: Opportunity Database
with tab6:
    st.header("🗄️ Opportunity Database")
    st.markdown("Save and manage opportunities for quick access later.")
    
    # Create sub-tabs for better organization
    db_tab1, db_tab2, db_tab3 = st.tabs(["📥 Add Opportunity", "📚 Browse Database", "🔍 Search"])
    
    # SUB-TAB 1: Add Opportunity
    with db_tab1:
        st.subheader("Add New Opportunity to Database")

        # Add URL extraction option
        st.markdown("**Option 1: Extract from URL**")
        col_url1, col_url2 = st.columns([3, 1])
        with col_url1:
            extract_url = st.text_input("Paste URL to extract opportunity details:", placeholder="https://...")
        with col_url2:
            st.write("")
            st.write("")
            extract_btn = st.button("🔍 Extract", use_container_width=True)

        if extract_btn and extract_url:
            with st.spinner("Extracting opportunity details from URL..."):
                try:
                    from langchain_openai import ChatOpenAI
                    import requests
                    from bs4 import BeautifulSoup

                    # Fetch webpage
                    headers = {'User-Agent': 'Mozilla/5.0'}
                    response = requests.get(extract_url, headers=headers, timeout=10)
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # Extract text
                    for script in soup(["script", "style"]):
                        script.decompose()
                    text = soup.get_text()
                    text = ' '.join(text.split())[:10000]

                    # Use AI to extract structured data
                    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
                    prompt = f"""Extract opportunity details from this webpage text and return ONLY a valid JSON object (no markdown, no code blocks):

{text}

Return JSON with these fields:
- title: opportunity name
- type: one of (Scholarship/Job/Academic Program/Fellowship/Internship/Other)
- description: brief summary
- requirements: eligibility criteria
- deadline: if mentioned, format YYYY-MM-DD
- provider: organization name
- funding: amount if mentioned

Return ONLY the JSON object, nothing else."""

                    result = llm.invoke(prompt)

                    # Clean the response
                    import json
                    import re

                    content = result.content.strip()
                    # Remove markdown code blocks if present
                    content = re.sub(r'^```json\s*', '', content)
                    content = re.sub(r'^```\s*', '', content)
                    content = re.sub(r'\s*```$', '', content)
                    content = content.strip()

                    # Parse JSON
                    extracted_data = json.loads(content)

                    st.success("✅ Extracted! Review below:")
                    st.session_state.extracted_from_url = extracted_data

                    # Display in a nice format
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Title:** {extracted_data.get('title', 'N/A')}")
                        st.write(f"**Type:** {extracted_data.get('type', 'N/A')}")
                        st.write(f"**Provider:** {extracted_data.get('provider', 'N/A')}")
                    with col2:
                        st.write(f"**Deadline:** {extracted_data.get('deadline', 'N/A')}")
                        st.write(f"**Funding:** {extracted_data.get('funding', 'N/A')}")

                    st.write(f"**Description:** {extracted_data.get('description', 'N/A')}")
                    st.write(f"**Requirements:** {extracted_data.get('requirements', 'N/A')}")

                    # Button to save directly
                    if st.button("💾 Save This to Database", use_container_width=True):
                        from opportunities_storage import save_opportunity
                        opp_data = {
                            "title": extracted_data.get('title'),
                            "type": extracted_data.get('type'),
                            "description": extracted_data.get('description'),
                            "requirements": extracted_data.get('requirements'),
                            "deadline": extracted_data.get('deadline'),
                            "provider": extracted_data.get('provider'),
                            "funding": extracted_data.get('funding'),
                            "link": extract_url
                        }
                        if save_opportunity(opp_data):
                            st.success("✅ Saved to database!")
                            st.balloons()
                        else:
                            st.error("Failed to save")
                except Exception as e:
                    st.error(f"Failed to extract: {str(e)}")

        st.divider()
        st.markdown("**Option 2: Manual Entry**")

        with st.form("add_to_database_form"):
            col1, col2 = st.columns([2, 1])

            with col1:
                db_title = st.text_input("Opportunity Title*", key="db_title")

            with col2:
                db_type = st.selectbox(
                    "Type*",
                    ["Scholarship", "Job", "Academic Program", "Fellowship", "Internship", "Other"],
                    key="db_type"
                )

            db_description = st.text_area(
                "Description*",
                height=100,
                key="db_description",
                placeholder="Enter the opportunity description..."
            )

            db_requirements = st.text_area(
                "Requirements*",
                height=100,
                key="db_requirements",
                placeholder="Enter eligibility criteria and requirements..."
            )

            col1, col2, col3 = st.columns(3)
            with col1:
                db_deadline = st.text_input("Deadline (optional)", key="db_deadline", placeholder="YYYY-MM-DD")
            with col2:
                db_provider = st.text_input("Provider (optional)", key="db_provider", placeholder="Organization name")
            with col3:
                db_funding = st.text_input("Funding Amount (optional)", key="db_funding", placeholder="e.g., $10,000")

            db_link = st.text_input("Application Link/Contact (optional)", key="db_link", placeholder="https://...")

            submit_to_db = st.form_submit_button("💾 Save to Database", use_container_width=True)
            
            if submit_to_db:
                if not db_title or not db_description or not db_requirements:
                    st.error("Please fill all required fields marked with *")
                else:
                    from opportunities_storage import save_opportunity
                    
                    opp_data = {
                        "title": db_title,
                        "type": db_type,
                        "description": db_description,
                        "requirements": db_requirements,
                        "deadline": db_deadline if db_deadline else None,
                        "provider": db_provider if db_provider else None,
                        "funding": db_funding if db_funding else None,
                        "link": db_link if db_link else None
                    }
                    
                    if save_opportunity(opp_data):
                        st.success(f"✅ '{db_title}' saved to database!")
                        st.balloons()
                        st.info("👉 Go to 'Browse Database' tab to see all saved opportunities")
                    else:
                        st.error("Failed to save opportunity")
    
    # SUB-TAB 2: Browse Database
    with db_tab2:
        st.subheader("Browse All Opportunities")

        from opportunities_storage import load_all_opportunities, delete_opportunity

        opportunities = load_all_opportunities()

        if not opportunities:
            st.info("📭 No opportunities in database yet. Add some in the 'Add Opportunity' tab!")
        else:
            st.write(f"**{len(opportunities)} opportunities in database:**")

            # Summary stats
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                scholarships = sum(1 for o in opportunities if o.get('type') == 'Scholarship')
                create_metric_card("Scholarships", scholarships)
            with col2:
                jobs = sum(1 for o in opportunities if o.get('type') == 'Job')
                create_metric_card("Jobs", jobs)
            with col3:
                programs = sum(1 for o in opportunities if o.get('type') == 'Academic Program')
                create_metric_card("Programs", programs)
            with col4:
                others = len(opportunities) - scholarships - jobs - programs
                create_metric_card("Others", others)

            st.divider()

            # Create tabs for different opportunity types
            browse_tab1, browse_tab2, browse_tab3, browse_tab4 = st.tabs([
                f"🎓 Scholarships ({scholarships})",
                f"💼 Jobs ({jobs})",
                f"🏫 Programs ({programs})",
                f"📌 All ({len(opportunities)})"
            ])

            # Helper function to display opportunities
            def display_opportunity_card(opp, key_prefix=""):
                with st.expander(f"🎯 {opp.get('title')}", expanded=False):
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.write(f"**Type:** {opp.get('type')}")
                        st.write(f"**Description:** {opp.get('description', 'N/A')}")
                        st.write(f"**Requirements:** {opp.get('requirements', 'N/A')}")

                        if opp.get('deadline'):
                            st.write(f"**Deadline:** {opp['deadline']}")
                        if opp.get('provider'):
                            st.write(f"**Provider:** {opp['provider']}")
                        if opp.get('funding'):
                            st.write(f"**Funding:** {opp['funding']}")
                        if opp.get('link'):
                            st.write(f"**Link:** {opp['link']}")

                        st.caption(f"Added: {opp.get('saved_at', 'Unknown')}")

                    with col2:
                        # Use this opportunity button
                        if st.button("✅ Use for Matching", key=f"{key_prefix}_use_{opp.get('id')}", use_container_width=True):
                            # Pre-fill the extracted data for Tab 2
                            st.session_state.extracted_opportunity_data = {
                                'title': opp.get('title'),
                                'type': opp.get('type'),
                                'description': opp.get('description'),
                                'requirements': opp.get('requirements'),
                                'deadline': opp.get('deadline'),
                                'provider': opp.get('provider'),
                                'funding': opp.get('funding'),
                                'link': opp.get('link')
                            }
                            st.success("✅ Opportunity loaded!")
                            st.info("👉 Go to 'Check Match' tab to evaluate")
                            st.rerun()

                        # Delete button
                        if st.button("🗑️ Delete", key=f"{key_prefix}_delete_{opp.get('id')}", type="secondary", use_container_width=True):
                            if delete_opportunity(opp.get('id')):
                                st.success("Deleted!")
                                st.rerun()
                            else:
                                st.error("Failed to delete")

            # Scholarships Tab
            with browse_tab1:
                scholarship_opps = [o for o in opportunities if o.get('type') == 'Scholarship']
                if scholarship_opps:
                    st.write(f"**{len(scholarship_opps)} scholarships available**")
                    for opp in reversed(scholarship_opps):
                        display_opportunity_card(opp, key_prefix="scholar")
                else:
                    st.info("📭 No scholarships found. Add some in the 'Add Opportunity' tab!")

            # Jobs Tab
            with browse_tab2:
                job_opps = [o for o in opportunities if o.get('type') == 'Job']
                if job_opps:
                    st.write(f"**{len(job_opps)} jobs available**")
                    for opp in reversed(job_opps):
                        display_opportunity_card(opp, key_prefix="job")
                else:
                    st.info("📭 No jobs found. Add some in the 'Add Opportunity' tab!")

            # Programs Tab
            with browse_tab3:
                program_opps = [o for o in opportunities if o.get('type') == 'Academic Program']
                if program_opps:
                    st.write(f"**{len(program_opps)} programs available**")
                    for opp in reversed(program_opps):
                        display_opportunity_card(opp, key_prefix="program")
                else:
                    st.info("📭 No academic programs found. Add some in the 'Add Opportunity' tab!")

            # All Tab
            with browse_tab4:
                st.write(f"**Showing all {len(opportunities)} opportunities (newest first)**")
                for opp in reversed(opportunities):
                    display_opportunity_card(opp, key_prefix="all")
    
    # SUB-TAB 3: Search
    with db_tab3:
        st.subheader("Search Opportunities")
        
        from opportunities_storage import search_opportunities
        
        search_query = st.text_input(
            "Search by title or type", 
            placeholder="e.g., Fulbright, Scholarship, Job",
            help="Search for opportunities by keywords in title or type"
        )
        
        if search_query:
            results = search_opportunities(search_query)
            
            if results:
                st.success(f"Found {len(results)} matching opportunities")
                
                for opp in results:
                    with st.expander(f"🎯 {opp.get('title')}", expanded=True):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.write(f"**Type:** {opp.get('type')}")
                            
                            # Show truncated description
                            description = opp.get('description', 'N/A')
                            if len(description) > 200:
                                st.write(f"**Description:** {description[:200]}...")
                            else:
                                st.write(f"**Description:** {description}")
                            
                            # Show key info
                            if opp.get('deadline'):
                                st.write(f"**Deadline:** {opp['deadline']}")
                            if opp.get('provider'):
                                st.write(f"**Provider:** {opp['provider']}")
                            if opp.get('funding'):
                                st.write(f"**Funding:** {opp['funding']}")
                        
                        with col2:
                            if st.button("✅ Use This", key=f"search_use_{opp.get('id')}", use_container_width=True):
                                st.session_state.extracted_opportunity_data = {
                                    'title': opp.get('title'),
                                    'type': opp.get('type'),
                                    'description': opp.get('description'),
                                    'requirements': opp.get('requirements'),
                                    'deadline': opp.get('deadline'),
                                    'provider': opp.get('provider'),
                                    'funding': opp.get('funding'),
                                    'link': opp.get('link')
                                }
                                st.success("✅ Loaded!")
                                st.info("👉 Go to 'Check Match'")
                                st.rerun()  # FIXED: Added rerun to refresh the form
                            
                            # View full details button
                            if st.button("📄 Full Details", key=f"search_details_{opp.get('id')}", use_container_width=True):
                                st.write("**Full Requirements:**")
                                st.write(opp.get('requirements', 'N/A'))
                                if opp.get('link'):
                                    st.write(f"**Link:** {opp['link']}")
            else:
                st.warning("No opportunities found matching your search")
                st.info("Try different keywords like: scholarship, job, fellowship, internship")
        else:
            st.info("💡 Enter a search term to find opportunities in the database")
            st.markdown("""
            **Search tips:**
            - Search by opportunity name (e.g., "Fulbright")
            - Search by type (e.g., "Scholarship", "Job")
            - Search by keywords in the title
            """)

# TAB 7: AI Strategy - Multi-Agent AI System
with tab7:
    st.header("🤖 AI Strategy & Intelligence")
    st.markdown("Harness the power of multiple AI agents working together to optimize your profile and application strategy.")

    if not st.session_state.profile:
        st.markdown("""
        <div class="warning-card">
            <strong>⚠️ Profile Required</strong><br>
            Please create your profile first in the 'Your Profile' tab to access AI Strategy features.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="success-card">
            <strong>✅ Profile Loaded</strong><br>
            Ready to analyze: <strong>{st.session_state.profile.name}</strong>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # Explanation of Multi-Agent System
        with st.expander("📖 How the Multi-Agent AI System Works"):
            st.markdown("""
            Our system uses **4 specialized AI agents** that work in parallel to provide comprehensive insights:

            1. **🔍 Profile Optimizer Agent**
               - Deep analysis of your strengths and weaknesses
               - Identifies quick wins and critical gaps
               - Provides personalized improvement recommendations

            2. **🎯 Opportunity Scout Agent**
               - Generates targeted search strategies
               - Identifies optimal platforms and filters
               - Recommends best timing for applications

            3. **📋 Application Strategist Agent**
               - Prioritizes applications by success probability
               - Estimates time investment for each opportunity
               - Creates customized application roadmap

            4. **🎭 Orchestrator Agent**
               - Coordinates all agents to run in parallel
               - Synthesizes results into actionable plan
               - Calculates overall success metrics

            **Result:** A unified action plan that maximizes your chances of success!
            """)

        # Main Action Button
        st.subheader("🚀 Run Complete AI Analysis")

        col_info, col_btn = st.columns([2, 1])

        with col_info:
            st.info("This will run all AI agents in parallel to analyze your profile, find opportunities, and create an application strategy. Takes ~30-60 seconds.")

        with col_btn:
            run_analysis = st.button("🤖 Run AI Analysis", type="primary", use_container_width=True)

        if run_analysis:
            # Load opportunities for analysis
            from opportunities_storage import load_all_opportunities
            all_opps = load_all_opportunities()

            if not all_opps:
                st.warning("⚠️ No opportunities in database. Add some scholarships first!")
            else:
                with st.spinner("🤖 AI agents are working... This may take 30-60 seconds"):
                    try:
                        # Run batch match to get scored opportunities
                        from ai_evaluator import evaluate_match
                        batch_results = []

                        # Evaluate top 10 opportunities for strategy
                        for opp_data in all_opps[:10]:
                            try:
                                from models import Opportunity
                                opportunity = Opportunity(
                                    title=opp_data.get('title', ''),
                                    opp_type=opp_data.get('type', 'Scholarship'),
                                    description=opp_data.get('description', ''),
                                    requirements=opp_data.get('requirements', ''),
                                    deadline=opp_data.get('deadline')
                                )

                                result = evaluate_match(st.session_state.profile, opportunity)

                                batch_results.append({
                                    'opportunity': opportunity,
                                    'result': result,
                                    'opp_data': opp_data,
                                    'score': result.compatibility_score
                                })
                            except:
                                pass

                        # Sort by score
                        batch_results.sort(key=lambda x: x['score'], reverse=True)

                        # Run orchestrator with results
                        import asyncio
                        from agents.orchestrator import orchestrate_ai_analysis

                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        unified_plan = loop.run_until_complete(
                            orchestrate_ai_analysis(st.session_state.profile, batch_results)
                        )

                        st.success("✅ AI Analysis Complete!")
                        st.markdown("---")

                        # Display Results
                        st.subheader("📊 Unified Action Plan")

                        # Key Metrics
                        col_m1, col_m2, col_m3 = st.columns(3)

                        with col_m1:
                            create_metric_card("Success Probability", f"{unified_plan.success_probability:.1%}")

                        with col_m2:
                            create_metric_card("Time Investment", f"{unified_plan.time_investment_hours} hours")

                        with col_m3:
                            create_metric_card("Priority Actions", str(len(unified_plan.priority_actions)))

                        st.markdown("---")

                        # Priority Actions
                        st.subheader("🎯 Top Priority Actions")
                        for idx, action in enumerate(unified_plan.priority_actions, 1):
                            st.markdown(f"{idx}. {action}")

                        st.markdown("---")

                        # Recommended Next Steps
                        st.subheader("📋 Recommended Next Steps")
                        for idx, step in enumerate(unified_plan.recommended_next_steps, 1):
                            st.markdown(f"{idx}. {step}")

                        st.markdown("---")

                        # Detailed Agent Results
                        st.subheader("🔍 Detailed Agent Analysis")

                        # Profile Optimization Results
                        if unified_plan.profile_optimization:
                            with st.expander("🔍 Profile Optimizer Agent Results", expanded=True):
                                prof_opt = unified_plan.profile_optimization

                                col1, col2 = st.columns(2)

                                with col1:
                                    st.markdown("### 💪 Quick Wins")
                                    if 'quick_wins' in prof_opt and prof_opt['quick_wins']:
                                        for qw in prof_opt['quick_wins'][:5]:
                                            st.markdown(f"- **{qw.get('action', 'N/A')}** (Impact: {qw.get('impact_score', 0)}/10)")
                                            st.caption(qw.get('rationale', ''))

                                    st.markdown("### 🌟 Unique Strengths")
                                    if 'unique_strengths' in prof_opt:
                                        for strength in prof_opt['unique_strengths'][:3]:
                                            st.success(f"✓ {strength}")

                                with col2:
                                    st.markdown("### ⚠️ Critical Gaps")
                                    if 'critical_gaps' in prof_opt and prof_opt['critical_gaps']:
                                        for gap in prof_opt['critical_gaps'][:5]:
                                            st.markdown(f"- **{gap.get('area', 'N/A')}** (Severity: {gap.get('severity', 0)}/10)")
                                            st.caption(gap.get('description', ''))

                                    st.markdown("### 📊 Profile Strength")
                                    if 'profile_strength_score' in prof_opt:
                                        score = prof_opt['profile_strength_score']
                                        st.metric("Overall Score", f"{score}/10")

                        # Search Strategies
                        if unified_plan.search_strategies:
                            with st.expander("🎯 Opportunity Scout Agent Results"):
                                search_strat = unified_plan.search_strategies

                                if 'recommended_platforms' in search_strat:
                                    st.markdown("### 🌐 Recommended Platforms")
                                    for platform in search_strat['recommended_platforms'][:5]:
                                        st.markdown(f"**{platform.get('name', 'N/A')}** - {platform.get('rationale', '')}")

                                if 'search_keywords' in search_strat:
                                    st.markdown("### 🔑 Search Keywords")
                                    st.write(", ".join(search_strat['search_keywords'][:10]))

                        # Application Strategy
                        if unified_plan.application_strategy:
                            with st.expander("📋 Application Strategist Agent Results"):
                                app_strat = unified_plan.application_strategy

                                if 'prioritized_applications' in app_strat and app_strat['prioritized_applications']:
                                    st.markdown("### 📊 Prioritized Applications")
                                    for idx, app in enumerate(app_strat['prioritized_applications'][:5], 1):
                                        col_a, col_b, col_c = st.columns([2, 1, 1])

                                        with col_a:
                                            st.markdown(f"**{idx}. {app.get('opportunity_title', 'N/A')}**")
                                            st.caption(app.get('strategy_summary', ''))

                                        with col_b:
                                            st.metric("Success Rate", f"{app.get('success_probability', 0):.0%}")

                                        with col_c:
                                            priority = app.get('priority_level', 'Medium')
                                            color = "🔴" if priority == "High" else "🟡" if priority == "Medium" else "🟢"
                                            st.metric("Priority", f"{color} {priority}")

                    except Exception as e:
                        st.error(f"Error running AI analysis: {str(e)}")
                        with st.expander("Debug Info"):
                            import traceback
                            st.code(traceback.format_exc())

# Footer with enhanced styling
st.divider()
st.markdown("""
<div class="custom-footer">
    <strong>🎯 Opportunity Matching Assistant</strong><br>
    Built with Streamlit and OpenAI • Made for finding your perfect opportunities<br>
    <small>Enhance your applications with AI-powered insights</small>
</div>
""", unsafe_allow_html=True)