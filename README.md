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

## Current status

- [x] README and project structure
- [x] Synthetic restaurant CSV data
- [x] Business glossary draft
- [x] Metric definitions draft
- [x] Benchmark question set draft
- [ ] dbt implementation
- [ ] DuckDB/PostgreSQL loader
- [ ] NL-to-SQL chatbot prototype
- [ ] Evaluation report
- [ ] Demo screenshots/video

## Author

Pham Quang Minh - Senior BI Developer / Analytics Engineer focused on Power BI, semantic modeling, analytics engineering, and AI-powered business intelligence.
