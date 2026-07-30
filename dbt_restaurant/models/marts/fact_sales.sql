select
    oi.order_id,
    o.order_date,
    o.customer_id,
    o.store_id,
    o.channel,
    oi.product_id,
    oi.quantity,
    oi.unit_cost,
    oi.unit_price,
    oi.quantity * oi.unit_price as revenue,
    oi.quantity * (oi.unit_price - oi.unit_cost) as gross_margin
from {{ ref('stg_order_items') }} oi
join {{ ref('stg_orders') }} o on oi.order_id = o.order_id
