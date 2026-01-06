-- Fact table: Orders
-- Grain: One row per order
-- Contains order-level metrics and foreign keys to dimensions

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
        count(*) as items_count,
        count(distinct product_id) as unique_products,
        count(distinct seller_id) as unique_sellers
    from order_items
    group by order_id
),

-- Aggregate payments to order level
payment_totals as (
    select
        order_id,
        sum(payment_value) as total_paid,
        count(*) as payment_count,
        max(payment_installments) as max_installments,
        -- Get primary payment method (most common)
        max(payment_type_clean) as primary_payment_type
    from payments
    group by order_id
),

-- Get review scores (latest review per order)
review_scores as (
    select
        order_id,
        review_score,
        sentiment,
        has_comment
    from reviews
    qualify
        row_number() over (partition by order_id order by created_at desc) = 1
),

final as (
    select
        -- Primary key
        o.order_id as order_key,

        -- Foreign keys (dimension references)
        c.customer_unique_id as customer_key,
        o.purchased_at::date as order_date_key,  -- For date dimension join

        -- Order details
        o.order_status,
        o.purchased_at,
        o.approved_at,
        o.carrier_delivered_at,
        o.customer_delivered_at,
        o.estimated_delivery_date,

        -- Calculated delivery metrics
        o.delivery_delay_days,
        o.is_late_delivery,
        pt.primary_payment_type,
        r.review_score,
        r.sentiment,

        -- Financial metrics
        r.has_comment,
        c.state as customer_state,
        c.city as customer_city,
        datediff('day', o.purchased_at::date, o.carrier_delivered_at::date)
            as days_to_carrier,

        -- Payment details
        datediff(
            'day', o.carrier_delivered_at::date, o.customer_delivered_at::date
        ) as days_in_transit,
        datediff('day', o.purchased_at::date, o.customer_delivered_at::date)
            as days_to_customer,
        coalesce(ot.order_value, 0) as order_value,

        -- Order composition
        coalesce(ot.items_value, 0) as items_value,
        coalesce(ot.freight_value, 0) as freight_value,
        coalesce(pt.total_paid, 0) as total_paid,

        -- Review metrics
        coalesce(pt.payment_count, 0) as payment_count,
        coalesce(pt.max_installments, 1) as max_installments,
        coalesce(ot.items_count, 0) as items_count,

        -- Customer location
        coalesce(ot.unique_products, 0) as unique_products,
        coalesce(ot.unique_sellers, 0) as unique_sellers,

        -- Flags
        coalesce(o.order_status = 'delivered', false)
            as is_delivered,
        coalesce(o.order_status = 'canceled', false)
            as is_canceled,
        coalesce(ot.unique_sellers > 1, false)
            as is_multi_seller,

        -- Metadata
        current_timestamp as created_at

    from orders o
    left join customers c on o.customer_id = c.customer_id
    left join order_totals ot on o.order_id = ot.order_id
    left join payment_totals pt on o.order_id = pt.order_id
    left join review_scores r on o.order_id = r.order_id
)

select * from final
