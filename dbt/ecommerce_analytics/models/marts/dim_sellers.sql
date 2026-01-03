-- Dimension table: Sellers
-- Seller/merchant information with performance metrics

with seller_performance as (
    select * from {{ ref('int_seller_performance') }}
)

select
    -- Primary key
    seller_id as seller_key,

    -- Seller attributes
    city,
    state,

    -- Performance metrics
    total_orders,
    total_items_sold,
    total_revenue,
    avg_item_price,
    unique_products,
    days_active,

    -- Delivery metrics
    avg_delivery_delay_days,
    late_deliveries,
    on_time_deliveries,
    on_time_delivery_pct,

    -- Review metrics
    avg_review_score,
    review_count,
    positive_reviews,
    negative_reviews,

    -- Tiers
    performance_tier,
    review_tier,

    -- Metadata
    current_timestamp as created_at

from seller_performance
