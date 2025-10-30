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
    st.session_state.evaluation_history = []
if 'extracted_opportunity_data' not in st.session_state:
    st.session_state.extracted_opportunity_data = {}
if 'selected_opportunity_for_materials' not in st.session_state:
    st.session_state.selected_opportunity_for_materials = None
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 0

# Create all tabs
tab1, tab2, tab3, tab4, tab5,tab6 = st.tabs([
    "📝 Your Profile",
    "🔍 Check Match", 
    "📊 History", 
    "✍️ Generate Materials", 
    "📄 Upload Documents",
    "🗄️ Opportunity Database" 
])

# TAB 1: Profile Creation
with tab1:
    st.header("Create Your Profile")
    st.markdown("Fill out your information once, then use it to evaluate multiple opportunities.")

    # Quick action buttons
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

        # BATCH MATCHING SECTION - Match against all scholarships in database
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
            with st.expander(f"🎯 {record['opportunity'].title} - {record['timestamp']}", expanded=False):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"**Type:** {record['opportunity'].opp_type}")
                    if record['opportunity'].deadline:
                        st.write(f"**Deadline:** {record['opportunity'].deadline}")
                    
                    # Mini status indicator
                    score = record['result'].compatibility_score
                    if score >= 0.7:
                        st.success(f"🎯 Strong Match ({score:.1%})")
                    elif score >= 0.5:
                        st.info(f"👍 Good Match ({score:.1%})")
                    else:
                        st.warning(f"⚠️ Partial Match ({score:.1%})")
                
                with col2:
                    st.write("**Recommendation:**")
                    st.write(record['result'].recommendation[:100] + "..." if len(record['result'].recommendation) > 100 else record['result'].recommendation)
                
                with col3:
                    # PDF Export for individual evaluation
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
                            key=f"pdf_{i}"
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

        # Check if opportunity was selected from batch match
        if st.session_state.selected_opportunity_for_materials:
            st.success(f"✅ Loaded: {st.session_state.selected_opportunity_for_materials.title}")

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
                # Use opportunity from history or enter new one
                use_previous = False
                use_selected = False

                if st.session_state.selected_opportunity_for_materials:
                    use_selected = st.checkbox("Use selected opportunity", value=True)

                if not use_selected and st.session_state.evaluation_history:
                    use_previous = st.checkbox("Use previous opportunity")
                    if use_previous:
                        selected_opp = st.selectbox(
                            "Select Opportunity",
                            range(len(st.session_state.evaluation_history)),
                            format_func=lambda x: st.session_state.evaluation_history[x]['opportunity'].title
                        )

            # Opportunity details
            if use_selected and st.session_state.selected_opportunity_for_materials:
                st.subheader("Selected Opportunity")
                st.write(f"**Title:** {st.session_state.selected_opportunity_for_materials.title}")
                st.write(f"**Type:** {st.session_state.selected_opportunity_for_materials.opp_type}")
                with st.expander("View Details"):
                    st.write(st.session_state.selected_opportunity_for_materials.description)
                    st.write(st.session_state.selected_opportunity_for_materials.requirements)
            elif not use_previous:
                st.subheader("Opportunity Details")
                opp_title = st.text_input("Opportunity Title")
                opp_type = st.selectbox("Type", ["Scholarship", "Job", "Academic Program", "Fellowship"])
                opp_description = st.text_area("Description", height=100)
                opp_requirements = st.text_area("Requirements", height=100)
            
            generate_material = st.form_submit_button("✍️ Generate Material", use_container_width=True)
            
            if generate_material:
                # Get opportunity data
                if use_selected and st.session_state.selected_opportunity_for_materials:
                    opportunity = st.session_state.selected_opportunity_for_materials
                elif use_previous and st.session_state.evaluation_history:
                    opportunity = st.session_state.evaluation_history[selected_opp]['opportunity']
                else:
                    if not all([opp_title, opp_description, opp_requirements]):
                        st.error("Please fill all opportunity fields")
                        st.stop()

                    opportunity = Opportunity(
                        title=opp_title,
                        opp_type=opp_type,
                        description=opp_description,
                        requirements=opp_requirements
                    )
                
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
                        
                        # Download option
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
            
            # Display opportunities
            for opp in reversed(opportunities):  # Show newest first
                with st.expander(f"🎯 {opp.get('title')} ({opp.get('type')})", expanded=False):
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
                        if st.button("✅ Use for Matching", key=f"use_{opp.get('id')}", use_container_width=True):
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
                            st.rerun()  # FIXED: Added rerun to refresh the form
                        
                        # Delete button
                        if st.button("🗑️ Delete", key=f"delete_{opp.get('id')}", type="secondary", use_container_width=True):
                            if delete_opportunity(opp.get('id')):
                                st.success("Deleted!")
                                st.rerun()
                            else:
                                st.error("Failed to delete")
    
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
# Footer with enhanced styling
st.divider()
st.markdown("""
<div class="custom-footer">
    <strong>🎯 Opportunity Matching Assistant</strong><br>
    Built with Streamlit and OpenAI • Made for finding your perfect opportunities<br>
    <small>Enhance your applications with AI-powered insights</small>
</div>
""", unsafe_allow_html=True)