import streamlit as st
from main import classify_and_summarize, All, Classified
from feed_parsing import fetch_data

st.set_page_config(page_title="News Summarizer", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

html, body, [class*="css"]  {
    font-family: 'Inter', sans-serif;
}

.block-container {
    max-width: 900px;
    padding-top: 2rem;
}

.card {
    padding: 16px 20px;
    margin-bottom: 16px;
    border-radius: 12px;
    border: 1px solid #e5e7eb;
    background-color: #fafafa;
}

.label {
    font-size: 14px;
    color: #6b7280;
    margin-bottom: 6px;
}

.summary {
    font-size: 16px;
    line-height: 1.6;
    color: #111827;
}

[data-testid="stSidebar"] {
    border-right: 1px solid black !important;
    padding-top: 1rem;
}

/* Categories (primary heading) */
[data-testid="stSidebar"] h2 {
    font-size: 32px !important;
    font-weight: 700 !important;
    margin-bottom: 12px !important;
}

/* Select Category (secondary label) */
[data-testid="stSidebar"] div[data-testid="stRadio"] p {
    font-size: 20px !important;
    font-weight: 500 !important;
    margin-bottom: 6px !important;
    color: #374151 !important;
}

/* Radio options */
[data-testid="stSidebar"] div[role="radiogroup"] label {
    font-size: 18px !important;
    font-weight: 500 !important;
}

</style>
""", unsafe_allow_html=True)

if "data_loaded" not in st.session_state:
    placeholder = st.empty()

    with placeholder.container():
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.markdown("<br><br><br><br>", unsafe_allow_html=True)
            with st.spinner("Fetching and summarizing news..."):
                data_path = fetch_data()
                all_summaries, classified = classify_and_summarize(data_path)

    placeholder.empty()

    st.session_state.all_summaries = all_summaries
    st.session_state.classified = classified
    st.session_state.data_loaded = True

else:
    all_summaries = st.session_state.all_summaries
    classified = st.session_state.classified

st.markdown("""
<h1 style="font-weight:600; margin-bottom:0;">News Summaries</h1>
<p style="color:#6b7280; margin-top:4px;">
Latest categorized news summaries
</p>
""", unsafe_allow_html=True)

if st.sidebar.button("Refresh News"):
    st.session_state.clear()
    st.rerun()

st.sidebar.title("Categories")

selected_category = st.sidebar.radio(
    "Select Category",
    ["All"] + list(classified.keys())
)

if selected_category == "All":
    for idx, (label, summary) in enumerate(all_summaries):
        st.markdown(f"""
        <div class="card">
            <div class="label">{idx+1}</div>
            <div class="summary">{summary}</div>
        </div>
        """, unsafe_allow_html=True)
else:
    summaries = classified[selected_category]
    for idx, summary in enumerate(summaries):
        st.markdown(f"""
        <div class="card">
            <div class="label">{idx+1}</div>
            <div class="summary">{summary}</div>
        </div>
        """, unsafe_allow_html=True)