"""
app.py
------
AI Resume Analyzer - Streamlit entry point (thin controller).

Final Year Project | Muhammad Zeeshan Ahmad (2022-ag-7939)
University of Agriculture Faisalabad | IT-610

This file only handles input collection and delegates all analysis to
``analyzer.pipeline.ResumeAnalysisPipeline`` and all rendering to
``visualizations.dashboard``. The heavy NLP models are cached so they load
only once per session.
"""

from __future__ import annotations
import streamlit as st

from analyzer.pipeline import ResumeAnalysisPipeline
from data.skills_db import ROLE_NAMES
from utils import pdf_parser, docx_parser
from visualizations import dashboard

st.set_page_config(page_title="AI Resume Analyzer", page_icon="📄",
                   layout="wide", initial_sidebar_state="expanded")
dashboard.inject_css()


@st.cache_resource(show_spinner=False)
def get_pipeline() -> ResumeAnalysisPipeline:
    """Build the pipeline once (loads and caches the NLP models)."""
    return ResumeAnalysisPipeline()


def read_resume(uploaded) -> str:
    name = uploaded.name.lower()
    if name.endswith(".pdf"):
        return pdf_parser.extract_text(uploaded)
    if name.endswith(".docx"):
        return docx_parser.extract_text(uploaded)
    return uploaded.read().decode("utf-8", errors="ignore")


# ── Sidebar ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    role_choice = st.selectbox("Target Job Role",
                               ["🔎 Auto-detect from Job Description"] + ROLE_NAMES)
    st.markdown("---")
    st.markdown("### How it works")
    st.markdown(
        "1. Upload your resume (PDF/DOCX/TXT)\n"
        "2. Paste the job description\n"
        "3. The NLP engine scores and analyzes the match\n"
        "4. Review charts, gaps, strengths and tailored tips")
    st.markdown("---")
    st.caption("v3.0 · spaCy + Sentence-Transformers · Final Year Project")

# ── Header & inputs ────────────────────────────────────────────────────
st.markdown('<p class="main-header">📄 AI Resume Analyzer</p>',
            unsafe_allow_html=True)
st.markdown('<p class="sub-header">Semantic, NLP-powered resume analysis and '
            'ATS optimization</p>', unsafe_allow_html=True)

col1, col2 = st.columns(2, gap="large")
with col1:
    st.markdown("### 📤 Upload Resume")
    uploaded = st.file_uploader("PDF, DOCX or TXT",
                                type=["pdf", "docx", "txt"])
with col2:
    st.markdown("### 📋 Job Description")
    jd_text = st.text_area("Paste the job description", height=150,
                           placeholder="Paste the full job description here...")

# ── Analysis ───────────────────────────────────────────────────────────
if uploaded and jd_text.strip():
    with st.spinner("Loading models and analyzing..."):
        resume_text = read_resume(uploaded)
        if not resume_text.strip():
            st.error("Could not extract text from the file. "
                     "If it is a scanned PDF, OCR is required.")
            st.stop()
        pipeline = get_pipeline()
        role = None if role_choice.startswith("🔎") else role_choice
        result = pipeline.analyze(resume_text, jd_text, role=role)

    st.success("✅ Analysis complete")
    dashboard.render(result)

    # Downloadable feedback report
    st.markdown("---")
    st.markdown("### 📥 Download Feedback Report")
    role_disp = (f"Custom Role - {result['role']['detected_title']}"
                 if result["role"].get("is_custom") else result["role"]["role"])
    lines = [
        "AI RESUME ANALYZER - FEEDBACK REPORT",
        "=" * 52,
        f"Role detection     : {role_disp} "
        f"(confidence {result['role']['confidence']:.0%})",
        f"Semantic engine    : {result['engine']}",
        "",
        f"Resume Quality Score    : {result['resume_quality']}/100",
        f"Job Match Score         : {result['job_match']}/100",
        f"ATS Compatibility Score : {result['ats_compatibility']}/100",
        f"Resume <-> Job Similarity: {result['semantic_match']}% "
        f"({result['semantic_label']})",
        f"Hiring Decision         : {result['decision']['label']}",
        f"Match Confidence        : {result['match_confidence']}",
        "",
        "SCORE COMPONENTS:",
        *[f"  {k:<16}: {v}/100" for k, v in result["components"].items()],
        "",
        f"SKILL COVERAGE     : {result['skill_gap']['coverage_pct']}%",
        f"Required skills    : {', '.join(result['skill_gap']['required']) or 'None'}",
        f"Detected skills    : {', '.join(result['skill_gap']['found']) or 'None'}",
        f"Missing skills     : {', '.join(result['skill_gap']['missing']) or 'None'}",
        "",
        "RECRUITER ASSESSMENT",
        " Strengths:", *[f"  + {s}" for s in result["recruiter"]["strengths"]],
        " Concerns :", *[f"  - {c}" for c in result["recruiter"]["concerns"]],
        f" Recommendation: {result['recruiter']['recommendation']}",
        "",
        "FEEDBACK:",
        f"  {result['narrative']}",
        "",
        "RECOMMENDATIONS:",
        *[f"  {i}. {t}" for i, t in enumerate(result["suggestions"], 1)],
    ]
    st.download_button("⬇️ Download Report (.txt)", "\n".join(lines),
                       file_name="resume_feedback_report.txt", mime="text/plain")

elif uploaded and not jd_text.strip():
    st.info("Paste a job description to begin.")
elif jd_text.strip() and not uploaded:
    st.info("Upload a resume to begin.")
else:
    st.markdown("---")
    a, b, c = st.columns(3)
    a.markdown("#### 🧠 Real NLP\nspaCy + Sentence-Transformers for semantic "
               "matching, not just keywords.")
    b.markdown("#### 📊 6-Factor Score\nSemantic, skills, experience, "
               "education, structure and achievements.")
    c.markdown("#### 🎯 Tailored Tips\nRecommendations generated from your "
               "actual skill and content gaps.")
