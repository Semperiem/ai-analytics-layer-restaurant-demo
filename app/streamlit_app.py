"""Streamlit demo: ask a business question, get a governed SQL-backed answer.

Run with:
    streamlit run app/streamlit_app.py

Works fully offline: questions are matched to metrics with a deterministic
keyword router (see analytics_engine.route_question), no LLM required.
If OPENAI_BASE_URL is set, an optional local-LLM path is offered for
free-text questions that the rule-based router can't match.
"""
import os
import subprocess
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import analytics_engine as ae  # noqa: E402

st.set_page_config(page_title="Restaurant AI Analytics Demo", layout="wide")
st.title("Restaurant AI Analytics Layer — Demo")
st.caption(
    "Ask a business question in plain English. Answers are matched to a "
    "governed metric, executed as SQL against DuckDB, and returned with "
    "the query, the result table, and a short business answer."
)


@st.cache_resource
def get_connection():
    return ae.get_connection()


def ensure_warehouse_built():
    if ae.DB_PATH.exists():
        return
    with st.spinner("Building DuckDB warehouse from synthetic CSVs (first run only)..."):
        subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "build_duckdb.py")],
            check=True,
        )


ensure_warehouse_built()
con = get_connection()

sample_questions = [q for q, _ in ae.SAMPLE_QUESTIONS]

st.subheader("Ask a question")
col1, col2 = st.columns([2, 1])
with col1:
    chosen = st.selectbox(
        "Pick a sample business question, or type your own below:",
        ["(type your own)"] + sample_questions,
    )
with col2:
    st.write("")
    st.write("")
    llm_configured = bool(os.environ.get("OPENAI_BASE_URL"))
    st.caption(
        "Local LLM fallback: "
        + ("configured" if llm_configured else "not configured (optional)")
    )

default_text = "" if chosen == "(type your own)" else chosen
question = st.text_input("Your question", value=default_text)

if st.button("Ask", type="primary") and question.strip():
    metric = ae.route_question(question)

    if metric is not None:
        result = ae.METRICS[metric](con)
        st.success(f"Interpreted as metric: **{result.metric}**")
        st.markdown("**SQL used:**")
        st.code(result.sql, language="sql")
        st.markdown("**Result:**")
        st.dataframe(result.df, use_container_width=True)
        st.markdown("**Business answer:**")
        st.info(result.answer)
    else:
        st.warning(
            "No rule-based match for this question. This demo only routes "
            "the 7 governed metrics below without an LLM."
        )
        if llm_configured:
            st.write(
                "OPENAI_BASE_URL is set — this is where a local LLM call to "
                "translate free text into SQL would go (not implemented in "
                "this offline-first demo)."
            )
        st.write("Try one of the sample questions instead:")
        for q in sample_questions:
            st.markdown(f"- {q}")

st.divider()
st.subheader("Supported questions (rule-based, no LLM needed)")
for q, metric in ae.SAMPLE_QUESTIONS:
    st.markdown(f"- *{q}* → `{metric}`")
