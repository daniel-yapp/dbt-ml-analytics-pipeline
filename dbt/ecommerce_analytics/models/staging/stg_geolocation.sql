-- Staging model for geolocation
-- Cleans and deduplicates Brazilian zip code to lat/long mappings

with source as (
    select * from {{ source('raw', 'olist_geolocation_dataset') }}
),

-- Deduplicate by taking average lat/long for each zip code prefix
deduplicated as (
    select
        geolocation_zip_code_prefix as zip_code_prefix,
        geolocation_city as city,
        geolocation_state as state,

        -- Average coordinates for zip codes with multiple entries
        avg(geolocation_lat) as latitude,
        avg(geolocation_lng) as longitude,

        count(*) as coordinate_count

    from source
    group by 1, 2, 3
)

select * from deduplicated
