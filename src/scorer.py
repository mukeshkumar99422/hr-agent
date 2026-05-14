from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

from src.llm_factory import get_llm
from src.jd_parser import JobRequirements
from src.profile_parser import CandidateProfile

load_dotenv()


# Pydantic schema ------------------------------------------------
class DimensionScore(BaseModel):
    score: float = Field(description="Score from 0 to 10")
    justification: str = Field(description="One sentence justification for this score")


class CandidateScore(BaseModel):
    skills_match: DimensionScore = Field(
        description="How well candidate skills match JD required skills (weight 30%)"
    )
    experience_relevance: DimensionScore = Field(
        description="Relevance and seniority of work experience to the role (weight 25%)"
    )
    education_certs: DimensionScore = Field(
        description="Education level and certifications vs JD requirement (weight 15%)"
    )
    portfolio: DimensionScore = Field(
        description="Quality and relevance of projects/portfolio (weight 20%)"
    )
    communication_quality: DimensionScore = Field(
        description="Clarity and structure of resume/profile writing (weight 10%)"
    )
    weighted_total: float = Field(
        description="Weighted total 0-10 — will be recomputed by code after LLM response"
    )
    recommendation: str = Field(
        description="One of exactly: Hire, Review, No Hire"
    )


# Rubric weights ------------------------------------------------
WEIGHTS = {
    "skills_match": 0.30,
    "experience_relevance": 0.25,
    "education_certs": 0.15,
    "portfolio": 0.20,
    "communication_quality": 0.10,
}


def compute_weighted_total(score: CandidateScore) -> float:
    def clamp(v: float) -> float:
        return max(0.0, min(10.0, v))

    return round(
        clamp(score.skills_match.score) * WEIGHTS["skills_match"]
        + clamp(score.experience_relevance.score) * WEIGHTS["experience_relevance"]
        + clamp(score.education_certs.score) * WEIGHTS["education_certs"]
        + clamp(score.portfolio.score) * WEIGHTS["portfolio"]
        + clamp(score.communication_quality.score) * WEIGHTS["communication_quality"],
        2
    )


def get_recommendation(total: float) -> str:
    """Always derive in Python — never trust LLM recommendation string."""
    if total >= 7.0:
        return "Hire"
    elif total >= 5.0:
        return "Review"
    return "No Hire"


# Prompt------------------------------------------------

_SYSTEM_MESSAGE = """You are a senior HR analyst, scoring candidates against a job description.

SCORING RUBRIC (be strict and consistent):
- Skills Match (30%)       : <30% match→0-3 | 50-70%→4-6 | >85%→8-10
- Experience Relevance (25%): Unrelated→0-3 | Adjacent domain→4-6 | Exact domain+seniority→8-10
- Education & Certs (15%)  : Below minimum→0-3 | Meets minimum→4-6 | Exceeds+extra certs→8-10
- Portfolio (20%)          : No evidence→0-3 | 1-2 generic projects→4-6 | Strong relevant portfolio→8-10
- Communication Quality(10%): Poor grammar→0-3 | Adequate clarity→4-6 | Crisp+structured→8-10

IMPORTANT RULES:
1. Score each dimension 0.0–10.0. Be strict — only give 9-10 for truly exceptional matches.
2. justification for each dimension must be exactly ONE sentence.
3. weighted_total: provide your best estimate — it will be recomputed by the system anyway.
4. recommendation must be EXACTLY one of: "Hire", "Review", "No Hire" — no other values.
5. Do NOT invent information not present in the candidate data."""

_HUMAN_MESSAGE = """Score this candidate against the job description below.

--JOB DESCRIPTION--
Title              : {jd_title}
Required skills    : {required_skills}
Preferred skills   : {preferred_skills}
Min experience     : {min_exp} years
Domain             : {domain}
Seniority          : {seniority}
Education required : {education_req}
Certifications     : {certs}

--CANDIDATE PROFILE--
Name               : {name}
Skills             : {candidate_skills}
Experience         : {experience} years in {exp_domain}
Past companies     : {companies}
Education          : {candidate_edu}
Certifications     : {candidate_certs}
Projects           : {projects}
Summary            : {summary}"""

_PROMPT = ChatPromptTemplate.from_messages([
    ("system", _SYSTEM_MESSAGE),
    ("human",  _HUMAN_MESSAGE),
])


# Main score function --------------------------------------------

def score_candidate(
    candidate: CandidateProfile,
    jd: JobRequirements,
) -> CandidateScore:

    llm = get_llm()
    structured_llm = llm.with_structured_output(CandidateScore)

    chain  = _PROMPT | structured_llm
    result: CandidateScore = chain.invoke({
        # JD fields
        "jd_title":         jd.title,
        "required_skills":  ", ".join(jd.required_skills),
        "preferred_skills": ", ".join(jd.preferred_skills),
        "min_exp":          jd.min_experience_years,
        "domain":           jd.domain,
        "seniority":        jd.seniority,
        "education_req":    jd.education_requirement,
        "certs":            ", ".join(jd.certifications),
        # Candidate fields
        "name":             candidate.name,
        "candidate_skills": ", ".join(candidate.skills),
        "experience":       candidate.total_experience_years,
        "exp_domain":       candidate.experience_domain,
        "companies":        ", ".join(candidate.past_companies),
        "candidate_edu":    candidate.education,
        "candidate_certs":  ", ".join(candidate.certifications),
        "projects":         "; ".join(candidate.projects[:5]),  # max 5
        "summary":          candidate.summary[:500],
    })

    result.weighted_total = compute_weighted_total(result)
    result.recommendation = get_recommendation(result.weighted_total)

    return result