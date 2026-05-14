import tempfile
import streamlit as st
from src.jd_parser import parse_jd

def render():
    st.subheader("Upload Job Description")
    st.caption("Upload a PDF, DOCX, or TXT — or paste the text directly.")

    tab1, tab2 = st.tabs(["📁 Upload file", "📝 Paste text"])

    with tab1:
        uploaded=st.file_uploader(
            "Job Description File",
            type=["pdf","docx","txt"],
            label_visibility="collapsed",
            key="jd_file_uploader"
        )

        if uploaded:
            ext=uploaded.name.split(".",1)[-1]
            tmp=tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}")
            tmp.write(uploaded.read())
            tmp.close()
            st.session_state.jd_file_path=tmp.name
            st.session_state.jd_name=uploaded.name

    with tab2:
        pasted=st.text_area(
            "Job Description Text",
            height=200,
            placeholder="Paste the job description here...",
            label_visibility="collapsed",
            key="jd_paste"
        )
        if st.button("Use Pasted Text", key="use_paste"):
            if pasted.strip():
                tmp=tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8")
                tmp.write(pasted)
                tmp.close()
                st.session_state.jd_file_path=tmp.name
                st.session_state.jd_name="pasted_jd.txt"

            else:
                st.warning("Please paste some text first.")

    
    # Display uploaded or pasted JD
    if st.session_state.get("jd_file_path"):
        st.success(f"✓ Loaded: **{st.session_state.jd_name}**")

        if st.button("Parse job description →", type="primary", key="parse_jd_btn"):
            with st.spinner("Parsing job description with LLM…"):
                try:
                    jd=parse_jd(st.session_state.jd_file_path)
                    st.session_state.jd_obj=jd
                    st.session_state.page="upload_candidates"
                    st.rerun()
                except Exception as e:
                    st.error(f"Parsing failed: {e}")

    else:
        st.info("Upload or paste a job description to continue.")
