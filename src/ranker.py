from src.profile_parser import CandidateProfile
from src.scorer import CandidateScore


def rank_candidates(
    scored: list[tuple[CandidateProfile, CandidateScore]]
) -> list[tuple[int, CandidateProfile, CandidateScore]]:
    sorted_candidates = sorted(
        scored,
        key=lambda x: x[1].weighted_total,
        reverse=True
    )
    return [
        (rank + 1, profile, score)
        for rank, (profile, score) in enumerate(sorted_candidates)
    ]
