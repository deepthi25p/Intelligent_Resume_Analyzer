"""
main.py  ─  Intelligent Resume Analyzer  ─  Entry Point
=========================================================
Run this file to analyse resumes against a job description.
Usage:
    python main.py                  # uses built-in sample data
    python main.py --interactive    # paste your own resume + job desc
"""

import argparse
import json
import os
from resume_analyzer import analyze_resume

# ─────────────────────────────────────────────
#  SAMPLE DATA
# ─────────────────────────────────────────────

SAMPLE_JOB = {
    "title":                "Senior Data Scientist",
    "department":           "Analytics & AI",
    "required_skills":      ["Python", "Machine Learning", "SQL", "Pandas", "Scikit-learn"],
    "preferred_skills":     ["TensorFlow", "PyTorch", "AWS", "Docker", "NLP"],
    "min_experience_years": 3,
    "max_experience_years": 8,
    "required_education":   "Bachelors",
}

SAMPLE_RESUMES = [
    {
        "label": "Shiva — Strong Match",
        "text": """Shiva Patel
shiva.patel@email.com | +1-555-0101

EDUCATION
B.Tech in Computer Science — MIT, 2018

EXPERIENCE
Data Scientist — TechCorp Inc.            Jan 2019 – Present
  • Built ML pipelines using Python, Scikit-learn, Pandas
  • Deployed NLP models to production (TensorFlow, PyTorch)
  • Managed AWS S3/EC2 infrastructure for model serving

Junior Analyst — DataLabs               Jun 2018 – Dec 2018
  • SQL queries, Excel dashboards, Python scripting

SKILLS
Python, Machine Learning, SQL, Pandas, Scikit-learn,
TensorFlow, PyTorch, NLP, AWS, Docker, Git, REST API
""",
    },
    {
        "label": "Rudra — Moderate Match",
        "text": """Rudra Sharma
rudra.sharma@email.com | +91-98765-43210

EDUCATION
Masters in Statistics — Delhi University, 2020

EXPERIENCE
Business Analyst — FinServe Ltd.         Mar 2020 – Present
  • SQL reporting and Excel dashboards
  • Basic Python scripting for data cleaning

SKILLS
Python, SQL, Excel, Tableau, R, Pandas, Power BI
""",
    },
    {
        "label": "Harry— Weak Match",
        "text": """Harry Johnson
harry.johnson@email.com

EDUCATION
High School Diploma — Springfield High, 2015

EXPERIENCE
Data Entry Operator — XYZ Corp           2016 – 2018

SKILLS
Microsoft Office, Excel, Data Entry, Typing
""",
    },
]


# ─────────────────────────────────────────────
#  INTERACTIVE MODE
# ─────────────────────────────────────────────

def get_interactive_inputs():
    print("\n" + "═"*60)
    print("         INTELLIGENT RESUME ANALYZER")
    print("═"*60)
    print("\n📋  STEP 1: Enter Job Details")

    job = {
        "title":       input("  Job Title          : ").strip() or "Software Engineer",
        "department":  input("  Department         : ").strip() or "Engineering",
    }

    print("\n  Required Skills (comma-separated):")
    req = input("  → ").strip()
    job["required_skills"] = [s.strip() for s in req.split(",") if s.strip()]

    print("  Preferred Skills (comma-separated, or press Enter to skip):")
    pref = input("  → ").strip()
    job["preferred_skills"] = [s.strip() for s in pref.split(",") if s.strip()]

    try:
        job["min_experience_years"] = float(input("  Min Experience (years): ").strip() or 0)
        job["max_experience_years"] = float(input("  Max Experience (years): ").strip() or 10)
    except ValueError:
        job["min_experience_years"] = 0
        job["max_experience_years"] = 10

    edu_options = ["Bachelors", "Masters", "PhD", "Diploma", "High School"]
    print(f"  Required Education {edu_options}:")
    edu = input("  → ").strip() or "Bachelors"
    job["required_education"] = edu if edu in edu_options else "Bachelors"

    print("\n📄  STEP 2: Paste Resume Text")
    print("  (Paste the resume, then press Enter twice to finish)\n")
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if lines and line == "":
            break
        lines.append(line)
    resume_text = "\n".join(lines)

    return resume_text, job


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Intelligent Resume Analyzer")
    parser.add_argument("--interactive", action="store_true",
                        help="Enter your own resume & job description")
    args = parser.parse_args()

    os.makedirs("output", exist_ok=True)

    if args.interactive:
        resume_text, job = get_interactive_inputs()
        safe_name = re.sub(r'\W+', '_', job.get("title", "job"))
        save_path = f"output/{safe_name}_result.json"
        result = analyze_resume(resume_text, job, save_path=save_path)
        print("\n" + result["report"])

    else:
        print("\n" + "═"*60)
        print("     INTELLIGENT RESUME ANALYZER  ─  DEMO MODE")
        print("═"*60)
        print(f"\n🔍  Analysing {len(SAMPLE_RESUMES)} resumes for: {SAMPLE_JOB['title']}\n")

        all_results = []
        for idx, sample in enumerate(SAMPLE_RESUMES, 1):
            print(f"  [{idx}/{len(SAMPLE_RESUMES)}] Processing: {sample['label']} ...", end="", flush=True)
            result = analyze_resume(
                sample["text"],
                SAMPLE_JOB,
                save_path=f"output/candidate_{idx}.json",
            )
            all_results.append({
                "rank":      idx,
                "label":     sample["label"],
                "score":     result["match"]["total"],
                "recommend": result["match"]["breakdown"]["skills"].get("required_matched", []),
            })
            print(f"  Score: {result['match']['total']}/100")
            print(result["report"])

        # Summary leaderboard
        all_results.sort(key=lambda x: x["score"], reverse=True)
        print("\n" + "═"*60)
        print("            CANDIDATE LEADERBOARD")
        print("═"*60)
        for rank, r in enumerate(all_results, 1):
            bar = "█" * int(r["score"] // 5) + "░" * (20 - int(r["score"] // 5))
            print(f"  #{rank}  {r['label'][:30]:<30}  {r['score']:5.1f}/100  {bar}")
        print("═"*60)

        # Save leaderboard
        leaderboard_path = "output/leaderboard.json"
        with open(leaderboard_path, "w") as f:
            json.dump(all_results, f, indent=2)
        print(f"\n✅  Leaderboard saved → {leaderboard_path}")
        print("✅  All results saved → output/\n")


import re

if __name__ == "__main__":
    main()
