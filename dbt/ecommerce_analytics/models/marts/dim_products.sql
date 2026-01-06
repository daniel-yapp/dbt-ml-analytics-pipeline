-- Dimension table: Products
-- Product catalog with performance metrics

with product_performance as (
    select * from {{ ref('int_product_performance') }}
)

select
    -- Primary key
    product_id as product_key,

    -- Product attributes
    category_english,
    category_portuguese,
    weight_grams,
    volume_cubic_cm,
    photos_qty,

    -- Performance metrics
    total_orders,
    total_items_sold,
    total_revenue,
    avg_item_price,
    unique_sellers,
    days_on_market,

    -- Review metrics
    avg_review_score,
    review_count,
    positive_reviews,
    negative_reviews,

    -- Tiers
    sales_tier,
    review_tier,

    -- Flags
    is_missing_category,

    -- Metadata
    current_timestamp as created_at

from product_performance
