import os
import streamlit as st
from src.profile_parser import parse_resume
from src.linkedin_parser import parse_linkedin
from src.scorer import score_candidate
from src.ranker import rank_candidates
from src.report_generator import generate_report

def render():
    st.subheader("Analysing candidates...")
    st.caption("Gemini 2.0 Flash is scoring each candidates against the rubric.")

    jd=st.session_state.jd_obj
    scored_pairs=[]
    errors=[]

    all_sources=(
        [("resume", p) for p in st.session_state.get("resume_files",[])]
        +[("linkedin_json",p) for p in st.session_state.get("linkedin_profiles",[])]
        +[("linkedin_url", u) for u in st.session_state.get("linkedin_urls",[])]
    )
    total=len(all_sources)
    if total == 0:
        st.warning("No candidates found. Go back and upload resumes or LinkedIn profiles.")
        if st.button("← Go back"):
            st.session_state.page = "upload_candidates"
            st.rerun()
        return
    
    progress=st.progress(0,text="Starting...")
    status=st.container()

    for i, (source_type, source) in enumerate(all_sources):
        if source_type=="resume":
            label=os.path.basename(source)
        elif source_type=="linkedin_json":
            label=(
                f"{source.get('firstName','')} "
                f"{source.get('lastName','')} (LinkedIn JSON)"
            ).strip()
        else:
            label=f"LinkedIn URL: {source}"

        progress.progress(i/total, text=f"Parsing: {label}")
        status.write(f"Parsing: **{label}**")

        try:
            if source_type=="resume":
                profile=parse_resume(source)
            elif source_type=="linkedin_json":
                profile=parse_linkedin(source)
            else:
                status.info(f"URL profiles need a JSON export - skipping {source}")
                continue
            
            progress.progress((i+0.5)/total, text=f"Scoring: {profile.name}")
            status.write(f"Scoring: **{profile.name}**")

            score=score_candidate(profile,jd)
            scored_pairs.append((profile,score))
            status.write(
                f"**{profile.name}** - "
                f"{score.weighted_total:.1f}/10 · {score.recommendation}"
            )

        except Exception as e:
            errors.append(f"{label}: {e}")
            status.error(f"x Failed: {label} - {e}")
        
        progress.progress((i+1)/total,text=f"Done: {i+1}/{total}")
    
    progress.empty()

    if not scored_pairs:
        st.error("No candidates could be scored. Check your input files.")
        if st.button("<- Go back"):
            st.session_state.page="upload_candidates"
            st.rerun()
        return

    # save results to session state
    ranked=rank_candidates(scored_pairs)
    st.session_state.ranked=ranked
    st.session_state.scored_map={p.name: s for _,p,s in ranked}
    st.session_state.profile_map={p.name: p for _,p,s in ranked}
    st.session_state.report_path=generate_report(ranked,jd)

    if errors:
        st.warning(f"{len(errors)} files failed = see above.")

    st.success(f"✓ {len(scored_pairs)} candidate(s) scored. Loading report…")
    st.session_state.page = "report"
    st.rerun()