Here is a clean, professional, and comprehensive `README.md` file for your GitHub repository, tailored to the project report you provided and incorporating your demo images.

---

# HR Resume & LinkedIn Shortlisting Agent

An AI-powered agent designed to help HR teams evaluate job candidates faster and more consistently. The agent parses Job Descriptions (JDs) and batches of resumes or LinkedIn profiles, scores candidates across 5 dimensions using Google Gemini, ranks them, and generates an interactive shortlist report. It also includes an audit-logged HR override feature for manual adjustments.

---

## 🚀 Key Features

* **Multi-Format Parsing:** Extracts clean text from PDF (`pdfplumber`), DOCX (`python-docx`), and manual LinkedIn JSON exports.
* **Structured LLM Outputs:** Utilizes Gemini's native `with_structured_output()` via LangChain to guarantee valid data schemas without flaky JSON string parsing.
* **5-Dimension Rubric Scoring:** Evaluates candidates based on Skills Match (30%), Experience Relevance (25%), Portfolio (20%), Education & Certs (15%), and Communication Quality (10%).
* **Performance Optimization:** Local `SQLiteCache` implementation prevents redundant API calls for identical inputs.
* **HR Control & Audit Trail:** Allows recruiters to override scores or flag candidates, saving a transparent history with timestamps and written justifications to a local log.
* **Enterprise-Grade Security:** Equipped with input sanitization against prompt injections, local-only calculations for final scores to avoid LLM arithmetic hallucination, and PII-safe logging.

---

## 🛠️ Tech Stack

| Layer | Library / Tool | Purpose |
| --- | --- | --- |
| **LLM Engine** | Google Gemini 2.5 Flash | High-quality inference with a generous free tier (1,500 req/day). |
| **LLM Framework** | LangChain (`langchain-core`) | Structured prompt building and robust model chaining. |
| **Data Extraction** | `pdfplumber` & `python-docx` | Lightweight, reliable parsing of raw resume files. |
| **Caching Layer** | `SQLiteCache` | Saves repeated LLM responses to disk to maximize API quota efficiency. |
| **Security** | `bleach` + Regex | Strips malicious HTML and blocks prompt injection phrases. |
| **UI Framework** | Streamlit | Rapidly deploys a clean, multi-page user interface in pure Python. |
| **Reporting** | Jinja2 HTML | Generates lightweight, browser-viewable shortlisted candidate reports. |

---

## 📸 Application Walkthrough & Demos

### 1. Job Description Parsing

Upload your target Job Description as a PDF, Word document, or plain text. The AI extracts structured requirements instantly.

### 2. Candidate Resume Parsing

Batch upload candidate resumes or feed in exported LinkedIn profile JSONs. The agent standardizes the data seamlessly.

### 3. Interactive Report & Rankings

View your ranked shortlist side-by-side with individual rubric scores, detailed AI justifications, and a quick-download HTML report option.

### 4. HR Overriding & Audit Logs

recruiter-in-the-loop control allows adjusting scores or flagging specific profiles, automatically maintaining a compliance-friendly audit trail.

---

## 📂 Project Structure

```text
├── src/                          # Core backend logic modules
│   ├── cache.py                  # Local SQLite cache initialization
│   ├── sanitizer.py              # Input scrubbing (HTML stripping & injection block)
│   ├── llm_factory.py            # Centralized LLM object creation 
│   ├── jd_parser.py              # Schema-enforced Job Description extractor
│   ├── profile_parser.py         # Batch PDF/DOCX resume content parser
│   ├── linkedin_parser.py        # Normalizes raw LinkedIn JSON to standard profiles
│   ├── scorer.py                 # Multi-rubric scoring (math validated in Python)
│   ├── ranker.py                 # Core sorting logic (pure Python sorted())
│   ├── report_generator.py       # Jinja2 HTML report generator
│   └── override.py               # HR overrides and JSONL audit logger
├── pages_ui/                     # Streamlit multi-page interface screens
│   ├── page_upload_jd.py
│   ├── page_upload_candidates.py
│   ├── page_analysing.py
│   ├── page_report.py
│   └── page_override.py
├── app.py                        # Main Streamlit application entrypoint
├── .env.example                  # Template for environment variables
└── README.md                     # Documentation

```

---

## 🛡️ Security & Reliability Architecture

* **Prompt Injection Defense:** Every piece of user text goes through a strict `sanitizer.py` layer that utilizes `bleach.clean()` and custom regular expressions to destroy phrases like *"ignore previous instructions"*.
* **Deterministic Math Guard:** To bypass notorious LLM arithmetic limitations, weighted totals and core recommendations are completely computed locally in Python (`scorer.py`) instead of being trusted to the model.
* **Privacy-First Logging:** The `override_log.jsonl` saves only file references, metrics, and justifications—keeping sensitive candidate PII completely off disk logs.

---

## ⚙️ Installation & Setup

### Prerequisites

* Python 3.10+
* A Google Gemini API Key

### Step-by-Step Installation

1. **Clone the Repository:**
```bash

```



git clone https://github.com/your-username/hr-resume-shortlisting-agent.git
cd hr-resume-shortlisting-agent

```

2. **Set Up a Virtual Environment:**
   ```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

```

3. **Install Dependencies:**
```bash

```



pip install -r requirements.txt

```

4. **Configure Environment Variables:**
   Create a `.env` file in the root directory using the provided template:
   ```bash
cp .env.example .env

```

Open the `.env` file and append your API Key:

```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
LLM_PROVIDER=Gemini

```

5. **Run the Application:**
```bash

```



streamlit run app.py

```

```
