import os
import datetime
from jinja2 import Environment, FileSystemLoader

from src.jd_parser import JobRequirements
from src.profile_parser import CandidateProfile
from src.scorer import CandidateScore
from src.override import get_audit_log

TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
OUTPUTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs")

# save the report as an HTML file in output dir and return path
def generate_report(
    ranked: list[tuple[int, CandidateProfile, CandidateScore]],
    jd: JobRequirements,
    filename: str = "shortlist_report.html",
) -> str:
    
    os.makedirs(OUTPUTS_DIR, exist_ok=True)

    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    template = env.get_template("report.html")

    html = template.render(
        jd=jd,
        ranked=ranked,
        overrides=get_audit_log(),
        generated_at=datetime.datetime.now().strftime("%d %b %Y, %H:%M"),
    )

    output_path = os.path.join(OUTPUTS_DIR, filename)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✓ Report saved → {output_path}")
    return output_path
