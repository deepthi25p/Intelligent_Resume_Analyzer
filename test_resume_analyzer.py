"""
test_resume_analyzer.py  ─  Unit Tests
========================================
Run with:  python test_resume_analyzer.py
"""

import sys
import os
import json
import tempfile

sys.path.insert(0, os.path.dirname(__file__))

from resume_analyzer import (
    extract_name, extract_email, extract_phone, extract_skills,
    extract_experience_years, extract_education,
    parse_resume, calculate_match_score, generate_report,
    save_results, load_results, analyze_resume,
    get_recommendation,
)

PASS = "✅ PASS"
FAIL = "❌ FAIL"

results = []

def test(name, condition):
    status = PASS if condition else FAIL
    results.append((name, status))
    print(f"  {status}  {name}")

print("\n" + "═"*55)
print("        INTELLIGENT RESUME ANALYZER — TESTS")
print("═"*55)

# ── Parser Tests ──────────────────────────────────────────
print("\n  [1] PARSER TESTS")

sample = """John Doe
john.doe@example.com | +1-800-555-1234

EDUCATION
B.Tech Computer Science — IIT Delhi, 2017

EXPERIENCE
ML Engineer — OpenAI                    2020 – Present
Data Analyst — IBM                      2017 – 2020

SKILLS
Python, Machine Learning, SQL, TensorFlow, Docker, AWS, Git
"""

test("Extract name",             extract_name(sample) == "John Doe")
test("Extract email",            extract_email(sample) == "john.doe@example.com")
test("Extract phone",            extract_phone(sample) != "Not found")
test("Extract skills (>=5)",     len(extract_skills(sample)) >= 5)
test("Python in skills",         "Python" in extract_skills(sample))
test("Experience > 0 years",     extract_experience_years(sample) > 0)
test("Education = Bachelors",    extract_education(sample) == "Bachelors")

# ── Match Score Tests ─────────────────────────────────────
print("\n  [2] MATCH SCORE TESTS")

candidate = parse_resume(sample)

job = {
    "title":                "Data Scientist",
    "department":           "AI",
    "required_skills":      ["Python", "Machine Learning", "SQL"],
    "preferred_skills":     ["TensorFlow", "AWS"],
    "min_experience_years": 2,
    "max_experience_years": 7,
    "required_education":   "Bachelors",
}

match = calculate_match_score(candidate, job)

test("Total score 0–100",          0 <= match["total"] <= 100)
test("Breakdown has 4 keys",       len(match["breakdown"]) == 4)
test("Skills score ≤ 50",          match["breakdown"]["skills"]["score"] <= 50)
test("Experience score ≤ 30",      match["breakdown"]["experience"]["score"] <= 30)
test("Education score ≤ 10",       match["breakdown"]["education"]["score"] <= 10)
test("Quality score ≤ 10",         match["breakdown"]["quality"]["score"] <= 10)
test("Strong match score > 60",    match["total"] > 60)

# ── Recommendation Tests ──────────────────────────────────
print("\n  [3] RECOMMENDATION TESTS")

test("≥80 → STRONG HIRE",     "STRONG" in get_recommendation(85))
test("65–79 → RECOMMENDED",   "RECOMMENDED" in get_recommendation(70))
test("45–64 → MAYBE",         "MAYBE" in get_recommendation(55))
test("<45 → NOT RECOMMENDED", "NOT RECOMMENDED" in get_recommendation(30))

# ── Report Generation Tests ───────────────────────────────
print("\n  [4] REPORT GENERATION TESTS")

report = generate_report(candidate, job, match)

test("Report is a string",       isinstance(report, str))
test("Report has name",          candidate["name"] in report)
test("Report has total score",   str(int(match["total"])) in report or str(match["total"]) in report)
test("Report has RECOMMENDATION", "RECOMMENDATION" in report)
test("Report has CANDIDATE",     "CANDIDATE" in report)

# ── File Operations Tests ─────────────────────────────────
print("\n  [5] FILE OPERATION TESTS")

with tempfile.TemporaryDirectory() as tmpdir:
    path = os.path.join(tmpdir, "test_result.json")
    data = {"score": 88.5, "name": "John Doe", "skills": ["Python", "SQL"]}
    save_results(data, path)
    loaded = load_results(path)
    test("Save & load JSON",        loaded == data)
    test("JSON has score",          loaded.get("score") == 88.5)

# ── Full Pipeline Test ────────────────────────────────────
print("\n  [6] FULL PIPELINE TEST")

result = analyze_resume(sample, job)
test("Result has timestamp",     "timestamp" in result)
test("Result has candidate",     "candidate" in result)
test("Result has match",         "match" in result)
test("Result has report",        "report" in result)
test("Candidate name correct",   result["candidate"]["name"] == "John Doe")

# ── Summary ───────────────────────────────────────────────
print("\n" + "═"*55)
passed = sum(1 for _, s in results if s == PASS)
total  = len(results)
print(f"\n  Results: {passed}/{total} tests passed")
if passed == total:
    print("  🎉 ALL TESTS PASSED — Project is ready to submit!\n")
else:
    failed = [(n, s) for n, s in results if s == FAIL]
    print(f"  ⚠ {len(failed)} test(s) failed:")
    for name, _ in failed:
        print(f"     • {name}")
    print()
print("═"*55 + "\n")
