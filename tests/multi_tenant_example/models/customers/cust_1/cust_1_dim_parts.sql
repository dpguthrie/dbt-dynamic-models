{{ config(schema='cust_1', alias='dim_parts') }}

select {{ dbt_utils.star(ref('dim_parts'), except=['customer']) }}
from {{ ref('dim_parts') }}
where customer = 'cust_1'