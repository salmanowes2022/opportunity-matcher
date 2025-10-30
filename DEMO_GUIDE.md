# Opportunity Matcher - Demo Guide

## Quick Start for Demo

### Step 1: Run the Application
```bash
streamlit run main.py
```
The app will open at: http://localhost:8501

---

## 🆕 NEW! Enhanced CV-to-Batch-Match Workflow

### The Improved User Journey:
1. **Upload CV** → AI extracts profile information
2. **Auto-fill Profile** → Review and edit extracted data
3. **Batch Match** → Evaluate against ALL scholarships in database
4. **View Ranked Results** → See best matches first with detailed feedback

This is now the **recommended demo flow** as it showcases the most powerful features!

---

## Demo Workflow Options

### OPTION A: Quick Demo (5 Minutes) - Original Flow

### 1. Load Demo Profile (30 seconds)
**Tab:** 📝 Your Profile

1. Click the **"🚀 Load Demo Profile"** button at the top
2. Profile will auto-populate with sample data:
   - Name: Sarah Ahmed
   - Education: Master's in Computer Science
   - GPA: 3.8
   - Experience: 3 years
   - Skills: Python, ML, NLP, etc.
   - Strong achievements and clear goals

3. Scroll down to see the profile summary with metrics

---

### 2. Upload Scholarship Poster (1 minute)
**Tab:** 🔍 Check Match

1. Click on "📤 Upload an Opportunity Image (Optional)"
2. Upload a scholarship/opportunity poster image (PNG, JPG, JPEG)
3. Wait 10-15 seconds for AI extraction
4. Watch as the form auto-fills with:
   - Title
   - Type (Scholarship/Job/Program)
   - Description
   - Requirements
   - Deadline
   - Additional info (funding, location, link)

**Demo Tip:** Use a clear, high-quality image of a scholarship poster for best results

---

### 3. Evaluate Match with AI (1 minute)
**Still in Tab:** 🔍 Check Match

1. Review the extracted opportunity details
2. Click **"🎯 Evaluate Match"** button
3. AI will analyze profile vs opportunity
4. Results display:
   - **Compatibility Score** (0.0 - 1.0) with color indicator
     - Green (>0.7): Strong match
     - Yellow (0.4-0.7): Moderate match
     - Red (<0.4): Weak match
   - **Strengths:** What makes you a good candidate
   - **Gaps:** Areas for improvement
   - **Recommendations:** Actionable advice

5. Scroll down and click **"💾 Save to History"**

---

### 4. Generate Application Materials (1 minute)
**Tab:** ✍️ Generate Materials

1. Select material type:
   - Cover Letter
   - Personal Statement
   - Motivation Letter

2. Adjust target word count (default: 500)

3. Click **"✍️ Generate Material"**

4. AI generates personalized content with:
   - Professionally written material
   - Key points highlighted
   - Suggestions for improvement
   - Word count

5. Click **"⬇️ Download"** to save as text file

---

### OPTION B: Full CV-to-Batch-Match Demo (7 Minutes) - 🆕 RECOMMENDED!

This showcases the most impressive features and real-world use case.

#### 1. Upload CV and Auto-fill Profile (2 minutes)
**Tab:** 📄 Upload Documents

1. Prepare a sample CV image (PNG/JPG of a resume)
2. Upload the CV image
3. Select document type: "CV/Resume" (or let AI auto-detect)
4. Click **"🔍 Analyze Document"**
5. Wait 15-20 seconds for AI to extract text
6. Review extracted information
7. Click **"⚡ Auto-fill Profile"** button
8. Profile is automatically created from CV!
9. Go to **📝 Your Profile** tab to review

**Demo Tip:** Use a well-formatted CV with clear sections (Education, Experience, Skills, etc.)

---

#### 2. Batch Match Against All Scholarships (3 minutes)
**Tab:** 🔍 Check Match

1. Scroll down to **"🎯 Batch Match - Evaluate All Scholarships"** section
2. Click **"🚀 Match Against All Scholarships"** button
3. Watch progress bar as AI evaluates each scholarship
   - Currently evaluates 11 scholarships in database
   - Takes ~30-60 seconds (depends on API speed)
4. View comprehensive results:
   - **Summary Metrics:** Total evaluated, strong/moderate/low matches, average score
   - **Ranked Results:** All scholarships sorted by compatibility score (best first)
   - **Color-coded:** 🟢 Strong (≥70%), 🟡 Moderate (40-69%), 🔴 Weak (<40%)

---

#### 3. Review Top Matches (2 minutes)
**Still in Batch Results Section:**

For each scholarship, you see:
- **Compatibility Score** with visual indicator
- **Provider & Deadline** information
- **Funding details**
- **Your Strengths** for this opportunity
- **Gaps to Address** specific to requirements
- **Personalized Recommendation** from AI
- **Apply Link** (if available)
- **Full description & requirements** (expandable)

Top 3 matches expand automatically for quick review!

**Demo Highlight:** Point out how different scholarships get different scores based on profile fit.

---

#### 4. Generate Materials for Best Match (Optional - 1 minute)
**Tab:** ✍️ Generate Materials

1. Note the title of your top match
2. Go to Generate Materials tab
3. Enter the scholarship details
4. Generate cover letter or personal statement
5. Download and review

---

### OPTION C: Quick Demo with Demo Profile (5 Minutes) - Original Flow

---

### 5. Save to Database (30 seconds)
**Tab:** 🗄️ Opportunity Database

1. Go to **"Add New Opportunity"** sub-tab
2. If you loaded an opportunity via image, it's already in the form
3. Click **"💾 Save to Database"**
4. Switch to **"Browse Database"** sub-tab
5. See all saved opportunities
6. Use search to filter by title or type
7. Click **"📋 Load to Match"** to re-evaluate

---

## Key Features to Highlight

### 🎯 Core Strengths
1. **One-Click Demo Profile** - Fast setup for testing
2. **AI-Powered Image Extraction** - Upload flyers, get structured data
3. **Intelligent Matching** - GPT-4 evaluates compatibility with detailed feedback
4. **Material Generation** - Creates professional cover letters and statements
5. **Document Analysis** - Upload CVs/transcripts for auto-profile filling
6. **Persistent Database** - Save and search opportunities

### 🤖 AI Technologies
- **OpenAI GPT-4o-mini:** Profile matching & content generation
- **Google Gemini 1.5 Flash:** Image analysis & data extraction
- **LangChain:** LLM orchestration with structured outputs

### 💡 User Experience
- Clean, modern UI with custom CSS
- Color-coded compatibility indicators
- PDF export for evaluations and profiles
- Session-based history tracking
- Real-time validation and error handling

---

## Demo Tips

### For Best Results:
1. **Image Quality:** Use clear, well-lit photos of opportunity posters
2. **Profile Completeness:** Demo profile is comprehensive - show how detail matters
3. **Multiple Opportunities:** Demo 2-3 different opportunities to show variety in scoring
4. **Material Generation:** Show different material types (cover letter vs statement)

### Common Questions to Address:
**Q: How accurate is the matching?**
A: Uses GPT-4 with career advisor prompts - comparable to human advisor

**Q: Can it work with any opportunity?**
A: Yes! Scholarships, jobs, programs, fellowships, internships

**Q: What about privacy?**
A: Profile data stays in session (unless saved). Images processed via API only

**Q: Cost?**
A: Depends on OpenAI/Gemini API usage - approximately $0.01-0.05 per evaluation

---

## Troubleshooting

### If API Keys Are Missing:
- Warning banner appears at top of app
- Click expander for instructions to get keys
- Add to `.env` file in project root

### If Image Extraction Fails:
- Check image clarity and text visibility
- Try different image format (PNG vs JPG)
- Fall back to manual entry

### If Evaluation Is Slow:
- Normal processing time: 5-10 seconds
- Depends on API response times
- Show spinner indicates it's working

---

## Technical Stack (For Technical Audience)

```
Frontend:  Streamlit (Python web framework)
AI/ML:     OpenAI GPT-4o-mini, Google Gemini 1.5 Flash
Framework: LangChain (LLM orchestration)
Database:  JSON (simple persistence)
PDFs:      ReportLab
Validation: Pydantic models
```

---

## After Demo - Next Steps

### Potential Improvements:
1. **Database:** Upgrade from JSON to PostgreSQL/MongoDB
2. **Authentication:** Add user accounts and login
3. **History:** Persist evaluation history to database
4. **Analytics:** Track success rates and trends
5. **Batch Processing:** Evaluate multiple opportunities at once
6. **Email Alerts:** Notify when new opportunities match profile
7. **Collaborative:** Share profiles with advisors/mentors

### Deployment Options:
- **Streamlit Cloud:** Free hosting (streamlit.io/cloud)
- **Heroku/Railway:** Simple PaaS deployment
- **Docker:** Containerized for any cloud provider
- **AWS/GCP/Azure:** Enterprise-grade deployment

---

## Demo Checklist

Before presenting:
- [ ] API keys are configured in `.env`
- [ ] App runs without errors: `streamlit run main.py`
- [ ] Sample scholarship poster image ready
- [ ] Demo profile loads correctly
- [ ] Internet connection stable (for API calls)
- [ ] Browser window sized appropriately
- [ ] Clear browser cache if needed

During demo:
- [ ] Show demo profile load feature
- [ ] Upload and extract from image
- [ ] Evaluate match (show score/feedback)
- [ ] Generate at least one application material
- [ ] Save to database and search
- [ ] Highlight error handling (API warnings)

---

## Contact & Support

**Repository:** [Add your GitHub link]
**Questions:** [Add your email]
**Documentation:** See README.md for full details

---

Good luck with your demo! 🚀
