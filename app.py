import streamlit as st
import requests
import json
import os
from datetime import datetime

# API Configuration
API_BASE_URL = "http://localhost:8000"

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
    .nav-nudge {
        background-color: #1DB954;
        color: white;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 20px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

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
        response = requests.post(f"{API_BASE_URL}/analyze", json={"limit": 500})
        if response.status_code == 200:
            st.sidebar.success("Analysis triggered! Running in background...")
        else:
            st.sidebar.error("Failed to trigger analysis.")
    except Exception as e:
        st.sidebar.error(f"Connection error: {e}")

st.sidebar.markdown("---")
st.sidebar.caption("Backend: FastAPI | Frontend: Streamlit")

# Main Header
st.markdown('<div class="main-header">Discovery Engine Insights</div>', unsafe_allow_html=True)

# Fetch Data from API
def fetch_data():
    try:
        res = requests.get(f"{API_BASE_URL}/results")
        if res.status_code == 200:
            return res.json()
        return None
    except:
        return None

def fetch_report():
    try:
        res = requests.get(f"{API_BASE_URL}/report")
        if res.status_code == 200:
            return res.json()['content']
        return None
    except:
        return None

data = fetch_data()

if data:
    reviews = data['grouped_reviews']
    total_reviews = len(reviews)
    avg_rating = sum([r['rating'] for r in reviews]) / total_reviews if total_reviews > 0 else 0

    # Top Metrics (Always visible)
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
        report_content = fetch_report()
        if report_content:
            st.subheader("📄 Latest Weekly Note Preview")
            st.markdown(report_content)
        else:
            st.warning("Weekly report not available yet. Please trigger an analysis.")

    elif navigation == "🔍 Deep Dive by Themes":
        st.subheader("🔍 Deep Dive: Exploring Themes")
        selected_theme = st.selectbox("Select a theme to explore detailed feedback:", data['themes'])
        
        theme_reviews = [r for r in reviews if r['theme'] == selected_theme]
        st.write(f"Showing feedback for: **{selected_theme}** ({len(theme_reviews)} reviews)")
        
        for r in theme_reviews[:15]:
            st.markdown(f'<div class="quote-box">"{r["text"]}"</div>', unsafe_allow_html=True)
            st.caption(f"Rating: {r['rating']} ★ | Date: {r['date'].split('T')[0]}")
else:
    st.info("👋 Welcome! No analysis data found. Use the 'Trigger New Analysis' button in the sidebar to start.")
    st.image("https://images.unsplash.com/photo-1614680376593-902f74cf0d41?auto=format&fit=crop&q=80&w=1500")

# Footer
st.markdown("---")
st.caption("Produced by Antigravity Spotify Review discovery Engine")
