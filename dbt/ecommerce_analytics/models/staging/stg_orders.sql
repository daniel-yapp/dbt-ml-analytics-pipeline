-- Staging model for orders
-- Cleans and standardizes raw order data with all status transitions

with source as (
    select * from {{ source('raw', 'olist_orders_dataset') }}
),

cleaned as (
    select
        -- Primary key
        order_id,

        -- Foreign keys
        customer_id,

        -- Order status
        order_status,

        -- Timestamps (keep original precision)
        order_purchase_timestamp as purchased_at,
        order_approved_at as approved_at,
        order_delivered_carrier_date as carrier_delivered_at,
        order_delivered_customer_date as customer_delivered_at,

        -- Estimated delivery (DATE type)
        order_estimated_delivery_date as estimated_delivery_date,

        -- Calculated fields
        case
            when order_delivered_customer_date is not null
                 and order_estimated_delivery_date is not null
            then datediff('day', order_estimated_delivery_date, order_delivered_customer_date::date)
            else null
        end as delivery_delay_days,

        case
            when order_delivered_customer_date is not null
                 and order_delivered_customer_date::date > order_estimated_delivery_date
            then true
            else false
        end as is_late_delivery

    from source
)

select * from cleaned
