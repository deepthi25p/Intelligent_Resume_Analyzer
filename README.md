# 🧠 Intelligent Resume Analyzer

> A Python-based system that automates resume screening — parses candidates, calculates match scores (0–100), and generates professional hiring reports.

---

## 🎯 Features

| Feature | Details |
|---|---|
| **Resume Parsing** | Extracts name, email, phone, skills, experience years, education |
| **Matching Algorithm** | Weighted 4-dimension scoring (Skills 50% + Experience 30% + Education 10% + Quality 10%) |
| **Skill Gap Analysis** | Identifies missing required skills and matched preferred skills |
| **Hiring Recommendation** | Automatic STRONG HIRE / RECOMMENDED / MAYBE / NOT RECOMMENDED |
| **JSON File I/O** | Save & load all analysis results in structured JSON |
| **Report Generation** | Clean, professional text reports with candidate leaderboard |
| **Error Handling** | Graceful fallbacks for missing fields, malformed input, edge cases |
| **No Dependencies** | Pure Python standard library — works anywhere |

---

## 📁 Project Structure

```
intelligent_resume_analyzer/
│
├── resume_analyzer.py      # Core engine: parser + scorer + reporter
├── main.py                 # Entry point (demo mode + interactive mode)
├── test_resume_analyzer.py # 25+ unit tests
├── requirements.txt        # No external deps needed
│
├── samples/
│   ├── alice_chen_resume.txt   # Sample strong-match resume
│   └── sample_job.json         # Sample job description
│
└── output/                 # Auto-created — JSON results saved here
    ├── candidate_1.json
    ├── candidate_2.json
    └── leaderboard.json
```

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/intelligent_resume_analyzer_hidevs.git
cd intelligent_resume_analyzer_hidevs
```

### 2. Run the demo (3 sample resumes vs 1 job)
```bash
python main.py
```

### 3. Run with your own resume
```bash
python main.py --interactive
```

### 4. Run unit tests
```bash
python test_resume_analyzer.py
```

---

## 📊 Scoring Algorithm

```
Total Score (0–100) = Skills Score + Experience Score + Education Score + Quality Score

Skills (50 pts):
  → Required Skills Match  × 80%  ┐
  → Preferred Skills Match × 20%  ┘  × 50

Experience (30 pts):
  → Within range → proportional score up to 30
  → Below minimum → partial credit (max 15)

Education (10 pts):
  → Meets or exceeds requirement → 10 pts
  → Below requirement → 5 pts

Resume Quality (10 pts):
  → Email present (+3), Phone present (+2),
    200+ words (+3), 5+ skills listed (+2)
```

---

## 🏆 Recommendation Thresholds

| Score | Recommendation |
|---|---|
| 80–100 | 🟢 **STRONG HIRE** — Schedule technical interview |
| 65–79 | 🟡 **RECOMMENDED** — Proceed with screening call |
| 45–64 | 🟠 **MAYBE** — Consider if pipeline is thin |
| 0–44 | 🔴 **NOT RECOMMENDED** — Significant gaps |

---

## 💻 Sample Output

```
════════════════════════════════════════════════════════════
         INTELLIGENT RESUME ANALYZER — REPORT
════════════════════════════════════════════════════════════
  Generated   : 23 May 2025, 10:30 AM
  Job Title   : Senior Data Scientist
  Department  : Analytics & AI
════════════════════════════════════════════════════════════

  CANDIDATE PROFILE
  ────────────────────────────────────────
  Name        : Alice Chen
  Email       : alice.chen@email.com
  Education   : Bachelors
  Experience  : 6.0 years
  Skills (12) : Python, Machine Learning, SQL, TensorFlow...

  MATCH SCORE BREAKDOWN
  ────────────────────────────────────────
  Skills      :  45.0 / 50
  Experience  :  27.0 / 30
  Education   :  10.0 / 10
  Quality     :  10.0 / 10
  ────────────────────
  TOTAL SCORE :  92.0 / 100

  RECOMMENDATION
  ────────────────────────────────────────
  🟢 STRONG HIRE — Exceptional match. Schedule technical interview immediately.
```

---

## 🧪 Tests

25 unit tests covering:
- All 7 parser functions
- Match score calculation (all 4 dimensions)
- Recommendation thresholds (all 4 levels)
- Report generation
- JSON save & load
- Full pipeline end-to-end

---

## 🛠 Skills Demonstrated

- **Python Programming** — Clean OOP + functional design, PEP 8 compliant
- **Text Processing** — Multi-pattern regex extraction, section parsing
- **Data Extraction** — Structured candidate profile from unstructured text
- **JSON File Handling** — Save/load with proper encoding & error handling
- **Matching Algorithms** — Weighted multi-factor scoring system

---

## 📹 Demo Video

[▶ Watch Demo on YouTube](#) ← *Add your YouTube link here*

---

## 👤 Author

**Your Name** | [GitHub](https://github.com/YOUR_USERNAME)

---

*Built for the HiDevs Intelligent Resume Analyzer challenge.*
