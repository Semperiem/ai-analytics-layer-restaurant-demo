# AI Analytics Layer for Restaurant Revenue

A public portfolio demo showing how to build a governed AI analytics layer over restaurant-style business data.

The goal: business users ask plain-English questions and receive SQL-backed answers from trusted dimensional models.

## Example questions

- Why did revenue drop last month?
- Which stores are underperforming?
- Which customer segments have the highest repeat purchase rate?
- What is average order value by channel?
- Which products have declining gross margin?
- Which regions have the highest churn risk?

## Business problem

Traditional BI dashboards are powerful, but business users often need follow-up answers that are not already in dashboards.

This project demonstrates a modern analytics workflow where:

1. Synthetic restaurant data is transformed into trusted dimensional models.
2. Business metrics are defined consistently.
3. Dashboards and AI-powered querying use the same governed data layer.
4. Users can ask natural-language questions and receive SQL-backed answers.

## Architecture

```text
Synthetic Restaurant Data
        |
        v
DuckDB / PostgreSQL Warehouse
        |
        v
dbt Models + Tests + Documentation
        |
        +------------------+
        |                  |
        v                  v
BI Dashboard               AI Analytics Layer
                           |
                           v
                  NL-to-SQL / Chat Interface
                           |
                           v
                  SQL-backed Business Answers
```

## Tech stack

- Python
- DuckDB or PostgreSQL
- dbt
- SQL
- Streamlit or Gradio
- Local LLM via llama.cpp / OpenAI-compatible endpoint
- Optional: WrenAI-style semantic interface
- Optional: Superset dashboard
- Optional: Airflow orchestration

## Quickstart

```bash
# 1) Create and activate a local virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2) Install dependencies
pip install -r requirements.txt

# 3) Build the local DuckDB warehouse from synthetic CSVs
python scripts/build_duckdb.py

# 4) Run the smoke test
python scripts/smoke_test.py

# 5) Start the BI chatbot demo
streamlit run app/streamlit_app.py
```

The demo works offline first: sample questions are routed by deterministic rules to governed SQL metrics, so no paid API or external LLM is required.

## Working demo questions

The Streamlit app currently supports these rule-based questions:

- What are the top selling products?
- How many repeat customers do we have?
- What is the monthly revenue trend?
- What is revenue by channel?
- What is revenue by store?
- What is the average order value?
- What is total revenue?

For each question, the app shows:

- interpreted metric
- SQL query used
- result table
- short business answer

## Demo files

- `scripts/build_duckdb.py` — builds `warehouse/restaurant.duckdb` from synthetic CSV files.
- `app/analytics_engine.py` — governed metric functions and rule-based question routing.
- `app/streamlit_app.py` — local BI chatbot UI.
- `scripts/smoke_test.py` — end-to-end verification of database build + sample questions.
- `data/synthetic/` — synthetic restaurant dataset.
- `docs/metric_definitions.md` — metric glossary.
- `eval/benchmark_questions.yml` — evaluation question set.

## Current status

- [x] README and project structure
- [x] Synthetic restaurant CSV data
- [x] Business glossary draft
- [x] Metric definitions draft
- [x] Benchmark question set draft
- [x] DuckDB loader
- [x] Governed metrics SQL layer
- [x] Offline Streamlit BI chatbot prototype
- [x] Smoke test
- [ ] dbt implementation completion
- [ ] Evaluation report
- [ ] Demo screenshots/video
- [ ] Optional local LLM integration

## Screenshots

Screenshots/GIF should be added after running the Streamlit app locally:

```bash
streamlit run app/streamlit_app.py
```

Recommended screenshots:

1. chatbot question selection
2. SQL-backed answer for total revenue
3. revenue by store table
4. monthly revenue trend result

## Author

Pham Quang Minh - Senior BI Developer / Analytics Engineer focused on Power BI, semantic modeling, analytics engineering, and AI-powered business intelligence.
