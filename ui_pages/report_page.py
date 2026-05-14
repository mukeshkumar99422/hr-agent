import os
import streamlit as st


def render():
    ranked=st.session_state.ranked
    jd=st.session_state.jd_obj

    st.subheader(f"Shortlist Report — {jd.title}")

    # Summary metrics---------------------------------------
    total=len(ranked)
    hires=sum(1 for _, _, s in ranked if s.recommendation == "Hire")
    reviews=sum(1 for _, _, s in ranked if s.recommendation == "Review")
    no_hires=sum(1 for _, _, s in ranked if s.recommendation == "No Hire")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total evaluated", total)
    c2.metric("Recommended hire", hires)
    c3.metric("For review", reviews)
    c4.metric("No hire", no_hires)

    st.divider()

    # Download button-------------------------------------
    report_path = st.session_state.get("report_path")
    if report_path and os.path.exists(report_path):
        with open(report_path, "r", encoding="utf-8") as f:
            st.download_button(
                "⬇ Download shortlist report (HTML)",
                data=f.read(),
                file_name="shortlist_report.html",
                mime="text/html",
            )

    st.divider()

    # Ranked candidates------------------------------------------
    st.markdown("### Candidate rankings")

    rec_icon = {"Hire": "🟢", "Review": "🟡", "No Hire": "🔴"}

    for rank, profile, score in ranked:
        icon = rec_icon.get(score.recommendation, "⚪")

        with st.expander(
            f"{icon}  #{rank}  {profile.name}  ·  "
            f"Total: **{score.weighted_total:.1f}/10**  ·  {score.recommendation}",
            expanded=(rank == 1),
        ):
            # Dimension metrics
            d1, d2, d3, d4, d5 = st.columns(5)
            d1.metric("Skills (30%)", f"{score.skills_match.score:.1f}")
            d2.metric("Exp (25%)", f"{score.experience_relevance.score:.1f}")
            d3.metric("Edu (15%)", f"{score.education_certs.score:.1f}")
            d4.metric("Portfolio (20%)", f"{score.portfolio.score:.1f}")
            d5.metric("Comm (10%)", f"{score.communication_quality.score:.1f}")

            # Justifications
            st.markdown("**Justifications:**")
            dims = [
                ("Skills match", score.skills_match.justification),
                ("Experience relevance", score.experience_relevance.justification),
                ("Education & certs", score.education_certs.justification),
                ("Portfolio", score.portfolio.justification),
                ("Communication", score.communication_quality.justification),
            ]
            for label, just in dims:
                st.markdown(f"- **{label}:** {just}")

            st.markdown("---")

    st.divider()
    if st.button(" HR Override / Flag candidates →", type="primary"):
        st.session_state.page = "override"
        st.rerun()