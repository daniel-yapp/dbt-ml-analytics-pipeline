-- Intermediate model: Customer order aggregations
-- Aggregates all order-level metrics for each unique customer

with orders as (
    select * from {{ ref('stg_orders') }}
),

order_items as (
    select * from {{ ref('stg_order_items') }}
),

payments as (
    select * from {{ ref('stg_order_payments') }}
),

reviews as (
    select * from {{ ref('stg_order_reviews') }}
),

customers as (
    select * from {{ ref('stg_customers') }}
),

-- Aggregate order items to order level
order_totals as (
    select
        order_id,
        sum(total_price) as order_value,
        sum(item_price) as items_value,
        sum(freight_price) as freight_value,
        count(*) as items_count
    from order_items
    group by order_id
),

-- Aggregate payments to order level
payment_totals as (
    select
        order_id,
        sum(payment_value) as total_paid,
        count(*) as payment_count,
        max(payment_installments) as max_installments
    from payments
    group by order_id
),

-- Get review scores
review_scores as (
    select
        order_id,
        review_score,
        sentiment,
        has_comment
    from reviews
),

-- Join everything together
order_enriched as (
    select
        o.order_id,
        o.customer_id,
        c.customer_unique_id,
        c.state as customer_state,

        -- Order details
        o.order_status,
        o.purchased_at,
        o.customer_delivered_at,
        o.estimated_delivery_date,
        o.delivery_delay_days,
        o.is_late_delivery,

        -- Financial metrics
        coalesce(ot.order_value, 0) as order_value,
        coalesce(ot.items_value, 0) as items_value,
        coalesce(ot.freight_value, 0) as freight_value,
        coalesce(ot.items_count, 0) as items_count,
        coalesce(pt.total_paid, 0) as total_paid,
        coalesce(pt.payment_count, 0) as payment_count,
        coalesce(pt.max_installments, 1) as max_installments,

        -- Review metrics
        r.review_score,
        r.sentiment,
        r.has_comment

    from orders o
    left join customers c on o.customer_id = c.customer_id
    left join order_totals ot on o.order_id = ot.order_id
    left join payment_totals pt on o.order_id = pt.order_id
    left join review_scores r on o.order_id = r.order_id
),

-- Aggregate to customer level (using customer_unique_id)
customer_aggregates as (
    select
        customer_unique_id,

        -- Order metrics
        count(distinct order_id) as total_orders,
        count(distinct case when order_status = 'delivered' then order_id end) as delivered_orders,
        count(distinct case when order_status = 'canceled' then order_id end) as canceled_orders,

        -- Financial metrics (only delivered orders)
        sum(case when order_status = 'delivered' then order_value else 0 end) as total_revenue,
        avg(case when order_status = 'delivered' then order_value end) as avg_order_value,
        max(case when order_status = 'delivered' then order_value end) as max_order_value,
        sum(case when order_status = 'delivered' then freight_value else 0 end) as total_freight_paid,

        -- Delivery performance
        avg(case when order_status = 'delivered' then delivery_delay_days end) as avg_delivery_delay_days,
        count(case when is_late_delivery = true then 1 end) as late_deliveries,

        -- Review metrics
        avg(review_score) as avg_review_score,
        count(case when review_score <= 2 then 1 end) as negative_reviews,
        count(case when review_score >= 4 then 1 end) as positive_reviews,

        -- Recency (days since last order)
        datediff('day', max(purchased_at)::date, '2018-08-31'::date) as days_since_last_order,

        -- Dates
        min(purchased_at) as first_order_date,
        max(purchased_at) as last_order_date,

        -- Location (from most recent order)
        max(customer_state) as customer_state

    from order_enriched
    group by customer_unique_id
)

select * from customer_aggregates
