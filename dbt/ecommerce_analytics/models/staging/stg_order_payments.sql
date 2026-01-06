-- Staging model for order payments
-- Cleans and standardizes payment transactions

with source as (
    select * from {{ source('raw', 'olist_order_payments_dataset') }}
),

cleaned as (
    select
        -- Composite primary key
        order_id,
        payment_sequential,

        -- Payment details
        payment_type,
        payment_installments,
        payment_value,

        -- Categorize payment types
        case
            when payment_type = 'credit_card' then 'Credit Card'
            when payment_type = 'boleto' then 'Boleto'
            when payment_type = 'voucher' then 'Voucher'
            when payment_type = 'debit_card' then 'Debit Card'
            else 'Other'
        end as payment_type_clean

    from source
)

select * from cleaned
