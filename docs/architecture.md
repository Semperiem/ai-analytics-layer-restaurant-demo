# Architecture

This demo uses synthetic restaurant data to show a BI + AI analytics layer.

Pipeline:

1. Generate synthetic data as CSV files.
2. Load CSV files into DuckDB or PostgreSQL.
3. Transform raw tables into staging and mart models using dbt.
4. Document metrics and business terms.
5. Build a natural-language question interface.
6. Generate SQL only against allowed tables and documented metrics.
7. Execute SQL and return a short business answer.
8. Evaluate generated SQL against a benchmark question set.
