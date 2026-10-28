# TrustLens

TrustLens helps teams find common data-quality problems before those problems affect business reporting and decisions.

## What it does

- Upload a CSV or explore the included example dataset
- Calculate a transparent 0–100 data trust screening score
- Detect missing values, exact duplicate rows, negative numeric values, invalid date/time values in date-like columns, entirely empty columns, and constant columns
- View issue severity, explanations, and suggested follow-up actions
- Explore charts and a column-level data profile
- Download the source data preview and a JSON quality report

## Technology

- Python 3.10+
- Streamlit
- Pandas
- Plotly

## Run locally

Create and activate a virtual environment, then install dependencies.

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

macOS/Linux:

```bash
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL printed in the terminal, usually `http://localhost:8501`.

If PowerShell blocks environment activation, use the environment's Python executable directly:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m streamlit run app.py
```

## Suggested demo walkthrough

1. Start with the built-in example dataset.
2. Show the trust score and row/column summary.
3. Open **Issues & fixes** and review missing values, duplicate rows, negative sales, and the invalid date.
4. Use **Overview** to inspect missing values by column and the dataset profile.
5. Upload a CSV of your own and compare the findings.
6. Export the JSON report to preserve the results.

## How the trust score works

The score starts at 100 and applies capped penalties for missing cells, exact duplicate rows, negative numeric values, invalid date/time values in columns whose names indicate dates or times, and entirely empty columns. The score is intentionally explainable and is only a screening heuristic. Teams should adjust checks and weights to match their business rules.

## Important limitations

- A negative number may be valid in a domain such as refunds or accounting adjustments.
- Exact duplicate rows are not always duplicate transactions.
- Date validation is currently applied to columns whose names include terms such as `date`, `time`, `timestamp`, or `_at`.
- The current version analyses uploaded CSV files only. It does not connect to live databases, schedule jobs, send alerts, or call an external AI model.
- Do not upload confidential or regulated data to a public demo.

## Product direction

Potential future improvements include configurable per-column rules, data freshness checks, schema-change detection, scheduled monitoring, alert integrations, and optional AI-generated summaries with human review.
