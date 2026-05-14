import os
import json
import tempfile
import streamlit as st
from src.jd_parser import JobRequirements

def render():
    jd:JobRequirements=st.session_state.jd_obj

    # parsed jd summary
    with st.expander("Parsed JD — click to review", expanded=False):
        st.markdown(
            f"**{jd.title}** · {jd.min_experience_years}+ yrs "
            f"· {jd.domain} · {jd.seniority}"
        )
        st.markdown(
            "**Required skills:** "
            + " · ".join([f"`{s}`" for s in jd.required_skills])
        )
        if jd.preferred_skills:
            st.markdown(
                "**Preferred:** "
                + " · ".join([f"`{s}`" for s in jd.preferred_skills])
            )

    st.divider()

    # Resume pdf/docx------------------------------------------------------
    st.subheader("Upload Resumes")
    st.caption("PDF or DOCX · Select multiple files at once")

    resume_uploads=st.file_uploader(
        "Resume files",
        type=["pdf","docx"],
        accept_multiple_files=True,
        label_visibility="collapsed",
        key="resume_file_uploader"
    )

    if resume_uploads:
        save_dir=tempfile.mkdtemp()
        saved=[]
        for f in resume_uploads:
            path=os.path.join(save_dir,f.name)
            with open(path,"wb") as out:
                out.write(f.read())
            saved.append(path)
        st.session_state.resume_files=saved

    if st.session_state.get("resume_files"):
        st.write(f"**{len(st.session_state.resume_files)} resume(s) ready**")
    
    st.divider()

    # LinkedIn Profiles-----------------------------------------
    st.subheader("LinkedIn Profiles")
    li_tab1, li_tab2=st.tabs(["JSON export", "Profile URL"])

    with li_tab1:
        st.caption("Me → Settings → Data Privacy → Get a copy → Profile")
        li_files=st.file_uploader(
            "LinkedIn JSON",
            type=["json"],
            label_visibility="collapsed",
            accept_multiple_files=True,
            key="li_uploader"
        )
        if li_files:
            for f in li_files:
                try:
                    data=json.load(f)
                    name = f"{data.get('firstName', '')} {data.get('lastName', '')}".strip()
                    existing=[
                        f"{p.get('firstName','')} {p.get('lastName','')}".strip()
                        for p in st.session_state.get("linkedin_profiles", [])
                    ]
                    if name not in existing:
                        st.session_state.linkedin_profiles.append(data)
                except Exception as e:
                    st.error(f"Could not parse {f.name}: {e}")
    
    with li_tab2:
        st.info("This Functionality is not implemented yet. Please use the JSON export method for now.")
    
    total_li=(
        len(st.session_state.get("linkedin_profiles",[]))
        + len(st.session_state.get("linkedin_urls",[]))
    )
    if total_li:
        st.write(f"**{total_li} LinkedIn profile(s) ready:**")
    
    st.divider()


    # run button---------------------------------
    total_candidates=len(st.session_state.get("resume_files",[]))+total_li
    has_candidates=total_candidates>0

    if not has_candidates:
        st.info("Upload at least one resume or LinkedIn profile to continue.")

    if st.button(
        f"Analyse {total_candidates} candidate(s) →",
        type="primary",
        disabled=not has_candidates,
        key="analyse_btn",
    ):
        st.session_state.page = "analysing"
        st.rerun()
        