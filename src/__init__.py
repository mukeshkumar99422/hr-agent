from src.cache       import setup_cache
from src.llm_factory import get_llm

from src.sanitizer import sanitize, sanitize_dict

from src.jd_parser      import parse_jd,      JobRequirements
from src.profile_parser import (
    parse_resume,
    load_all_resumes,
    CandidateProfile,
    extract_text,
)
from src.linkedin_parser import (
    parse_linkedin,
)

from src.scorer     import (
    score_candidate,
    CandidateScore,
    DimensionScore,
    compute_weighted_total,
    get_recommendation,
    WEIGHTS,
)
from src.ranker import rank_candidates

from src.report_generator import generate_report

from src.override import (
    apply_override,
    flag_candidate,
    get_audit_log,
    VALID_DIMENSIONS,
)

__all__ = [
    # setup
    "setup_cache",
    "get_llm",

    # security
    "sanitize",
    "sanitize_dict",

    # schemas
    "JobRequirements",
    "CandidateProfile",
    "CandidateScore",
    "DimensionScore",

    # input parsers
    "parse_jd",
    "parse_resume",
    "load_all_resumes",
    "extract_text",
    "parse_linkedin",

    # scoring
    "get_skills_score",
    "skill_similarity",
    "score_candidate",
    "compute_weighted_total",
    "get_recommendation",
    "WEIGHTS",

    # ranking
    "rank_candidates",

    # output
    "generate_report",

    # HITL
    "apply_override",
    "flag_candidate",
    "get_audit_log",
    "VALID_DIMENSIONS",
]