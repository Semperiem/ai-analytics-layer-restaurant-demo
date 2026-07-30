"""End-to-end smoke test: build the DuckDB warehouse and run every sample
question through the rule-based router and metrics layer.

Usage:
    python scripts/smoke_test.py

Exits non-zero on any failure so it can be used in CI.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.build_duckdb import build, DB_PATH  # noqa: E402
from app import analytics_engine as ae  # noqa: E402


def main() -> int:
    print("Building DuckDB warehouse...")
    build(DB_PATH)

    con = ae.get_connection(DB_PATH)

    failures = []
    for question, expected_metric in ae.SAMPLE_QUESTIONS:
        routed = ae.route_question(question)
        if routed != expected_metric:
            failures.append(
                f"ROUTING MISMATCH: {question!r} -> {routed!r} (expected {expected_metric!r})"
            )
            continue

        try:
            result = ae.answer_question(con, question)
        except Exception as exc:  # noqa: BLE001
            failures.append(f"QUERY ERROR for {question!r}: {exc}")
            continue

        if result is None or result.df.empty or not result.answer:
            failures.append(f"EMPTY RESULT for {question!r}")
            continue

        print(f"OK  [{result.metric:>22}] {question}")
        print(f"      -> {result.answer}")

    con.close()

    if failures:
        print("\nSMOKE TEST FAILED:")
        for f in failures:
            print(f"  - {f}")
        return 1

    print(f"\nSMOKE TEST PASSED ({len(ae.SAMPLE_QUESTIONS)} sample questions).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
