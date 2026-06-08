"""
dashboard.py
------------
Streamlit rendering of the analysis (Fixes #1, #4, #5, #6, #8).

Surfaces the three separated scores, a prominent hiring decision, the
resume<->job semantic similarity, the required/detected/missing skills, the
recruiter assessment, strengths/weaknesses, narrative feedback and tips.
"""

from __future__ import annotations
from typing import Dict

import streamlit as st

from visualizations import charts

CSS = """
<style>
.main-header { font-size:2.4rem; font-weight:700; color:#4da3ff; text-align:center; margin-bottom:.3rem; }
.sub-header  { font-size:1.0rem; color:#9aa7b4; text-align:center; margin-bottom:1.2rem; }
.score-card { background:#161f2b; border-radius:12px; padding:1rem; text-align:center; border-top:4px solid #4da3ff; }
.score-card .v { font-size:2.2rem; font-weight:700; }
.score-card .l { font-size:.85rem; color:#9aa7b4; }
.decision { text-align:center; padding:.9rem; border-radius:12px; font-size:1.4rem; font-weight:700; color:#fff; margin:.4rem 0 1rem; }
.sem-box { background:#161f2b; border-radius:10px; padding:1rem 1.2rem; text-align:center; }
.sem-box .pct { font-size:2rem; font-weight:700; }
.badge-found   { background:#1e4620; color:#7ee787; padding:4px 11px; border-radius:12px; margin:3px; display:inline-block; font-size:.85rem; }
.badge-missing { background:#4d1f24; color:#ff7b81; padding:4px 11px; border-radius:12px; margin:3px; display:inline-block; font-size:.85rem; }
.badge-req     { background:#2a2f3a; color:#cdd6e0; padding:4px 11px; border-radius:12px; margin:3px; display:inline-block; font-size:.85rem; }
.pill { background:#13314f; color:#9cd1ff; padding:6px 14px; border-radius:8px; display:inline-block; font-weight:600; }
.pill-warn { background:#3a2a10; color:#ffce6b; }
.s-box { background:#11261a; border-left:4px solid #28a745; padding:.55rem .9rem; border-radius:4px; margin-bottom:.45rem; color:#cde6d4; }
.w-box { background:#2a1416; border-left:4px solid #dc3545; padding:.55rem .9rem; border-radius:4px; margin-bottom:.45rem; color:#f3c9cc; }
.tip-box { background:#2b2410; border-left:4px solid #ffc107; padding:.65rem 1rem; border-radius:4px; margin-bottom:.5rem; color:#ffe9a8; }
.tip-box b { color:#ffd24d; }
.narr { background:#13202e; border-left:4px solid #4da3ff; padding:.9rem 1.1rem; border-radius:6px; color:#cdd9e6; }
</style>
"""


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def _color(v: float) -> str:
    return "#28a745" if v >= 70 else "#ffc107" if v >= 45 else "#dc3545"


def render(result: Dict) -> None:
    role = result["role"]
    engine = result["engine"]

    # ---- role / custom role (Fix #3) --------------------------------
    if role.get("is_custom"):
        st.markdown(
            f'Role detection: <span class="pill pill-warn">Custom Role</span> '
            f'&nbsp; Detected title: <span class="pill">{role["detected_title"]}</span> '
            f'&nbsp; <span style="color:#8a98a6">confidence {role["confidence"]:.0%} '
            f'&middot; {role["message"]}</span>', unsafe_allow_html=True)
    else:
        st.markdown(
            f'Target role: <span class="pill">{role["role"]}</span> '
            f'&nbsp; <span style="color:#8a98a6">confidence '
            f'{role["confidence"]:.0%}</span>', unsafe_allow_html=True)
    note = ("Sentence-Transformers (all-MiniLM-L6-v2)"
            if engine == "transformer" else
            "TF-IDF fallback - install sentence-transformers for full semantics")
    st.caption(f"Semantic engine: {note}")

    # ---- decision banner (Fix #8) -----------------------------------
    dec = result["decision"]
    st.markdown(
        f'<div class="decision" style="background:{dec["color"]}">'
        f'{dec["label"]} &nbsp;·&nbsp; ATS Compatibility '
        f'{result["ats_compatibility"]}/100</div>', unsafe_allow_html=True)

    # ---- three separated scores (Fix #1) ----------------------------
    c1, c2, c3 = st.columns(3)
    cards = [
        (c1, "Resume Quality", result["resume_quality"],
         "How well the resume is written"),
        (c2, "Job Match", result["job_match"],
         "Relevance to this specific job"),
        (c3, "ATS Compatibility", result["ats_compatibility"],
         "Final score (gated by relevance)"),
    ]
    for col, label, val, sub in cards:
        col.markdown(
            f'<div class="score-card" style="border-top-color:{_color(val)}">'
            f'<div class="v" style="color:{_color(val)}">{val}</div>'
            f'<div class="l"><b>{label}</b><br>{sub}</div></div>',
            unsafe_allow_html=True)

    st.markdown("")

    # ---- semantic match visibility (Fix #6) -------------------------
    sc1, sc2 = st.columns([1, 2])
    with sc1:
        sm = result["semantic_match"]
        st.markdown(
            f'<div class="sem-box"><div class="l">Resume ↔ Job Similarity</div>'
            f'<div class="pct" style="color:{_color(sm)}">{sm}%</div>'
            f'<div class="l">{result["semantic_label"]}</div></div>',
            unsafe_allow_html=True)
        if result["penalty_multiplier"] < 1.0:
            st.caption(f"⚠ Low-relevance penalty applied "
                       f"(×{result['penalty_multiplier']}).")
    with sc2:
        st.plotly_chart(charts.score_gauge(result["ats_compatibility"]),
                        use_container_width=True)

    st.markdown("---")

    # ---- charts -----------------------------------------------------
    g1, g2 = st.columns(2)
    with g1:
        st.plotly_chart(charts.component_bars(result["components"]),
                        use_container_width=True)
    with g2:
        st.plotly_chart(charts.strength_radar(result["components"]),
                        use_container_width=True)
    g3, g4 = st.columns(2)
    with g3:
        st.plotly_chart(charts.skill_gap_chart(result["skill_gap"]),
                        use_container_width=True)
    with g4:
        st.plotly_chart(charts.section_completeness(result["sections"]),
                        use_container_width=True)
    g5, g6 = st.columns(2)
    with g5:
        st.plotly_chart(
            charts.experience_distribution(result["experience"],
                                           result["achievements"]),
            use_container_width=True)
    with g6:
        st.plotly_chart(charts.keyword_heatmap(result["skill_gap"]),
                        use_container_width=True)

    st.markdown("---")

    # ---- required / detected / missing skills (Fix #4) --------------
    gap = result["skill_gap"]
    st.markdown("#### Skills Analysis")
    r1, r2, r3 = st.columns(3)
    with r1:
        st.markdown("**Required (from JD)**")
        st.markdown(" ".join(f'<span class="badge-req">{s}</span>'
                             for s in gap["required"]) or "_None_",
                    unsafe_allow_html=True)
    with r2:
        st.markdown("**Detected (matched)**")
        st.markdown(" ".join(f'<span class="badge-found">{s}</span>'
                             for s in gap["found"]) or "_None_",
                    unsafe_allow_html=True)
    with r3:
        st.markdown("**Missing**")
        st.markdown(" ".join(f'<span class="badge-missing">{s}</span>'
                             for s in gap["missing"]) or "_None_",
                    unsafe_allow_html=True)

    st.markdown("---")

    # ---- recruiter assessment (Fix #5) ------------------------------
    rec = result["recruiter"]
    st.markdown("#### 🧑‍💼 Recruiter Assessment")
    rc1, rc2 = st.columns(2)
    with rc1:
        st.markdown("**Strengths**")
        for s in rec["strengths"]:
            st.markdown(f'<div class="s-box">✓ {s}</div>', unsafe_allow_html=True)
    with rc2:
        st.markdown("**Concerns**")
        for c in rec["concerns"]:
            st.markdown(f'<div class="w-box">✗ {c}</div>', unsafe_allow_html=True)
    st.markdown(
        f'**Recommendation:** <span class="pill" style="background:'
        f'{result["decision"]["color"]};color:#fff">{rec["recommendation"]}'
        f'</span> &nbsp; **Match Confidence:** {rec["match_confidence"]}',
        unsafe_allow_html=True)

    st.markdown("---")

    # ---- narrative + tips (Fix #7) ----------------------------------
    st.markdown("#### Feedback Summary")
    st.markdown(f'<div class="narr">{result["narrative"]}</div>',
                unsafe_allow_html=True)
    st.markdown("#### Personalized Recommendations")
    for i, tip in enumerate(result["suggestions"], 1):
        st.markdown(f'<div class="tip-box"><b>Tip {i}:</b> {tip}</div>',
                    unsafe_allow_html=True)
