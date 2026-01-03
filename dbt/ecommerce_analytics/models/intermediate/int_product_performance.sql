-- Intermediate model: Product performance metrics
-- Aggregates sales, revenue, and review metrics for each product

with order_items as (
    select * from {{ ref('stg_order_items') }}
),

orders as (
    select * from {{ ref('stg_orders') }}
),

products as (
    select * from {{ ref('stg_products') }}
),

reviews as (
    select * from {{ ref('stg_order_reviews') }}
),

-- Get delivered orders only
delivered_items as (
    select
        oi.*,
        o.purchased_at,
        o.customer_delivered_at
    from order_items as oi
    inner join orders as o on oi.order_id = o.order_id
    where o.order_status = 'delivered'
),

-- Aggregate to product level
product_metrics as (
    select
        di.product_id,

        -- Sales metrics
        count(distinct di.order_id) as total_orders,
        count(*) as total_items_sold,
        sum(di.total_price) as total_revenue,
        sum(di.item_price) as total_items_revenue,
        sum(di.freight_price) as total_freight_revenue,

        -- Averages
        avg(di.item_price) as avg_item_price,
        avg(di.freight_price) as avg_freight_price,
        avg(di.total_price) as avg_total_price,

        -- Seller diversity
        count(distinct di.seller_id) as unique_sellers,

        -- Time metrics
        min(di.shipping_limit_date) as first_sale_date,
        max(di.shipping_limit_date) as last_sale_date,
        datediff(
            'day', min(di.shipping_limit_date), max(di.shipping_limit_date)
        ) as days_on_market

    from delivered_items as di
    group by di.product_id
),

-- Get review metrics for products
product_reviews as (
    select
        oi.product_id,
        avg(r.review_score) as avg_review_score,
        count(*) as review_count,
        count(case when r.review_score >= 4 then 1 end) as positive_reviews,
        count(case when r.review_score <= 2 then 1 end) as negative_reviews
    from reviews as r
    inner join order_items as oi on r.order_id = oi.order_id
    group by oi.product_id
),

-- Join with product details
final as (
    select
        p.product_id,
        p.category_english,
        p.category_portuguese,

        -- Product attributes
        p.weight_grams,
        p.volume_cubic_cm,
        p.photos_qty,
        p.is_missing_category,

        -- Sales metrics
        coalesce(pm.total_orders, 0) as total_orders,
        coalesce(pm.total_items_sold, 0) as total_items_sold,
        coalesce(pm.total_revenue, 0) as total_revenue,
        coalesce(pm.avg_item_price, 0) as avg_item_price,
        coalesce(pm.unique_sellers, 0) as unique_sellers,
        pm.days_on_market,

        -- Review metrics
        pr.avg_review_score,
        coalesce(pr.review_count, 0) as review_count,
        coalesce(pr.positive_reviews, 0) as positive_reviews,
        coalesce(pr.negative_reviews, 0) as negative_reviews,

        -- Performance indicators
        case
            when pm.total_revenue >= 10000 then 'Top Seller'
            when pm.total_revenue >= 1000 then 'Good Seller'
            when pm.total_revenue > 0 then 'Low Seller'
            else 'No Sales'
        end as sales_tier,

        case
            when pr.avg_review_score >= 4.5 then 'Excellent'
            when pr.avg_review_score >= 4.0 then 'Good'
            when pr.avg_review_score >= 3.0 then 'Average'
            when pr.avg_review_score < 3.0 then 'Poor'
            else 'No Reviews'
        end as review_tier

    from products as p
    left join product_metrics as pm on p.product_id = pm.product_id
    left join product_reviews as pr on p.product_id = pr.product_id
)

select * from final
