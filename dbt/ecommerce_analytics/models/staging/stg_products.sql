-- Staging model for products
-- Cleans and standardizes product catalog with English translations

with source as (
    select * from {{ source('raw', 'olist_products_dataset') }}
),

translations as (
    select * from {{ source('raw', 'product_category_name_translation') }}
),

cleaned as (
    select
        -- Primary key
        p.product_id,

        -- Category (with English translation)
        p.product_category_name as category_portuguese,
        coalesce(t.product_category_name_english, 'Unknown') as category_english,

        -- Product attributes (note: actual names not in dataset, only lengths)
        p.product_name_lenght as name_length,
        p.product_description_lenght as description_length,
        p.product_photos_qty as photos_qty,

        -- Physical dimensions for shipping calculation
        p.product_weight_g as weight_grams,
        p.product_length_cm as length_cm,
        p.product_height_cm as height_cm,
        p.product_width_cm as width_cm,

        -- Calculated volume (cubic cm)
        (p.product_length_cm * p.product_height_cm * p.product_width_cm) as volume_cubic_cm,

        -- Data quality flags
        case when p.product_category_name is null then true else false end as is_missing_category

    from source p
    left join translations t
        on p.product_category_name = t.product_category_name
)

select * from cleaned
