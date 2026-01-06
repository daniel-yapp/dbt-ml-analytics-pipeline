-- Staging model for sellers
-- Cleans and standardizes seller/merchant data

with source as (
    select * from {{ source('raw', 'olist_sellers_dataset') }}
),

cleaned as (
    select
        -- Primary key
        seller_id,

        -- Location
        seller_zip_code_prefix as zip_code_prefix,
        seller_city as city,
        seller_state as state

    from source
)

select * from cleaned
