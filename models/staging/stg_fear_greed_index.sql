with source as (

    select * from {{ source('raw', 'raw_fear_greed_index') }}

),

renamed as (

    select
        -- identifiers
        cast(value as int)                          as fear_greed_value,
        value_classification                        as sentiment_label,

        -- time
        cast(timestamp as int)                      as unix_timestamp,
        to_date(dateadd(
            second,
            cast(timestamp as int),
            '1970-01-01'::timestamp
        ))                                          as sentiment_date,

        -- metadata
        ingested_at

    from source

)

select * from renamed