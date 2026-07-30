# WrenAI PostgreSQL Connection

This repo can run a dedicated PostgreSQL copy of the restaurant demo data for WrenAI.

## Start / reload PostgreSQL

1. Create a private env file:

```bash
cp .env.postgres.example .env.postgres
# edit POSTGRES_PASSWORD and optionally TAILSCALE_IP
```

2. Start PostgreSQL and load synthetic data:

```bash
scripts/load_postgres_for_wrenai.sh
```

The script is idempotent: it can be re-run to rebuild the demo schema and reload CSV data.

## WrenAI connection values

If WrenAI is running in Docker on the same `wrenai_wren` network, use:

```text
Database type: PostgreSQL
Host: restaurant-demo-postgres
Port: 5432
Database: restaurant_demo
User: restaurant_user
Password: value from .env.postgres
SSL: disable
```

For direct access from another device on the same Tailscale network, use:

```text
Host: <machine MagicDNS name>
Port: 5435
Database: restaurant_demo
User: restaurant_user
Password: value from .env.postgres
SSL: disable
```

## Demo objects

Tables:

```text
stores
products
customers
orders
order_items
```

Views:

```text
stg_orders
stg_order_items
fact_sales
```

Recommended WrenAI modeling starting point:

```text
fact_sales
stores
products
customers
```

Join keys:

```text
fact_sales.store_id = stores.store_id
fact_sales.product_id = products.product_id
fact_sales.customer_id = customers.customer_id
```

Useful measures:

```text
Revenue = SUM(fact_sales.revenue)
Gross margin = SUM(fact_sales.gross_margin)
Order count = COUNT(DISTINCT fact_sales.order_id)
Customer count = COUNT(DISTINCT fact_sales.customer_id)
Average order value = SUM(fact_sales.revenue) / COUNT(DISTINCT fact_sales.order_id)
```

## Ops commands

```bash
docker compose -f docker-compose.wrenai-postgres.yml --env-file .env.postgres ps
docker logs restaurant-demo-postgres --tail 100
docker restart restaurant-demo-postgres
```

The container uses `restart: unless-stopped`, so it should survive reboot as long as Docker starts on boot.
