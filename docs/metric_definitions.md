# Metric Definitions

## revenue
Formula: `sum(quantity * unit_price)`

## gross_margin
Formula: `sum(quantity * (unit_price - unit_cost))`

## average_order_value
Formula: `revenue / count(distinct order_id)`

## order_count
Formula: `count(distinct order_id)`

## customer_count
Formula: `count(distinct customer_id)`

## repeat_purchase_rate
Formula: `repeat_customers / total_customers`

## churn_risk_customer_count
Formula: count of customers where churn risk flag = high.
