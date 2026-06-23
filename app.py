import streamlit as st
import requests
import json
import os
from datetime import datetime

# Import Phase functions for direct fallback (Streamlit Cloud Deployment)
from Phase1_Data_Acquisition.scraper import scrape_reviews
from Phase2_Data_Processing.processor import process_reviews
from Phase3_Theme_Generation.theme_engine import run_phase_3
from Phase4_Synthesis_Reporting.reporter import generate_report

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Page Configuration
st.set_page_config(
    page_title="Spotify Review Discovery Engine",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Look
st.markdown("""
<style>
    .stApp {
        background-color: #121212;
        color: #FFFFFF;
    }
    .main-header {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(45deg, #1DB954, #191414);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #181818;
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid #282828;
        transition: transform 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        border-color: #1DB954;
    }
    .quote-box {
        background-color: #282828;
        padding: 1rem;
        border-left: 5px solid #1DB954;
        margin-bottom: 1rem;
        font-style: italic;
    }
</style>
""", unsafe_allow_html=True)

# Direct execution helper
def run_full_pipeline_directly():
    with st.status("🚀 Running Discovery Pipeline...", expanded=True) as status:
        st.write("Fetching reviews...")
        scrape_reviews(target_count=500)
        st.write("Cleaning and filtering...")
        process_reviews()
        st.write("Generating AI themes...")
        run_phase_3()
        st.write("Synthesizing report...")
        generate_report()
        status.update(label="✅ Analysis Complete!", state="complete", expanded=False)

# Sidebar - Nudges/Navigation
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/1/19/Spotify_logo_without_text.svg", width=50)
st.sidebar.title("Discovery Control")

# Nudge 1: Navigation Selector
navigation = st.sidebar.radio(
    "Navigation Nudges",
    ["📝 Latest Weekly Note", "🔍 Deep Dive by Themes"],
    index=0
)

st.sidebar.markdown("---")

# Trigger Button
if st.sidebar.button("🚀 Trigger New Analysis", use_container_width=True):
    try:
        # Try calling the FastAPI backend first (Local mode)
        response = requests.post(f"{API_BASE_URL}/analyze", json={"limit": 500}, timeout=2)
        if response.status_code == 200:
            st.sidebar.success("Analysis triggered via API!")
        else:
            st.sidebar.info("API unavailable. Running directly...")
            run_full_pipeline_directly()
            st.rerun()
    except:
        # Fallback to direct execution (Streamlit Cloud mode)
        st.sidebar.info("Local API not detected. Running directly on cloud...")
        run_full_pipeline_directly()
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("Dual-Mode: Local API & Cloud Native")

# Main Header
st.markdown('<div class="main-header">Discovery Engine Insights</div>', unsafe_allow_html=True)

# Fetch Data helper (Handles both API and Local File fallback)
def load_analysis_data():
    # Try API first
    try:
        res = requests.get(f"{API_BASE_URL}/results", timeout=2)
        if res.status_code == 200:
            return res.json(), "API"
    except:
        pass
    
    # Fallback to local files
    path = "data/themed_reviews.json"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f), "FILE"
    return None, None

def load_report_content():
    # Try API first
    try:
        res = requests.get(f"{API_BASE_URL}/report", timeout=2)
        if res.status_code == 200:
            return res.json()['content'], "API"
    except:
        pass
    
    # Fallback to local files
    path = "reports/weekly_note.md"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read(), "FILE"
    return None, None

data, source = load_analysis_data()

if data:
    reviews = data['grouped_reviews']
    total_reviews = len(reviews)
    avg_rating = sum([r['rating'] for r in reviews]) / total_reviews if total_reviews > 0 else 0
    
    # Metrics Row
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="metric-card"><h3>Total Analyzed</h3><h1 style="color:#1DB954">{total_reviews}</h1></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><h3>Avg. Rating</h3><h1 style="color:#1DB954">{avg_rating:.2f} ★</h1></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><h3>Report Date</h3><h1 style="color:#1DB954">{datetime.now().strftime("%b %d")}</h1></div>', unsafe_allow_html=True)

    st.markdown("---")

    # Handle Navigation Nudges
    if navigation == "📝 Latest Weekly Note":
        report_content, r_source = load_report_content()
        if report_content:
            st.subheader(f"📄 Latest Weekly Note (Source: {r_source})")
            st.markdown(report_content)
        else:
            st.warning("Weekly report not available yet. Please trigger an analysis.")

    elif navigation == "🔍 Deep Dive by Themes":
        st.subheader(f"🔍 Deep Dive: Exploring Themes (Source: {source})")
        selected_theme = st.selectbox("Select a theme to explore detailed feedback:", data['themes'])
        
        theme_reviews = [r for r in reviews if r['theme'] == selected_theme]
        st.write(f"Showing feedback for: **{selected_theme}** ({len(theme_reviews)} reviews)")
        
        for r in theme_reviews[:15]:
            st.markdown(f'<div class="quote-box">"{r["text"]}"</div>', unsafe_allow_html=True)
            source_tag = r.get('source', 'Google Play Store')
            st.caption(f"Rating: {r['rating']} ★ | Date: {r['date'].split('T')[0]} | Source: {source_tag}")
else:
    st.info("👋 Welcome! No analysis data found. Use the 'Trigger New Analysis' button in the sidebar to start.")
    st.image("https://images.unsplash.com/photo-1614680376593-902f74cf0d41?auto=format&fit=crop&q=80&w=1500")

# Footer
st.markdown("---")
st.caption("Produced by Antigravity Spotify Review Discovery Engine")
