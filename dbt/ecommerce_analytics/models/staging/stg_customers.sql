-- Staging model for customers
-- Cleans and standardizes raw customer data

with source as (
    select * from {{ source('raw', 'olist_customers_dataset') }}
),

cleaned as (
    select
        -- Primary key
        customer_id,

        -- Customer identifier (actual person)
        customer_unique_id,

        -- Location
        customer_zip_code_prefix as zip_code_prefix,
        customer_city as city,
        customer_state as state

    from source
)

select * from cleaned
