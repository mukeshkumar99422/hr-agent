import re
import bleach

# Phrases that indicate prompt injection attempts
INJECTION_PATTERNS = [
    r"ignore (all )?previous instructions?",
    r"system prompt",
    r"you are now",
    r"disregard (all )?previous",
    r"forget (all )?previous",
    r"new instructions?:",
    r"override (all )?instructions?",
    r"act as (?!a candidate|an applicant)",
]

INJECTION_REGEX = re.compile(
    "|".join(INJECTION_PATTERNS),
    flags=re.IGNORECASE
)

# 1. Strip all HTML tags (resume may contain HTML artifacts)
# 2. Remove prompt injection phrases
# 3. Collapse excessive whitespace
def sanitize(text: str) -> str:
    if not text or not isinstance(text, str):
        return ""

    # Step 1: strip HTML
    text = bleach.clean(text, tags=[], strip=True)

    # Step 2: remove injection patterns
    text = INJECTION_REGEX.sub("", text)

    # Step 3: collapse whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" {2,}", " ", text)

    return text.strip()


def sanitize_dict(data: dict) -> dict:
    """Recursively sanitize all string values in a dict (for LinkedIn JSON)."""
    cleaned = {}
    for key, value in data.items():
        if isinstance(value, str):
            cleaned[key] = sanitize(value)
        elif isinstance(value, dict):
            cleaned[key] = sanitize_dict(value)
        elif isinstance(value, list):
            cleaned[key] = [
                sanitize(v) if isinstance(v, str)
                else sanitize_dict(v) if isinstance(v, dict)
                else v
                for v in value
            ]
        else:
            cleaned[key] = value
    return cleaned

