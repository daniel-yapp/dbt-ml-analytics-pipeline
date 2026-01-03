-- Dimension table: Customers
-- Slowly Changing Dimension Type 1 (current state only)
-- Combines customer data with RFM segmentation

with customer_orders as (
    select * from {{ ref('int_customer_orders') }}
),

rfm_scores as (
    select * from {{ ref('int_rfm_scores') }}
),

customers as (
    select * from {{ ref('stg_customers') }}
),

-- Get most recent customer record for each unique customer
latest_customers as (
    select
        customer_unique_id,
        max(customer_id) as latest_customer_id
    from customers
    group by customer_unique_id
),

final as (
    select
        -- Primary key
        lc.customer_unique_id as customer_key,

        -- Customer attributes
        c.city,
        c.state,
        c.zip_code_prefix,

        -- Order history
        co.total_orders,
        co.delivered_orders,
        co.canceled_orders,
        co.first_order_date,
        co.last_order_date,

        -- Financial metrics
        co.total_revenue,
        co.avg_order_value,
        co.max_order_value,
        co.total_freight_paid,

        -- Delivery performance
        co.avg_delivery_delay_days,
        co.late_deliveries,

        -- Review metrics
        co.avg_review_score,
        co.negative_reviews,
        co.positive_reviews,

        -- RFM segmentation
        rfm.recency_score,
        rfm.frequency_score,
        rfm.monetary_score,
        rfm.rfm_score,
        rfm.rfm_string,
        rfm.customer_segment,
        rfm.customer_tier,

        -- Recency
        co.days_since_last_order,

        -- Flags
        case when co.total_orders = 1 then true else false end as is_one_time_buyer,
        case when co.canceled_orders > 0 then true else false end as has_cancellations,
        case when co.negative_reviews > 0 then true else false end as has_negative_reviews,

        -- Metadata
        current_timestamp as created_at

    from latest_customers lc
    inner join customers c on lc.latest_customer_id = c.customer_id
    left join customer_orders co on lc.customer_unique_id = co.customer_unique_id
    left join rfm_scores rfm on lc.customer_unique_id = rfm.customer_unique_id
)

select * from final
