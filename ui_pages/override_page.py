import streamlit as st
from src.override import (
    apply_override,
    flag_candidate,
    get_audit_log,
    VALID_DIMENSIONS,
)
from src.ranker import rank_candidates
from src.report_generator import generate_report


def render():
    st.subheader("HR Override Panel")
    st.caption("Adjust scores or flag candidates. All changes are logged.")

    candidate_names = list(st.session_state.get("scored_map", {}).keys())

    if not candidate_names:
        st.warning("No scored candidates available.")
        return

    # Override form---------------------------------------
    st.markdown("### Override a score")

    col1, col2 = st.columns(2)
    with col1:
        candidate = st.selectbox("Candidate", candidate_names, key="ov_candidate")
    with col2:
        dimension = st.selectbox(
            "Dimension",
            VALID_DIMENSIONS,
            format_func=lambda x: x.replace("_", " ").title(),
            key="ov_dimension",
        )

    if candidate and dimension:
        score_obj = st.session_state.scored_map[candidate]
        current   = getattr(score_obj, dimension).score

        col3, col4 = st.columns(2)
        with col3:
            st.metric("Current score", f"{current:.1f}/10")
        with col4:
            new_score = st.number_input(
                "New score (0–10)",
                min_value=0.0,
                max_value=10.0,
                value=current,
                step=0.5,
                key="ov_new_score",
            )

    reason = st.text_input(
        "Reason for override (required)",
        placeholder="e.g. Candidate has fintech consulting exp not shown in resume",
        key="ov_reason",
    )

    if st.button("Save override", key="save_override_btn"):
        if not reason.strip():
            st.error("Please provide a reason before saving.")
        else:
            try:
                updated = apply_override(
                    candidate_name=candidate,
                    score=st.session_state.scored_map[candidate],
                    dimension=dimension,
                    new_score=new_score,
                    reason=reason,
                )
                st.session_state.scored_map[candidate] = updated
                st.success(
                    f"✓ Saved. {candidate} → "
                    f"{updated.weighted_total:.1f}/10 · {updated.recommendation}"
                )
                # Re-rank and regenerate report
                pairs = [
                    (st.session_state.profile_map[n], st.session_state.scored_map[n])
                    for n in candidate_names
                ]
                ranked = rank_candidates(pairs)
                st.session_state.ranked      = ranked
                st.session_state.report_path = generate_report(ranked, st.session_state.jd_obj)
            except Exception as e:
                st.error(f"Override failed: {e}")

    st.divider()

    # Flag form----------------------------------------------------
    st.markdown("### Flag for manual review")

    flag_name   = st.selectbox("Candidate to flag", candidate_names, key="flag_name")
    flag_reason = st.text_input(
        "Flag reason",
        placeholder="e.g. Portfolio links broken — cannot verify projects",
        key="flag_reason",
    )
    if st.button("Flag candidate", key="flag_btn"):
        if not flag_reason.strip():
            st.error("Please provide a reason.")
        else:
            flag_candidate(flag_name, flag_reason)
            st.success(f"✓ {flag_name} flagged for review.")

    st.divider()

    # Audit log--------------------------------------------
    st.markdown("### Audit log")
    log = get_audit_log()

    if not log:
        st.info("No overrides or flags yet.")
    else:
        for entry in reversed(log):
            ts = entry.get("timestamp", "")[:16]
            if entry.get("type") == "override":
                st.markdown(
                    f"🟢 `{ts}` **Override** — {entry['candidate']} · "
                    f"{entry['dimension'].replace('_',' ').title()} "
                    f"{entry['old_score']} → {entry['new_score']} · "
                    f"*{entry['reason']}*"
                )
            else:
                st.markdown(
                    f"🟡 `{ts}` **Flag** — {entry['candidate']} · *{entry['reason']}*"
                )

    st.divider()
    if st.button("← Back to report", key="back_report_btn"):
        st.session_state.page = "report"
        st.rerun()