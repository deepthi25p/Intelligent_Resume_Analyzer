"""
Intelligent Resume Analyzer
============================
Parses resumes, matches candidates to job requirements,
calculates match scores, and generates detailed hiring reports.
"""

import re
import json
import os
from datetime import datetime


# ─────────────────────────────────────────────
#  SECTION 1 ─ RESUME PARSER
# ─────────────────────────────────────────────

def extract_name(text: str) -> str:
    """Extract candidate name from the first non-empty line."""
    for line in text.strip().splitlines():
        line = line.strip()
        if line and not re.search(r'[@\d]', line):
            return line
    return "Unknown"


def extract_email(text: str) -> str:
    """Extract email address using regex."""
    match = re.search(r'[\w.\-+]+@[\w.\-]+\.\w+', text)
    return match.group() if match else "Not found"


def extract_phone(text: str) -> str:
    """Extract phone number."""
    match = re.search(r'(\+?\d[\d\s\-().]{7,}\d)', text)
    return match.group().strip() if match else "Not found"


def extract_skills(text: str) -> list[str]:
    """Extract skills by scanning for a Skills section or common tech keywords."""
    skills = []

    # Try to find a skills section
    skills_section = re.search(
        r'(?:skills?|technical skills?|core competencies)[:\s]*(.*?)(?:\n\n|\Z)',
        text, re.IGNORECASE | re.DOTALL
    )
    if skills_section:
        raw = skills_section.group(1)
        # Split by comma, pipe, bullet, newline
        tokens = re.split(r'[,|\n•\-–]+', raw)
        skills = [t.strip() for t in tokens if 2 < len(t.strip()) < 40]

    # Fallback: scan for known tech keywords
    if not skills:
        known = [
            'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'R',
            'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'SQLite',
            'Django', 'Flask', 'FastAPI', 'React', 'Angular', 'Vue',
            'Node.js', 'Express', 'Spring',
            'Machine Learning', 'Deep Learning', 'NLP', 'TensorFlow', 'PyTorch',
            'Keras', 'Scikit-learn', 'Pandas', 'NumPy', 'Matplotlib', 'Seaborn',
            'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Git', 'GitHub',
            'Linux', 'REST API', 'GraphQL', 'HTML', 'CSS', 'Tableau', 'Power BI',
            'Excel', 'Agile', 'Scrum', 'JIRA', 'CI/CD',
        ]
        skills = [k for k in known if re.search(rf'\b{re.escape(k)}\b', text, re.IGNORECASE)]

    return list(dict.fromkeys(skills))  # deduplicate while preserving order


def extract_experience_years(text: str) -> float:
    """Estimate total years of experience from date ranges in text."""
    # Match patterns like "Jan 2019 – Mar 2022" or "2018 - 2021"
    date_ranges = re.findall(
        r'(\d{4})\s*[-–to]+\s*(present|\d{4})',
        text, re.IGNORECASE
    )
    total_years = 0.0
    current_year = datetime.now().year
    for start, end in date_ranges:
        end_year = current_year if end.lower() == 'present' else int(end)
        diff = end_year - int(start)
        if 0 < diff < 50:
            total_years += diff
    return round(total_years, 1) if total_years else 0.0


def extract_education(text: str) -> str:
    """Extract highest education level mentioned."""
    levels = [
        (r'\bph\.?d\b|\bdoctor\b', 'PhD'),
        (r'\bm\.?tech\b|\bm\.?sc\b|\bmasters?\b|\bm\.?e\b', 'Masters'),
        (r'\bb\.?tech\b|\bb\.?sc\b|\bbachelors?\b|\bb\.?e\b', 'Bachelors'),
        (r'\bdiploma\b', 'Diploma'),
        (r'\bhigh school\b|\bh\.?s\.?c\b|\bssc\b', 'High School'),
    ]
    for pattern, level in levels:
        if re.search(pattern, text, re.IGNORECASE):
            return level
    return "Not specified"


def parse_resume(text: str) -> dict:
    """Parse resume text and return structured candidate data."""
    return {
        "name":             extract_name(text),
        "email":            extract_email(text),
        "phone":            extract_phone(text),
        "skills":           extract_skills(text),
        "experience_years": extract_experience_years(text),
        "education":        extract_education(text),
        "raw_length":       len(text.split()),
    }


# ─────────────────────────────────────────────
#  SECTION 2 ─ MATCHING ALGORITHM
# ─────────────────────────────────────────────

EDUCATION_RANK = {
    'PhD': 5, 'Masters': 4, 'Bachelors': 3,
    'Diploma': 2, 'High School': 1, 'Not specified': 0,
}


def calculate_match_score(candidate: dict, job: dict) -> dict:
    """
    Calculate a 0–100 match score across four weighted dimensions:
      - Skills match      : 50%
      - Experience match  : 30%
      - Education match   : 10%
      - Resume quality    : 10%
    """
    breakdown = {}

    # 1. Skills (50 pts)
    required  = {s.lower() for s in job.get("required_skills", [])}
    preferred = {s.lower() for s in job.get("preferred_skills", [])}
    candidate_skills = {s.lower() for s in candidate.get("skills", [])}

    req_match  = len(required  & candidate_skills) / max(len(required),  1)
    pref_match = len(preferred & candidate_skills) / max(len(preferred), 1)
    skills_score = round((req_match * 0.8 + pref_match * 0.2) * 50, 1)
    breakdown["skills"] = {
        "score":            skills_score,
        "max":              50,
        "required_matched": sorted(required  & candidate_skills),
        "preferred_matched":sorted(preferred & candidate_skills),
        "missing_required": sorted(required  - candidate_skills),
    }

    # 2. Experience (30 pts)
    min_exp  = job.get("min_experience_years", 0)
    max_exp  = job.get("max_experience_years", 20)
    cand_exp = candidate.get("experience_years", 0)
    if cand_exp >= min_exp:
        exp_ratio = min(cand_exp / max(max_exp, 1), 1.0)
        exp_score = round(exp_ratio * 30, 1)
    else:
        exp_score = round((cand_exp / max(min_exp, 1)) * 15, 1)  # partial credit
    breakdown["experience"] = {
        "score":           exp_score,
        "max":             30,
        "candidate_years": cand_exp,
        "required_range":  f"{min_exp}–{max_exp} years",
    }

    # 3. Education (10 pts)
    required_edu  = job.get("required_education", "Bachelors")
    candidate_edu = candidate.get("education", "Not specified")
    edu_ok  = EDUCATION_RANK.get(candidate_edu, 0) >= EDUCATION_RANK.get(required_edu, 0)
    edu_score = 10 if edu_ok else 5
    breakdown["education"] = {
        "score":     edu_score,
        "max":       10,
        "candidate": candidate_edu,
        "required":  required_edu,
        "meets":     edu_ok,
    }

    # 4. Resume quality (10 pts) — based on word count & contact info
    quality = 0
    if candidate.get("email") != "Not found":     quality += 3
    if candidate.get("phone") != "Not found":     quality += 2
    if candidate.get("raw_length", 0) >= 200:     quality += 3
    if len(candidate.get("skills", [])) >= 5:     quality += 2
    breakdown["quality"] = {"score": quality, "max": 10}

    total = round(skills_score + exp_score + edu_score + quality, 1)
    return {"total": min(total, 100), "breakdown": breakdown}


def get_recommendation(score: float) -> str:
    if score >= 80:
        return "🟢 STRONG HIRE — Exceptional match. Schedule technical interview immediately."
    elif score >= 65:
        return "🟡 RECOMMENDED — Good match. Proceed with initial screening call."
    elif score >= 45:
        return "🟠 MAYBE — Partial match. Consider if pipeline is thin."
    else:
        return "🔴 NOT RECOMMENDED — Significant skill/experience gaps."


# ─────────────────────────────────────────────
#  SECTION 3 ─ FILE OPERATIONS (JSON)
# ─────────────────────────────────────────────

def save_results(data: dict, filepath: str) -> None:
    """Save analysis results to a JSON file."""
    os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ Results saved → {filepath}")


def load_results(filepath: str) -> dict:
    """Load previously saved results from JSON."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


# ─────────────────────────────────────────────
#  SECTION 4 ─ REPORT GENERATOR
# ─────────────────────────────────────────────

def generate_report(candidate: dict, job: dict, match: dict) -> str:
    """Generate a clean, professional text report."""
    bd   = match["breakdown"]
    sep  = "═" * 60

    lines = [
        sep,
        "         INTELLIGENT RESUME ANALYZER — REPORT",
        sep,
        f"  Generated   : {datetime.now().strftime('%d %b %Y, %I:%M %p')}",
        f"  Job Title   : {job.get('title', 'N/A')}",
        f"  Department  : {job.get('department', 'N/A')}",
        sep,
        "",
        "  CANDIDATE PROFILE",
        "  " + "─" * 40,
        f"  Name        : {candidate['name']}",
        f"  Email       : {candidate['email']}",
        f"  Phone       : {candidate['phone']}",
        f"  Education   : {candidate['education']}",
        f"  Experience  : {candidate['experience_years']} years",
        f"  Skills ({len(candidate['skills'])}): {', '.join(candidate['skills'][:10])}",
        "",
        "  MATCH SCORE BREAKDOWN",
        "  " + "─" * 40,
        f"  Skills      : {bd['skills']['score']:5.1f} / 50",
        f"  Experience  : {bd['experience']['score']:5.1f} / 30",
        f"  Education   : {bd['education']['score']:5.1f} / 10",
        f"  Quality     : {bd['quality']['score']:5.1f} / 10",
        "  " + "─" * 20,
        f"  TOTAL SCORE : {match['total']:5.1f} / 100",
        "",
        "  RECOMMENDATION",
        "  " + "─" * 40,
        f"  {get_recommendation(match['total'])}",
        "",
    ]

    missing = bd['skills'].get('missing_required', [])
    if missing:
        lines += [
            "  SKILL GAPS (Required but missing)",
            "  " + "─" * 40,
        ]
        for skill in missing:
            lines.append(f"  ✗ {skill}")
        lines.append("")

    matched_req  = bd['skills'].get('required_matched', [])
    matched_pref = bd['skills'].get('preferred_matched', [])
    if matched_req or matched_pref:
        lines += ["  MATCHED SKILLS", "  " + "─" * 40]
        for skill in matched_req:
            lines.append(f"  ✓ {skill} (required)")
        for skill in matched_pref:
            lines.append(f"  ✓ {skill} (preferred)")
        lines.append("")

    lines.append(sep)
    return "\n".join(lines)


# ─────────────────────────────────────────────
#  SECTION 5 ─ MAIN ORCHESTRATOR
# ─────────────────────────────────────────────

def analyze_resume(resume_text: str, job: dict, save_path: str = None) -> dict:
    """
    Full pipeline:
      1. Parse resume text
      2. Calculate match score
      3. Generate report
      4. Optionally save JSON
    Returns the complete result dict.
    """
    candidate = parse_resume(resume_text)
    match     = calculate_match_score(candidate, job)
    report    = generate_report(candidate, job, match)

    result = {
        "timestamp": datetime.now().isoformat(),
        "job":       job,
        "candidate": candidate,
        "match":     match,
        "report":    report,
    }

    if save_path:
        save_results(result, save_path)

    return result
