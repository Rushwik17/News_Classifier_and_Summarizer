import streamlit as st
from main import classify_and_summarize, All, Classified
from feed_parsing import fetch_data

st.set_page_config(
    page_title="Hindi News Briefing",
    page_icon="HN",
    layout="wide",
)

CATEGORY_COLORS = {
    "Automobile":    "#64748b",
    "Business":      "#10b981",
    "Crime":         "#dc2626",
    "Education":     "#8b5cf6",
    "Entertainment": "#ec4899",
    "Health":        "#06b6d4",
    "International": "#3b82f6",
    "Sports":        "#f59e0b",
    "National":      "#f97316",
    "Politics":      "#ef4444",
    "Technology":    "#6366f1",
}
DEFAULT_COLOR = "#6366f1"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Noto+Sans+Devanagari:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', 'Noto Sans Devanagari', sans-serif;
}

/* Main container */
.block-container {
    max-width: 960px;
    padding-top: 1.2rem;
    padding-bottom: 3rem;
}

/* ── Hero header ── */
.hero-header {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 40%, #2563eb 80%, #7c3aed 100%);
    border-radius: 20px;
    padding: 36px 40px 32px;
    margin-bottom: 28px;
    color: #fff;
    position: relative;
    overflow: hidden;
    animation: fadeSlideDown 0.6s ease both;
    box-shadow: 0 8px 32px rgba(37, 99, 235, 0.25);
}
.hero-header::before {
    content: "";
    position: absolute;
    top: -60px; right: -60px;
    width: 220px; height: 220px;
    border-radius: 50%;
    background: rgba(255,255,255,0.04);
}
.hero-header::after {
    content: "";
    position: absolute;
    bottom: -30px; left: 50px;
    width: 120px; height: 120px;
    border-radius: 50%;
    background: rgba(124, 58, 237, 0.15);
}
.hero-header h1 {
    font-size: 2.1rem;
    font-weight: 800;
    margin: 0 0 6px;
    letter-spacing: -0.8px;
    line-height: 1.2;
}
.hero-header p {
    margin: 0;
    opacity: 0.72;
    font-size: 0.92rem;
    font-weight: 400;
    letter-spacing: 0.3px;
}

/* ── News card ── */
.news-card {
    padding: 0;
    margin-bottom: 18px;
    border-radius: 16px;
    border: 1px solid #e5e7eb;
    background: #ffffff;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.03);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    animation: fadeIn 0.45s ease both;
    position: relative;
    overflow: hidden;
}
.news-card::before {
    content: "";
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 5px;
    background: var(--accent, #6366f1);
    border-radius: 5px 0 0 5px;
}
.news-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 28px rgba(0,0,0,0.09);
}

/* Card top (headline area) */
.card-top {
    padding: 18px 22px 0 22px;
}
.card-meta {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 10px;
}
.card-index {
    font-size: 10px;
    font-weight: 700;
    color: #94a3b8;
    background: #f1f5f9;
    border-radius: 6px;
    padding: 3px 9px;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}
.card-tag {
    font-size: 10px;
    font-weight: 700;
    padding: 3px 11px;
    border-radius: 20px;
    color: #fff;
    letter-spacing: 0.4px;
    text-transform: uppercase;
}

/* Headline */
.card-headline {
    font-size: 17px;
    font-weight: 700;
    color: #0f172a;
    margin: 0 0 4px;
    line-height: 1.55;
    letter-spacing: -0.2px;
}

/* Card body (summary area) */
.card-body {
    padding: 10px 22px 18px 22px;
}
.card-summary-label {
    font-size: 10px;
    font-weight: 700;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 6px;
}
.card-summary {
    font-size: 14.5px;
    line-height: 1.75;
    color: #374151;
    font-weight: 400;
}

/* Card divider */
.card-divider {
    height: 1px;
    background: #f1f5f9;
    margin: 0 22px;
}

/* ── Full article view ── */
.article-back-bar {
    margin-bottom: 20px;
}
.article-header {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #2563eb 100%);
    border-radius: 18px;
    padding: 32px 36px;
    margin-bottom: 20px;
    color: #fff;
    position: relative;
    overflow: hidden;
    box-shadow: 0 6px 24px rgba(37, 99, 235, 0.2);
}
.article-header::before {
    content: "";
    position: absolute;
    top: -40px; right: -40px;
    width: 160px; height: 160px;
    border-radius: 50%;
    background: rgba(255,255,255,0.04);
}
.article-header .article-tag {
    display: inline-block;
    font-size: 11px;
    font-weight: 700;
    padding: 4px 14px;
    border-radius: 20px;
    color: #fff;
    margin-bottom: 14px;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}
.article-header h2 {
    font-size: 1.5rem;
    font-weight: 800;
    margin: 0;
    line-height: 1.45;
    letter-spacing: -0.5px;
}

.article-section {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 16px;
    padding: 28px 32px;
    margin-bottom: 16px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.article-section h3 {
    font-size: 11px;
    font-weight: 700;
    color: #94a3b8;
    margin: 0 0 14px;
    text-transform: uppercase;
    letter-spacing: 1px;
}
.article-section .content-text {
    font-size: 15.5px;
    line-height: 1.85;
    color: #1e293b;
}

/* ── Sidebar dark theme ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important;
    border-right: none !important;
    padding-top: 0.5rem;
}
[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}
[data-testid="stSidebar"] h2 {
    font-size: 1.3rem !important;
    font-weight: 700 !important;
    color: #f8fafc !important;
    letter-spacing: -0.3px !important;
    padding: 16px 16px 6px !important;
    border-bottom: 1px solid rgba(255,255,255,0.08) !important;
    margin-bottom: 10px !important;
}
[data-testid="stSidebar"] div[data-testid="stRadio"] p {
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    color: #64748b !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    margin-bottom: 8px !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] label {
    font-size: 0.92rem !important;
    font-weight: 500 !important;
    padding: 6px 10px !important;
    border-radius: 8px !important;
    transition: background 0.15s !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    background: rgba(255,255,255,0.07) !important;
}

/* Sidebar button */
[data-testid="stSidebar"] button {
    background: linear-gradient(135deg, #2563eb, #7c3aed) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    padding: 8px 16px !important;
    width: 100% !important;
    margin: 12px 0 6px !important;
    cursor: pointer !important;
    transition: opacity 0.15s ease, transform 0.15s ease !important;
    letter-spacing: 0.3px !important;
}
[data-testid="stSidebar"] button:hover {
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
}

/* Loading screen */
.loading-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    padding: 24px;
    text-align: center;
}
.loading-title {
    font-size: 1.3rem;
    font-weight: 600;
    color: #1e3a5f;
    margin-bottom: 6px;
}
.loading-sub {
    font-size: 0.9rem;
    color: #6b7280;
    margin-bottom: 20px;
}
.loading-spinner {
    width: 60px;
    height: 60px;
    border: 4px solid #e5e7eb;
    border-top: 4px solid #2563eb;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto 20px;
}
@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* Stats bar */
.stats-bar {
    display: flex;
    gap: 10px;
    margin-bottom: 22px;
    flex-wrap: wrap;
}
.stat-chip {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 20px;
    padding: 5px 16px;
    font-size: 12px;
    font-weight: 600;
    color: #475569;
    display: flex;
    align-items: center;
    gap: 5px;
}

/* Card button container */
.card-button-wrap {
    padding: 0 22px 18px 22px;
}

/* Hide the view button containers */
div[key*="view_"] {
    display: none !important;
}

/* Alternative: hide with negative margin */
[data-testid="stButton"] button[data-testid*="view_"] {
    display: none !important;
}

/* Style buttons inside news cards */
.news-card ~ [data-testid="stButton"] {
    margin-top: -1.5rem;
}

/* Keyframes */
@keyframes fadeSlideDown {
    from { opacity: 0; transform: translateY(-18px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}
</style>
""", unsafe_allow_html=True)

if "data_loaded" not in st.session_state:
    placeholder = st.empty()
    with placeholder.container():
        st.markdown("""
        <div class="loading-wrap">
            <div class="loading-spinner"></div>
            <div class="loading-title">Fetching latest Hindi news...</div>
            <div class="loading-sub">Classifying and summarizing with AI -- this may take a moment</div>
        </div>
        """, unsafe_allow_html=True)
        with st.spinner(""):
            data_path = fetch_data()
            all_summaries, classified = classify_and_summarize(data_path)
    placeholder.empty()
    st.session_state.all_summaries = all_summaries
    st.session_state.classified = classified
    st.session_state.data_loaded = True
    
else:
    all_summaries = st.session_state.all_summaries
    classified = st.session_state.classified

if "viewing_article" not in st.session_state:
    st.session_state.viewing_article = None
if "article_source_idx" not in st.session_state:
    st.session_state.article_source_idx = 0

def show_full_article():
    """Render the full article detail view."""
    art = st.session_state.viewing_article
    label = art["label"]
    color = CATEGORY_COLORS.get(label, DEFAULT_COLOR)

    st.markdown(f"""
    <div class="article-header">
        <span class="article-tag" style="background:{color};">{label}</span>
        <h2>{art['title']}</h2>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="article-section">
        <h3>Full Article</h3>
        <div class="content-text">{art['description']}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    if st.button("← BACK TO NEWS LIST", key="back_btn", use_container_width=True):
        st.session_state.viewing_article = None
        st.session_state.previous_category_idx = st.session_state.article_source_idx
        st.rerun()

    return

if st.session_state.viewing_article is not None:
    show_full_article()
    st.stop()

st.markdown("""
<div class="hero-header">
    <h1>Hindi News Briefing</h1>
    <p>Sourced from Dainik Bhaskar</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("## Categories")

if st.sidebar.button("Refresh News"):
    st.session_state.clear()
    st.rerun()

categories_with_all = ["All"] + list(classified.keys())

if "previous_category_idx" not in st.session_state:
    st.session_state.previous_category_idx = 0

selected_idx = st.sidebar.radio(
    "Browse by topic",
    options=range(len(categories_with_all)),
    format_func=lambda i: categories_with_all[i],
    index=st.session_state.previous_category_idx,
)

st.session_state.previous_category_idx = selected_idx
selected_category = categories_with_all[selected_idx]

def render_card(idx: int, label: str, summary: str, title: str, description: str, category_context: str):
    color = CATEGORY_COLORS.get(label, DEFAULT_COLOR)

    st.markdown(f"""
    <div class="news-card" style="--accent:{color};">
        <div class="card-top">
            <div class="card-meta">
                <span class="card-index">#{idx}</span>
                <span class="card-tag" style="background:{color};">{label}</span>
            </div>
            <div class="card-headline">{title}</div>
        </div>
        <div class="card-divider"></div>
        <div class="card-body">
            <div class="card-summary-label">AI Summary</div>
            <div class="card-summary">{summary}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("View Full Article", key=f"view_{category_context}_{label}_{idx}", use_container_width=True):
        st.session_state.article_source_idx = st.session_state.previous_category_idx
        st.session_state.viewing_article = {
            "label": label,
            "summary": summary,
            "title": title,
            "description": description,
        }
        st.rerun()

if selected_category == "All":
    for idx, (label, summary, title, description) in enumerate(all_summaries, start=1):
        render_card(idx, label, summary, title, description, "All")
else:
    items = classified[selected_category]
    for idx, (summary, title, description) in enumerate(items, start=1):
        render_card(idx, selected_category, summary, title, description, selected_category)