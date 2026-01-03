-- Intermediate model: RFM (Recency, Frequency, Monetary) scores
-- Segments customers for targeted marketing and churn prevention

with customer_orders as (
    select * from {{ ref('int_customer_orders') }}
),

-- Calculate RFM quintiles using ntile()
rfm_quintiles as (
    select
        customer_unique_id,

        -- Raw RFM metrics
        days_since_last_order as recency_days,
        total_orders as frequency,
        total_revenue as monetary_value,

        -- RFM scores (1-5, where 5 is best)
        -- Recency: Lower days = Higher score (more recent)
        6 - ntile(5) over (order by days_since_last_order) as recency_score,

        -- Frequency: More orders = Higher score
        ntile(5) over (order by total_orders) as frequency_score,

        -- Monetary: More revenue = Higher score
        ntile(5) over (order by total_revenue) as monetary_score

    from customer_orders
    where total_revenue > 0  -- Only customers with completed purchases
),

-- Calculate combined RFM score and segment
rfm_segmented as (
    select
        *,

        -- Combined RFM score (3-15 scale)
        (recency_score + frequency_score + monetary_score) as rfm_score,

        -- RFM string (e.g., "555" for champions)
        cast(recency_score as varchar)
        || cast(frequency_score as varchar)
        || cast(monetary_score as varchar) as rfm_string,

        -- Customer segments based on RFM scores
        case
            -- Champions: Best customers (recent, frequent, high value)
            when
                recency_score >= 4
                and frequency_score >= 4
                and monetary_score >= 4
                then 'Champions'

            -- Loyal Customers: Frequent buyers
            when frequency_score >= 4 and monetary_score >= 4
                then 'Loyal Customers'

            -- Potential Loyalists: Recent customers with potential
            when
                recency_score >= 4
                and frequency_score >= 2
                and monetary_score >= 2
                then 'Potential Loyalists'

            -- Recent Customers: Just bought
            when recency_score >= 4
                then 'Recent Customers'

            -- Promising: Recent, spent decent amount
            when recency_score >= 3 and monetary_score >= 3
                then 'Promising'

            -- Need Attention: Above average but not recent
            when
                recency_score >= 2
                and frequency_score >= 2
                and monetary_score >= 2
                then 'Need Attention'

            -- At Risk: Used to be good customers, but haven't purchased recently
            when
                recency_score <= 2
                and frequency_score >= 3
                and monetary_score >= 3
                then 'At Risk'

            -- Can't Lose Them: High value, but not recent
            when
                recency_score <= 2
                and frequency_score >= 4
                and monetary_score >= 4
                then 'Cannot Lose Them'

            -- Hibernating: Low recency, used to buy
            when recency_score <= 2 and frequency_score >= 2
                then 'Hibernating'

            -- Lost: Lowest scores
            else 'Lost'
        end as customer_segment,

        -- Simplified tier
        case
            when
                (recency_score + frequency_score + monetary_score) >= 12
                then 'High Value'
            when
                (recency_score + frequency_score + monetary_score) >= 8
                then 'Medium Value'
            else 'Low Value'
        end as customer_tier

    from rfm_quintiles
)

select * from rfm_segmented
