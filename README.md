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

## Remote access via Tailscale

For a persistent demo that survives reboot and is reachable from other devices on your
[Tailscale](https://tailscale.com) network, install the app as a `systemd --user` service:

```bash
scripts/install_user_service.sh
```

This script (idempotent — safe to re-run):

1. Builds the DuckDB warehouse (`scripts/build_duckdb.py`) using the repo `.venv`.
2. Renders `deploy/systemd/user/bi-chatbot-demo.service` into
   `~/.config/systemd/user/` and points it at this repo's `.venv/bin/streamlit`.
3. Runs `systemctl --user daemon-reload`, `enable`, and `restart` for the service,
   which binds Streamlit to `127.0.0.1:8501`.
4. Tries to enable **linger** (`loginctl enable-linger`) so the service keeps running
   after you log out and starts automatically at boot. This step needs root; if it
   can't get it, the script does **not** run `sudo` itself — it prints the exact
   command to run (`sudo loginctl enable-linger <user>`).
5. Publishes the local app through **Tailscale Serve** on HTTPS port `8501`, tailnet-only.
6. Prints the Tailscale MagicDNS URL to open the demo remotely, e.g.
   `https://<machine>.<tailnet>.ts.net:8501`.

Manage the running service with:

```bash
systemctl --user status bi-chatbot-demo.service
systemctl --user restart bi-chatbot-demo.service
journalctl --user -u bi-chatbot-demo.service -f
```

**Security note:** Streamlit itself binds to `127.0.0.1:8501` only. Remote access is provided by Tailscale Serve, so the public URL is tailnet-only and only works from devices logged into your Tailscale network. No `sudo` or system-wide service changes are made by this script.

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
