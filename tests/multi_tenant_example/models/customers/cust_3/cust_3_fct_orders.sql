{{ config(schema='cust_3', alias='fct_orders') }}

select {{ dbt_utils.star(ref('fct_orders'), except=['customer']) }}
from {{ ref('fct_orders') }}
where customer = 'cust_3'