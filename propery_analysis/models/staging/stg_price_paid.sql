-- grain: one row per property transaction (record_status - 'A'/Addition)

SELECT 
    transaction_id,
    SAFE_CAST(price AS INTEGER)      AS  price,
    SAFE_CAST(transfer_date AS TIMESTAMP) AS transfer_date,
    postcode,
    primary_address,
    secondary_address,
    street_name,
    local_area_name,
    town_city_name,
    district_name,
    county_name,
    CASE
        WHEN property_type = 'D' THEN 'detached'
        WHEN property_type = 'S' THEN 'semi_detached'
        WHEN property_type = 'T' THEN 'terraced'
        WHEN property_type = 'f' THEN 'flat'
        ELSE 'other'
    END AS property_type,
    CASE
        WHEN is_new = 'Y' THEN 'new_build'
        WHEN is_new = 'N' THEN 'established_build'
        ELSE 'unknown'
    END AS build_type,
    CASE
        WHEN duration = 'L' THEN 'freehold'
        WHEN duration = 'F' THEN 'leasehold'
        ELSE 'unknown'
    END AS ownership_type,
    CASE
        WHEN ppd_category_type = 'A' THEN 'standard_price_entry'
        WHEN ppd_category_type = 'B' THEN 'additional_price_entry'
        ELSE 'unknown'
    END AS pricepaid_type,

FROM {{ source('raw','price_paid')}}
WHERE 
    SAFE_CAST(price AS INTEGER) > 0
    AND record_status='A'
    AND transfer_date IS NOT NULL