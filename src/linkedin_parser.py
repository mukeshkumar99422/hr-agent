import json
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

from src.sanitizer import sanitize, sanitize_dict
from src.llm_factory import get_llm
from src.profile_parser import CandidateProfile

load_dotenv()


# Prompt ------------------------------------------------

_SYSTEM_MESSAGE = """You are an expert linkedin profile parser, you have to extract information in JSON format from a LinkedIn profile.

Rules you must follow:
1. Extract information ONLY from the data provided — do NOT invent data.
2. skills must be individual names e.g. "Python", "LangChain".
3. total_experience_years: calculate from the roles listed — use a float.
4. If a field is missing, return an empty string or empty list.
5. source_file will be set by the system — leave it as empty string."""

_HUMAN_MESSAGE = """Parse this LinkedIn profile(provided in json string format) and extract structured candidate information in JSON format:

\"\"\"
{linkedin_profile_json}
\"\"\""""

_PROMPT = ChatPromptTemplate.from_messages([
    ("system", _SYSTEM_MESSAGE),
    ("human",  _HUMAN_MESSAGE),
])


# Main parse function --------------------------------------------

def parse_linkedin(source) -> CandidateProfile:
    if isinstance(source, str):
        with open(source, "r", encoding="utf-8") as f:
            data = json.load(f)
    elif isinstance(source, dict):
        data = source
    else:
        raise ValueError("source must be a file path string or a dict")

    # Sanitize all string values to prevent prompt injection
    data = sanitize_dict(data)

    # Flatten JSON → plain text → sanitize → truncate
    profile_text = json.dumps(data)

    llm = get_llm()
    structured_llm = llm.with_structured_output(CandidateProfile)

    chain = _PROMPT | structured_llm
    profile: CandidateProfile = chain.invoke({"linkedin_profile_json": profile_text})

    # source_file set by code — not LLM
    profile.source_file = "linkedin"
    return profile

