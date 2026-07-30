#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="${ROOT_DIR}/docker-compose.wrenai-postgres.yml"
ENV_FILE="${ROOT_DIR}/.env.postgres"
CONTAINER="restaurant-demo-postgres"

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "Missing ${ENV_FILE}. Copy .env.postgres.example and set POSTGRES_PASSWORD." >&2
  exit 1
fi

# Export env vars for docker compose and docker exec psql commands below.
set -a
# shellcheck disable=SC1090
source "${ENV_FILE}"
set +a

cd "${ROOT_DIR}"

docker compose -f "${COMPOSE_FILE}" --env-file "${ENV_FILE}" up -d

echo "Waiting for PostgreSQL health check..."
for i in {1..30}; do
  status="$(docker inspect -f '{{.State.Health.Status}}' "${CONTAINER}" 2>/dev/null || true)"
  if [[ "${status}" == "healthy" ]]; then
    break
  fi
  sleep 2
  if [[ "${i}" == "30" ]]; then
    echo "PostgreSQL did not become healthy. Current status: ${status}" >&2
    docker logs "${CONTAINER}" --tail 80 >&2 || true
    exit 1
  fi
done

# Load/reload schema and data. Uses container psql so host does not need psql installed.
docker exec -i "${CONTAINER}" psql -v ON_ERROR_STOP=1 -U "${POSTGRES_USER:-restaurant_user}" -d "${POSTGRES_DB:-restaurant_demo}" <<'SQL'
DROP VIEW IF EXISTS fact_sales;
DROP VIEW IF EXISTS stg_orders;
DROP VIEW IF EXISTS stg_order_items;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS stores;

CREATE TABLE stores (
  store_id integer PRIMARY KEY,
  store_name text NOT NULL,
  region text NOT NULL,
  store_type text NOT NULL
);

CREATE TABLE products (
  product_id integer PRIMARY KEY,
  category text NOT NULL,
  product_name text NOT NULL,
  unit_cost numeric(12,2) NOT NULL,
  unit_price numeric(12,2) NOT NULL
);

CREATE TABLE customers (
  customer_id integer PRIMARY KEY,
  customer_segment text NOT NULL,
  churn_risk text NOT NULL
);

CREATE TABLE orders (
  order_id integer PRIMARY KEY,
  order_date date NOT NULL,
  customer_id integer NOT NULL REFERENCES customers(customer_id),
  store_id integer NOT NULL REFERENCES stores(store_id),
  channel text NOT NULL
);

CREATE TABLE order_items (
  order_id integer NOT NULL REFERENCES orders(order_id),
  product_id integer NOT NULL REFERENCES products(product_id),
  quantity integer NOT NULL,
  unit_cost numeric(12,2) NOT NULL,
  unit_price numeric(12,2) NOT NULL
);
SQL

docker exec -i "${CONTAINER}" psql -v ON_ERROR_STOP=1 -U "${POSTGRES_USER:-restaurant_user}" -d "${POSTGRES_DB:-restaurant_demo}" <<'SQL'
\copy stores FROM '/demo_data/stores.csv' WITH (FORMAT csv, HEADER true);
\copy products FROM '/demo_data/products.csv' WITH (FORMAT csv, HEADER true);
\copy customers FROM '/demo_data/customers.csv' WITH (FORMAT csv, HEADER true);
\copy orders FROM '/demo_data/orders.csv' WITH (FORMAT csv, HEADER true);
\copy order_items FROM '/demo_data/order_items.csv' WITH (FORMAT csv, HEADER true);

CREATE VIEW stg_orders AS SELECT * FROM orders;
CREATE VIEW stg_order_items AS SELECT * FROM order_items;
CREATE VIEW fact_sales AS
SELECT
  oi.order_id,
  o.order_date,
  o.customer_id,
  o.store_id,
  o.channel,
  oi.product_id,
  oi.quantity,
  oi.unit_cost,
  oi.unit_price,
  oi.quantity * oi.unit_price AS revenue,
  oi.quantity * (oi.unit_price - oi.unit_cost) AS gross_margin
FROM stg_order_items oi
JOIN stg_orders o ON oi.order_id = o.order_id;

CREATE INDEX idx_orders_order_date ON orders(order_date);
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_store_id ON orders(store_id);
CREATE INDEX idx_order_items_product_id ON order_items(product_id);
SQL

echo "Loaded restaurant demo data into PostgreSQL."
docker exec "${CONTAINER}" psql -U "${POSTGRES_USER:-restaurant_user}" -d "${POSTGRES_DB:-restaurant_demo}" -c "SELECT 'fact_sales' AS object, COUNT(*) AS rows, ROUND(SUM(revenue), 2) AS revenue FROM fact_sales;"
