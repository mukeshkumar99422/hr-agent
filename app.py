import os
import sys
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0,os.path.dirname(__file__))

from src.cache import setup_cache
setup_cache()

# streamlit page configuration
st.set_page_config(
    page_title="HR shortlisting agent",
    page_icon="📜",
    layout="wide",
)

st.markdown("""
<style>
    /* Custom styles */
  .stProgress > div > div { background-color: #534AB7; }
  .block-container { padding-top: 2rem; }
  div[data-testid="metric-container"] {
    background: #f9f9f9; border-radius: 8px;
    padding: 12px; border: 1px solid #eee;
  }
</style>
""", unsafe_allow_html=True)

# default states of app
defaults={
    "page": "upload_jd",
    "jd_obj": None,
    "jd_file_path": None,
    "jd_name": None,
    "resume_files": [],
    "resume_files": [],
    "linkedin_profiles": [],
    "linkedin_urls": [],
    "ranked": None,
    "scored_map": {},
    "profile_map": {},
    "report_path": None
}

for key,val in defaults.items():
    if key not in st.session_state:
        st.session_state[key]=val


# Header
st.markdown("## HR Shortlisting Agent")
st.caption("AI-powered candidate evaluation · Gemini 2.0 Flash + LangChain")

pages=["upload_jd","upload_candidates","analysis","report","override"]
labels=[
    "1. Job Description",
    "2. Candidates",
    "3. Analysis",
    "4. Report",
    "5. Override"
]

# Safe index lookup (if page value is unexpected)
current_index = pages.index(st.session_state.page) \
    if st.session_state.page in pages else 0

cols=st.columns(len(labels))
for i, (col,label) in enumerate(zip(cols,labels)):
    with col:
        if i == current_index:
            st.markdown(f"**🔵 {label}**")
        elif i < current_index:
            st.markdown(f"🟢 {label}")
        else:
            st.markdown(
                f"<span style='color:#aaa'>{label}</span>",
                unsafe_allow_html=True,
            )

st.divider()
st.divider()

# routers
from ui_pages import (
    upload_jd_page,
    upload_candidates_page,
    analysing_page,
    report_page,
    override_page,
)

page_map = {
    "upload_jd": upload_jd_page,
    "upload_candidates": upload_candidates_page,
    "analysing": analysing_page,
    "report": report_page,
    "override": override_page,
}
 
page_map.get(st.session_state.page, upload_jd_page).render()