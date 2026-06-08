# AI Resume Analyzer (v4 — Quality vs. Match Separation)

Final Year Project · Muhammad Zeeshan Ahmad (2022-ag-7939) · BS IT
Supervisor: Dr. M. Milhan Afzal Khan · IT-610 · University of Agriculture Faisalabad

Semantic, NLP-powered resume analyzer (spaCy + Sentence-Transformers
`all-MiniLM-L6-v2`) that **separates how well a resume is written from how well
it fits a job**, so a polished but irrelevant resume correctly scores low.

## Setup
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm   # one-time, needs internet
streamlit run app.py
```
If transformers/spaCy are absent the app runs on a scikit-learn TF-IDF
fallback (never crashes; lower semantic accuracy).

## Three separated scores (Fix #1)
| Score | Measures | JD-dependent? |
|-------|----------|:---:|
| **Resume Quality** | structure, achievements, experience, education, skill richness | No |
| **Job Match** | semantic similarity + required-skill coverage | Yes |
| **ATS Compatibility** | final score = 0.3·Quality + 0.7·Match, **× relevance penalty** | Yes |

## Relevance penalty (Fix #2)
`semantic < 15% → ×0.30`, `semantic < 30% → ×0.50`. High skill coverage
(≥50%/≥75%) rescues the multiplier so genuine matches aren't over-penalized
on the lexical fallback engine.

## Other fixes
- **#3 Confidence-aware role detection** — below 40% confidence it returns
  *Custom Role* + the detected title instead of forcing a wrong category.
- **#4 Skill extraction** — spaCy PhraseMatcher + noun-chunk extraction picks
  up novel domain phrases ("dragon handling", "storm scheduling"); shows
  Required / Detected / Missing.
- **#5 Recruiter Assessment** — strengths, concerns, recommendation, confidence.
- **#6 Semantic visibility** — Resume↔Job similarity shown as a % + label.
- **#7 Narrative feedback** — explains *why*, grounded in actual gaps.
- **#8 Decision system** — Highly Recommended / Recommended / Consider /
  Weak Match / Not Recommended.

## Dragon Wrangler test result
Custom Role (6% conf) · Quality 72 · Job Match 3 · **ATS Compatibility 7** ·
Semantic 6% (Very Weak) · **Not Recommended** — exactly the intended behavior.

## Architecture
```
app.py · analyzer/{semantic_matcher,skill_extractor,info_extractor,
role_detector,ats_scorer,suggestion_engine,pipeline}.py ·
utils/{pdf_parser,docx_parser,text_cleaner}.py ·
visualizations/{charts,dashboard}.py · models/transformer_models.py ·
data/skills_db.py
```
