{{ config(schema='cust_2', alias='fct_order_items') }}

select {{ dbt_utils.star(ref('fct_order_items'), except=['customer']) }}
from {{ ref('fct_order_items') }}
where customer = 'cust_2'