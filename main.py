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

# Apply custom CSS styling
apply_custom_css()

# Title and description with enhanced styling
st.markdown('<h1 class="custom-title">Opportunity Matching Assistant</h1>', unsafe_allow_html=True)
st.markdown('<p class="custom-subtitle">AI-powered tool to evaluate how well you match scholarships, jobs, and programs</p>', unsafe_allow_html=True)

# Initialize session state
if 'profile' not in st.session_state:
    st.session_state.profile = None
if 'evaluation_history' not in st.session_state:
    st.session_state.evaluation_history = []

# Create all tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📝 Your Profile", 
    "🔍 Check Match", 
    "📊 History", 
    "✍️ Generate Materials", 
    "📄 Upload Documents"
])

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

    # Display saved profile with enhanced styling
    if st.session_state.profile:
        st.divider()
        st.subheader("Your Saved Profile")
        
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

# TAB 2: Match Evaluation
# TAB 2: Match Evaluation
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
        
        # Form for opportunity input
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
            
            # Submit button - ONLY this button should be in the form
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
                            
                            # Check if we got a valid result (not an error fallback)
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
                                
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    # Generate evaluation PDF
                                    try:
                                        from pdf_generator import generate_evaluation_pdf
                                        pdf_buffer = generate_evaluation_pdf(st.session_state.profile, opportunity, result)
                                        
                                        st.download_button(
                                            label="📄 Download PDF Report",
                                            data=pdf_buffer.getvalue(),
                                            file_name=f"evaluation_report_{opportunity.title.replace(' ', '_')}.pdf",
                                            mime="application/pdf",
                                            help="Download a professional PDF report of this evaluation"
                                        )
                                    except Exception as e:
                                        st.button(
                                            "📄 PDF Export",
                                            disabled=True,
                                            help="PDF export requires reportlab library"
                                        )
                                
                                with col2:
                                    # Link to materials generation
                                    if st.button("✍️ Generate Application Materials"):
                                        st.info("💡 Switch to the 'Generate Materials' tab to create personalized cover letters and personal statements for this opportunity!")
                                
                                with col3:
                                    # Save evaluation
                                    if st.button("💾 Save to History"):
                                        evaluation_record = {
                                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                            "opportunity": opportunity,
                                            "result": result
                                        }
                                        st.session_state.evaluation_history.append(evaluation_record)
                                        st.success("✅ Evaluation saved to history!")
                                        st.rerun()
                                
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
                            
                            # Debug information (only show if needed)
                            with st.expander("🐛 Debug Information", expanded=False):
                                st.write(f"Error type: {type(e).__name__}")
                                st.write(f"Error message: {str(e)}")
                                st.write(f"API key status: {'Set' if api_key else 'Not set'}")
                                st.write(f"API key format: {'Valid' if api_key and api_key.startswith(('sk-', 'sk-proj-')) else 'Invalid'}")
        
        # Quick API test section (for debugging)
        if st.session_state.profile:
            with st.expander("🔧 API Connection Test", expanded=False):
                st.write("Use this to test if your OpenAI API key is working:")
                
                if st.button("Test API Connection"):
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
                if st.session_state.evaluation_history:
                    use_previous = st.checkbox("Use previous opportunity")
                    if use_previous:
                        selected_opp = st.selectbox(
                            "Select Opportunity",
                            range(len(st.session_state.evaluation_history)),
                            format_func=lambda x: st.session_state.evaluation_history[x]['opportunity'].title
                        )
            
            # Opportunity details (can reuse from previous or enter new)
            if not use_previous:
                st.subheader("Opportunity Details")
                opp_title = st.text_input("Opportunity Title")
                opp_type = st.selectbox("Type", ["Scholarship", "Job", "Academic Program", "Fellowship"])
                opp_description = st.text_area("Description", height=100)
                opp_requirements = st.text_area("Requirements", height=100)
            
            generate_material = st.form_submit_button("✍️ Generate Material", use_container_width=True)
            
            if generate_material:
                # Get opportunity data
                if use_previous and st.session_state.evaluation_history:
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
                        
                        # Display results with enhanced styling
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
                        
                        # Download options
                        st.divider()
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.download_button(
                                label=f"📄 Download {material_type.replace('_', ' ').title()} (TXT)",
                                data=result.content,
                                file_name=f"{material_type}_{opportunity.title.replace(' ', '_')}.txt",
                                mime="text/plain"
                            )
                        
                        with col2:
                            st.info("💡 Tip: Copy the content and paste into your preferred document editor for further customization")
                        
                    except Exception as e:
                        st.error(f"❌ Error generating material: {str(e)}")

# TAB 5: Document Upload and Analysis
with tab5:
    st.header("Upload and Analyze Documents")
    st.markdown("Upload images of your CV, transcripts, certificates, or other documents to extract information automatically.")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose a document image",
        type=['png', 'jpg', 'jpeg'],
        help="Upload clear, high-quality images for best results"
    )
    
    if uploaded_file is not None:
        # Display the uploaded image
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📄 Uploaded Document")
            st.image(uploaded_file, caption="Uploaded Document", use_column_width=True)
            
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
                            from image_analyzer import analyze_document_image, extract_profile_info_from_text
                            
                            # Read image bytes
                            image_bytes = uploaded_file.getvalue()
                            
                            # Analyze the document
                            doc_hint = None if doc_type_hint == "Auto-detect" else doc_type_hint
                            analysis = analyze_document_image(image_bytes, doc_hint)
                            
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
                            
                            # Extract profile information if we have a profile
                            if st.session_state.profile:
                                st.divider()
                                st.subheader("🔄 Profile Enhancement Suggestions")
                                
                                with st.spinner("Analyzing how to enhance your profile..."):
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
                            
                            # Download analysis
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
            st.write("• CV/Resume")
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
        st.write("• Suggests how to use the information")
        st.write("• Helps enhance your existing profile")
        st.write("• Saves time on manual data entry")

# Footer with enhanced styling
st.divider()
st.markdown("""
<div class="custom-footer">
    <strong>🎯 Opportunity Matching Assistant</strong><br>
    Built with Streamlit and OpenAI • Made for finding your perfect opportunities<br>
    <small>Enhance your applications with AI-powered insights</small>
</div>
""", unsafe_allow_html=True)