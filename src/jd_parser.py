import os
import pdfplumber
from docx import Document
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

from src.sanitizer import sanitize
from src.llm_factory import get_llm

load_dotenv()


# Pydantic schema-------------------------------------------------

class JobRequirements(BaseModel):
    title: str = Field(description="Job title")
    required_skills: list[str] = Field(description="Must-have technical skills")
    preferred_skills: list[str] = Field(description="Nice-to-have skills")
    min_experience_years: int = Field(description="Minimum years of experience required")
    education_requirement: str = Field(description="Minimum education e.g. B.Tech CS")
    certifications: list[str] = Field(description="Preferred or required certifications")
    domain: str = Field(description="Industry domain e.g. fintech, ML engineering")
    seniority: str = Field(description="Seniority level e.g. senior, mid-level, junior")
    responsibilities: list[str] = Field(description="Key responsibilities listed")
    raw_text: str = Field(default="", description="Full raw JD text (passed through, not LLM generated)")


# JD Text extractor----------------------------------------------------

def _load_pdf(path: str) -> str:
    with pdfplumber.open(path) as pdf:
        pages = [p.extract_text() or "" for p in pdf.pages]
    return "\n".join(pages)


def _load_docx(path: str) -> str:
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs)


def _load_txt(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
 
def load_jd_text(source: str) -> str:
    if os.path.isfile(source):
        ext = source.rsplit(".", 1)[-1].lower()
        loaders = {"pdf": _load_pdf, "docx": _load_docx, "txt": _load_txt}
        if ext not in loaders:
            raise ValueError(f"Unsupported file type: .{ext}")
        return loaders[ext](source)
    return source  # treat as raw pasted text


# Prompt------------------------------------------------------

_SYSTEM_MESSAGE = """You are an expert jd parser, you have to extract information in JSON format from a job description.

Rules you must follow:
1. Extract information ONLY from the text provided — do NOT invent data.
2. required_skills must be individual skill names e.g. "Python", "LangChain".
3. If a field has no data in the JD, return an empty string or empty list.
4. seniority must be one of: junior, mid-level, senior, lead, principal.
5. min_experience_years must be an integer — use 0 if not stated."""

_HUMAN_MESSAGE = """Parse this job description and extract structured information in JSON format:

\"\"\"
{jd_text}
\"\"\""""

_PROMPT = ChatPromptTemplate.from_messages([
    ("system", _SYSTEM_MESSAGE),
    ("human",  _HUMAN_MESSAGE),
])


# Main parse function--------------------------------------------

def parse_jd(source: str) -> JobRequirements:
    raw_text = load_jd_text(source)
    clean_text = sanitize(raw_text)
    truncated = clean_text[:6000]

    llm = get_llm()
    structured_llm = llm.with_structured_output(JobRequirements)

    chain = _PROMPT | structured_llm
    result: JobRequirements = chain.invoke({"jd_text": truncated})

    result.raw_text = raw_text
    return result
 