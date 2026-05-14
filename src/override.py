import json
import datetime
import os

from src.scorer import CandidateScore, compute_weighted_total, get_recommendation

LOG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "outputs",
    "override_log.jsonl"
)

VALID_DIMENSIONS = [
    "skills_match",
    "experience_relevance",
    "education_certs",
    "portfolio",
    "communication_quality",
]

# Apply a score override to a CandidateScore object.
# Recalculates weighted_total and recommendation.
# Logs the change to override_log.jsonl.
# Returns the updated CandidateScore.
def apply_override(
    candidate_name: str,
    score: CandidateScore,
    dimension: str,
    new_score: float,
    reason: str,
    overridden_by: str = "HR",
) -> CandidateScore:
    
    # Validate inputs
    if dimension not in VALID_DIMENSIONS:
        raise ValueError(
            f"Invalid dimension '{dimension}'. "
            f"Choose from: {VALID_DIMENSIONS}"
        )
    if not (0.0 <= new_score <= 10.0):
        raise ValueError(f"new_score must be between 0 and 10, got {new_score}")

    # Get old score for logging
    old_score = getattr(score, dimension).score

    # Apply override
    dim_obj = getattr(score, dimension)
    dim_obj.score = round(new_score, 1)
    dim_obj.justification += f" [HR override: {reason}]"

    # Recompute total
    score.weighted_total = compute_weighted_total(score)
    score.recommendation = get_recommendation(score.weighted_total)

    # Log to audit file
    _log_override(
        candidate_name=candidate_name,
        dimension=dimension,
        old_score=old_score,
        new_score=new_score,
        new_total=score.weighted_total,
        new_recommendation=score.recommendation,
        reason=reason,
        overridden_by=overridden_by,
    )

    return score


def flag_candidate(
    candidate_name: str,
    reason: str,
    flagged_by: str = "HR",
) -> dict:
    """
    Flag a candidate for manual review.
    Logs the flag and returns the log entry.
    """
    entry = {
        "type": "flag",
        "timestamp": datetime.datetime.now().isoformat(),
        "candidate": candidate_name,
        "reason": reason,
        "flagged_by": flagged_by,
    }
    _write_log(entry)
    return entry


def get_audit_log() -> list[dict]:
    """Read and return all audit log entries."""
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    if not os.path.exists(LOG_PATH):
        return []
    entries = []
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return entries


def _log_override(
    candidate_name: str,
    dimension: str,
    old_score: float,
    new_score: float,
    new_total: float,
    new_recommendation: str,
    reason: str,
    overridden_by: str,
):
    entry = {
        "type": "override",
        "timestamp": datetime.datetime.now().isoformat(),
        "candidate": candidate_name,
        "dimension": dimension,
        "old_score": old_score,
        "new_score": new_score,
        "new_total": new_total,
        "new_recommendation": new_recommendation,
        "reason": reason,
        "overridden_by": overridden_by,
    }
    _write_log(entry)


def _write_log(entry: dict):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
