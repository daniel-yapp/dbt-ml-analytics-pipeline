-- Intermediate model: Seller performance metrics
-- Aggregates sales, delivery, and review metrics for each seller

with order_items as (
    select * from {{ ref('stg_order_items') }}
),

orders as (
    select * from {{ ref('stg_orders') }}
),

sellers as (
    select * from {{ ref('stg_sellers') }}
),

reviews as (
    select * from {{ ref('stg_order_reviews') }}
),

-- Get delivered orders for seller metrics
delivered_items as (
    select
        oi.*,
        o.order_status,
        o.purchased_at,
        o.customer_delivered_at,
        o.carrier_delivered_at,
        o.is_late_delivery,
        o.delivery_delay_days
    from order_items oi
    inner join orders o on oi.order_id = o.order_id
    where o.order_status = 'delivered'
),

-- Aggregate to seller level
seller_metrics as (
    select
        seller_id,

        -- Sales metrics
        count(distinct order_id) as total_orders,
        count(*) as total_items_sold,
        sum(total_price) as total_revenue,
        avg(item_price) as avg_item_price,

        -- Product diversity
        count(distinct product_id) as unique_products,

        -- Delivery performance
        avg(delivery_delay_days) as avg_delivery_delay_days,
        count(case when is_late_delivery = true then 1 end) as late_deliveries,
        count(case when is_late_delivery = false then 1 end) as on_time_deliveries,

        -- Time metrics
        min(purchased_at) as first_sale_date,
        max(purchased_at) as last_sale_date,
        datediff('day', min(purchased_at), max(purchased_at)) as days_active

    from delivered_items
    group by seller_id
),

-- Get review metrics for sellers
seller_reviews as (
    select
        oi.seller_id,
        avg(r.review_score) as avg_review_score,
        count(*) as review_count,
        count(case when r.review_score >= 4 then 1 end) as positive_reviews,
        count(case when r.review_score <= 2 then 1 end) as negative_reviews
    from reviews r
    inner join order_items oi on r.order_id = oi.order_id
    group by oi.seller_id
),

-- Join with seller details
final as (
    select
        s.seller_id,
        s.city,
        s.state,

        -- Sales metrics
        coalesce(sm.total_orders, 0) as total_orders,
        coalesce(sm.total_items_sold, 0) as total_items_sold,
        coalesce(sm.total_revenue, 0) as total_revenue,
        coalesce(sm.avg_item_price, 0) as avg_item_price,
        coalesce(sm.unique_products, 0) as unique_products,
        sm.days_active,

        -- Delivery metrics
        sm.avg_delivery_delay_days,
        coalesce(sm.late_deliveries, 0) as late_deliveries,
        coalesce(sm.on_time_deliveries, 0) as on_time_deliveries,
        case
            when sm.late_deliveries + sm.on_time_deliveries > 0
            then round(100.0 * sm.on_time_deliveries /
                 (sm.late_deliveries + sm.on_time_deliveries), 2)
            else null
        end as on_time_delivery_pct,

        -- Review metrics
        sr.avg_review_score,
        coalesce(sr.review_count, 0) as review_count,
        coalesce(sr.positive_reviews, 0) as positive_reviews,
        coalesce(sr.negative_reviews, 0) as negative_reviews,

        -- Performance tiers
        case
            when sm.total_revenue >= 50000 then 'Top Seller'
            when sm.total_revenue >= 10000 then 'High Performer'
            when sm.total_revenue >= 1000 then 'Medium Performer'
            when sm.total_revenue > 0 then 'Low Performer'
            else 'No Sales'
        end as performance_tier,

        case
            when sr.avg_review_score >= 4.5 then 'Excellent'
            when sr.avg_review_score >= 4.0 then 'Good'
            when sr.avg_review_score >= 3.0 then 'Average'
            when sr.avg_review_score < 3.0 then 'Poor'
            else 'No Reviews'
        end as review_tier

    from sellers s
    left join seller_metrics sm on s.seller_id = sm.seller_id
    left join seller_reviews sr on s.seller_id = sr.seller_id
)

select * from final
