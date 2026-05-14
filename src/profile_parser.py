import os
import pdfplumber
from docx import Document
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

from src.sanitizer import sanitize
from src.llm_factory import get_llm

load_dotenv()


# Pydantic schema of profile-------------------------------------------------

class CandidateProfile(BaseModel):
    name: str = Field(description="Full name of the candidate")
    email: str = Field(default="", description="Email address, empty string if not found")
    phone: str = Field(default="", description="Phone number, empty string if not found")
    skills: list[str] = Field(description="All technical and soft skills listed")
    total_experience_years: float = Field(description="Total years of work experience as a float e.g. 4.5")
    experience_domain: str = Field(description="Primary domain e.g. ML engineering, data analysis")
    past_companies: list[str] = Field(default=[], description="List of companies worked at")
    education: str = Field(default="", description="Highest education qualification")
    certifications: list[str] = Field(default=[], description="Professional certifications")
    projects: list[str] = Field(default=[], description="Project titles or brief descriptions")
    summary: str = Field(default="", description="Candidate summary or objective statement")
    source_file: str = Field(default="", description="Source filename — set by code, not LLM")


# resume text extractor -------------------------------------------------

def _extract_pdf(path: str) -> str:
    try:
        with pdfplumber.open(path) as pdf:
            pages = [p.extract_text() or "" for p in pdf.pages]
        return "\n".join(pages)
    except Exception as e:
        raise RuntimeError(f"Failed to read PDF {path}: {e}")


def _extract_docx(path: str) -> str:
    try:
        doc = Document(path)
        return "\n".join(p.text for p in doc.paragraphs)
    except Exception as e:
        raise RuntimeError(f"Failed to read DOCX {path}: {e}")


def extract_text(path: str) -> str:
    ext = path.rsplit(".", 1)[-1].lower()
    if ext == "pdf":
        return _extract_pdf(path)
    elif ext == "docx":
        return _extract_docx(path)
    raise ValueError(f"Unsupported resume format: .{ext}. Use PDF or DOCX.")


# Prompt ------------------------------------------------

_SYSTEM_MESSAGE = """You are an expert resume parser, you have to extract information in JSON format from a resume.

Rules you must follow:
1. Extract information ONLY from the resume text — do NOT invent data.
2. skills must be individual names e.g. "Python", "Docker", "Communication".
3. total_experience_years must be a float e.g. 4.5 — calculate from roles.
4. projects must be short one-line descriptions, one item per project.
5. If a field is missing from the resume, return an empty string or empty list.
6. Do NOT include PII like passport numbers or national IDs in any field."""

_HUMAN_MESSAGE = """Parse this resume and extract structured candidate information in JSON format:

\"\"\"
{resume_text}
\"\"\""""

_PROMPT = ChatPromptTemplate.from_messages([
    ("system", _SYSTEM_MESSAGE),
    ("human",  _HUMAN_MESSAGE),
])


# parse every resume using llm -----------------------------------------------

def parse_resume(file_path: str) -> CandidateProfile:
    raw_text  = extract_text(file_path)
    clean_text = sanitize(raw_text)
    truncated = clean_text[:4000]   # enough for any resume

    llm = get_llm()
    structured_llm = llm.with_structured_output(CandidateProfile)

    chain  = _PROMPT | structured_llm
    profile: CandidateProfile = chain.invoke({"resume_text": truncated})

    # source_file is set by code — not asked from LLM
    profile.source_file = os.path.basename(file_path)
    return profile


def load_all_resumes(folder_path: str) -> list[CandidateProfile]:
    profiles  = []
    supported = (".pdf", ".docx")

    files = [f for f in os.listdir(folder_path) if f.lower().endswith(supported)]

    if not files:
        print(f"⚠ No PDF/DOCX files found in {folder_path}")
        return profiles

    for fname in files:
        full_path = os.path.join(folder_path, fname)
        try:
            profile = parse_resume(full_path)
            profiles.append(profile)
            print(f"  ✓ Parsed: {fname} → {profile.name}")
        except Exception as e:
            print(f"  ✗ Failed: {fname} — {e}")

    return profiles
