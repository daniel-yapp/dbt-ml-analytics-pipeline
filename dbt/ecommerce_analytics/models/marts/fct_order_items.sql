-- Fact table: Order Items
-- Grain: One row per order line item
-- Contains item-level metrics and foreign keys to dimensions

with order_items as (
    select * from {{ ref('stg_order_items') }}
),

orders as (
    select * from {{ ref('stg_orders') }}
),

customers as (
    select * from {{ ref('stg_customers') }}
),

final as (
    select
        -- Composite primary key
        oi.order_id || '-' || oi.order_item_id as order_item_key,

        -- Foreign keys (dimension references)
        oi.order_id as order_key,
        c.customer_unique_id as customer_key,
        oi.product_id as product_key,
        oi.seller_id as seller_key,
        o.purchased_at::date as order_date_key,  -- For date dimension join

        -- Item details
        oi.order_item_id as item_sequence,

        -- Pricing (Brazilian Real - R$)
        oi.item_price,
        oi.freight_price,
        oi.total_price,

        -- Shipping
        oi.shipping_limit_date,

        -- Order context
        o.order_status,
        o.purchased_at,
        o.customer_delivered_at,

        -- Customer location
        c.state as customer_state,

        -- Flags
        case when o.order_status = 'delivered' then true else false end as is_delivered,

        -- Metadata
        current_timestamp as created_at

    from order_items oi
    inner join orders o on oi.order_id = o.order_id
    left join customers c on o.customer_id = c.customer_id
)

select * from final
