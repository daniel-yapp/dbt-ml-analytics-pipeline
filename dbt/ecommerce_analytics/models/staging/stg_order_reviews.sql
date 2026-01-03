-- Staging model for order reviews
-- Cleans and standardizes customer review data

with source as (
    select * from {{ source('raw', 'olist_order_reviews_dataset') }}
),

cleaned as (
    select
        -- Primary key
        review_id,

        -- Foreign key
        order_id,

        -- Review score (1-5 stars)
        review_score,

        -- Review text (Portuguese - needs translation for NLP)
        review_comment_title,
        review_comment_message,

        -- Timestamps
        review_creation_date as created_at,
        review_answer_timestamp as answered_at,

        -- Derived fields
        case
            when review_comment_message is not null
                 and length(trim(review_comment_message)) > 0
            then true
            else false
        end as has_comment,

        case
            when review_score >= 4 then 'Positive'
            when review_score = 3 then 'Neutral'
            else 'Negative'
        end as sentiment

    from source
)

select * from cleaned
