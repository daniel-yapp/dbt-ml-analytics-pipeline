-- Staging model for order items
-- Cleans and standardizes order line items

with source as (
    select * from {{ source('raw', 'olist_order_items_dataset') }}
),

cleaned as (
    select
        -- Composite primary key
        order_id,
        order_item_id,

        -- Foreign keys
        product_id,
        seller_id,

        -- Shipping
        shipping_limit_date,

        -- Pricing (Brazilian Real - R$)
        price as item_price,
        freight_value as freight_price,
        (price + freight_value) as total_price

    from source
)

select * from cleaned
