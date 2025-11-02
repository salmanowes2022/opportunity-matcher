# Missing Features To Add

## Current Status
You have a fully functional **Opportunity Matching Assistant** with:
- ✅ 7 tabs (Profile, Check Match, History, Materials, Upload Documents, Database, AI Strategy)
- ✅ Multi-agent AI system (4 agents working in parallel)
- ✅ CV auto-fill and analysis
- ✅ Beautiful analytics-style results for scholarship matching
- ✅ Web scraper agent (`agents/web_scraper.py`) - READY TO USE!

## 3 Features That Need to Be Added to UI

### 1. URL EXTRACTION FEATURE (Tab 6 - Opportunity Database)

**Location:** Tab 6, Sub-tab 1 "Add Opportunity" (around line 1764 in main.py)

**What to add:** Before the manual form, add this section:

```python
# URL SCRAPING SECTION
st.subheader("🌐 Extract from URL")
st.markdown("Paste a scholarship/job URL and we'll automatically extract all details!")

col_url1, col_url2 = st.columns([3, 1])

with col_url1:
    opportunity_url = st.text_input(
        "Opportunity URL",
        placeholder="https://example.com/scholarship-page",
        help="Paste the URL of a scholarship, job, or program page"
    )

with col_url2:
    st.write("")  # Spacing
    st.write("")  # Spacing
    extract_btn = st.button("🔍 Extract from URL", use_container_width=True, type="primary")

if extract_btn and opportunity_url:
    with st.spinner("Scraping and analyzing URL..."):
        try:
            from agents.web_scraper import scrape_opportunity_from_url
            scraped_data = scrape_opportunity_from_url(opportunity_url)

            st.success("✅ Successfully extracted data from URL!")

            # Display extracted data
            with st.expander("📋 Extracted Information", expanded=True):
                st.json({
                    "title": scraped_data.title,
                    "type": scraped_data.opp_type,
                    "provider": scraped_data.provider,
                    "deadline": scraped_data.deadline,
                    "funding": scraped_data.funding
                })

            # Auto-save to database
            from opportunities_storage import save_opportunity
            opp_dict = {
                "title": scraped_data.title,
                "type": scraped_data.opp_type,
                "description": scraped_data.description,
                "requirements": scraped_data.requirements,
                "deadline": scraped_data.deadline or "Not specified",
                "provider": scraped_data.provider or "Not specified",
                "funding": scraped_data.funding or "Not specified",
                "location": scraped_data.location or "Not specified",
                "link": scraped_data.link
            }
            save_opportunity(opp_dict)
            st.success("💾 Automatically saved to database!")
            st.balloons()

        except Exception as e:
            st.error(f"Error extracting from URL: {str(e)}")

st.markdown("---")
st.subheader("📝 Or Add Manually")
```

**Status:** Backend ready (web_scraper.py exists), just needs UI integration

---

###2. SEPARATE OPPORTUNITIES BY TYPE (Tab 6 - Browse Database)

**Location:** Tab 6, Sub-tab 2 "Browse Database" (around line 1850)

**What to change:** Replace the current Browse Database section with tabbed view:

```python
# SUB-TAB 2: Browse Database with Type Separation
with db_tab2:
    st.subheader("Browse Opportunities by Type")

    from opportunities_storage import load_all_opportunities
    all_opps = load_all_opportunities()

    if not all_opps:
        st.info("No opportunities in database yet.")
    else:
        # Separate by type
        scholarships = [o for o in all_opps if o.get('type') == 'Scholarship']
        jobs = [o for o in all_opps if o.get('type') == 'Job']
        programs = [o for o in all_opps if o.get('type') in ['Academic Program', 'Fellowship', 'Internship']]
        other = [o for o in all_opps if o.get('type') not in ['Scholarship', 'Job', 'Academic Program', 'Fellowship', 'Internship']]

        # Create tabs for each type
        type_tab1, type_tab2, type_tab3, type_tab4 = st.tabs([
            f"🎓 Scholarships ({len(scholarships)})",
            f"💼 Jobs ({len(jobs)})",
            f"📚 Programs ({len(programs)})",
            f"📋 Other ({len(other)})"
        ])

        # Function to display opportunities
        def display_opportunities(opps, opp_type):
            if not opps:
                st.info(f"No {opp_type} found in database.")
                return

            for idx, opp in enumerate(opps, 1):
                with st.expander(f"#{idx} - {opp.get('title', 'Untitled')}"):
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.write(f"**Provider:** {opp.get('provider', 'N/A')}")
                        st.write(f"**Deadline:** {opp.get('deadline', 'N/A')}")
                        st.write(f"**Funding:** {opp.get('funding', 'N/A')}")
                        if opp.get('link'):
                            st.markdown(f"[🔗 Link]({opp.get('link')})")
                    with col2:
                        if st.button("🗑️ Delete", key=f"del_{opp_type}_{idx}"):
                            # Delete logic here
                            pass

        with type_tab1:
            display_opportunities(scholarships, "scholarships")

        with type_tab2:
            display_opportunities(jobs, "jobs")

        with type_tab3:
            display_opportunities(programs, "programs")

        with type_tab4:
            display_opportunities(other, "other opportunities")
```

---

### 3. AUTO-FILL MATERIALS TAB (Tab 4 - Generate Materials)

**Location:** Tab 4 "Generate Materials" (around line 1201)

**What to add:** At the very beginning of Tab 4, before the form:

```python
# TAB 4: Generate Materials
with tab4:
    st.header("Generate Application Materials")

    # CHECK IF OPPORTUNITY WAS SELECTED FROM MATCHING
    if 'selected_opportunity_for_materials' in st.session_state and st.session_state.selected_opportunity_for_materials:
        selected_opp = st.session_state.selected_opportunity_for_materials
        selected_opp_data = st.session_state.get('selected_opportunity_data', {})

        st.markdown("""
        <div class="success-card">
            <strong>✅ Opportunity Selected!</strong><br>
            Generating materials for: <strong>{}</strong>
        </div>
        """.format(selected_opp.title), unsafe_allow_html=True)

        # Pre-filled opportunity details (read-only)
        with st.expander("📋 Opportunity Details", expanded=True):
            st.write(f"**Title:** {selected_opp.title}")
            st.write(f"**Type:** {selected_opp.opp_type}")
            st.write(f"**Description:** {selected_opp.description}")
            st.write(f"**Requirements:** {selected_opp.requirements}")

        # Material type selection
        material_type = st.selectbox(
            "What would you like to generate?",
            ["Cover Letter", "Statement of Purpose / Personal Statement", "Both"]
        )

        # Generate button (no form needed!)
        if st.button("✍️ Generate Materials", type="primary", use_container_width=True):
            with st.spinner("Generating your application materials..."):
                try:
                    from material_generator import generate_cover_letter, generate_statement_of_purpose

                    if material_type in ["Cover Letter", "Both"]:
                        cover_letter = generate_cover_letter(
                            st.session_state.profile,
                            selected_opp
                        )
                        st.subheader("📄 Cover Letter")
                        st.write(cover_letter)
                        st.download_button(
                            "📥 Download Cover Letter",
                            data=cover_letter,
                            file_name=f"cover_letter_{selected_opp.title.replace(' ', '_')}.txt",
                            mime="text/plain"
                        )

                    if material_type in ["Statement of Purpose / Personal Statement", "Both"]:
                        sop = generate_statement_of_purpose(
                            st.session_state.profile,
                            selected_opp
                        )
                        st.subheader("📜 Statement of Purpose")
                        st.write(sop)
                        st.download_button(
                            "📥 Download Statement",
                            data=sop,
                            file_name=f"statement_{selected_opp.title.replace(' ', '_')}.txt",
                            mime="text/plain"
                        )

                    st.success("✅ Materials generated successfully!")

                except Exception as e:
                    st.error(f"Error generating materials: {str(e)}")

        st.markdown("---")
        st.markdown("### Or enter opportunity details manually below")

    # ORIGINAL MANUAL FORM CONTINUES HERE...
    else:
        st.info("💡 Tip: Match with a scholarship first in 'Check Match' tab, then come here to auto-generate materials!")
```

---

## How to Implement

1. **Option A - Manual Implementation:**
   - Open main.py in your editor
   - Find each location mentioned above
   - Copy-paste the code snippets
   - Test each feature

2. **Option B - Continue Session:**
   - Start a new conversation session
   - Share this document
   - Ask me to implement these 3 features one by one

3. **Option C - Git Restore:**
   - Check if there's an older commit that had these features
   - Use `git log --all --oneline` to find it
   - Restore that version

## Testing Checklist

After adding all features:

- [ ] Tab 6: Paste a scholarship URL and click "Extract from URL" - should scrape and save
- [ ] Tab 6: Browse Database shows separate tabs for Scholarships/Jobs/Programs
- [ ] Tab 2: Match with a scholarship, click "Generate Materials", should auto-fill Tab 4
- [ ] Tab 4: Should show pre-filled opportunity details when coming from matching

## Notes

- The `web_scraper.py` backend is complete and tested
- All dependencies are installed (BeautifulSoup, requests)
- The app is currently at commit `b6e655e` with multi-agent system
- Current line count: ~2150 lines in main.py

Good luck! These features will make the app complete! 🚀
