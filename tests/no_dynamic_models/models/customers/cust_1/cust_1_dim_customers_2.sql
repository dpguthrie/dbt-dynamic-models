{{ config(schema='cust_1', alias='dim_customers') }}

select {{ dbt_utils.star(ref('dim_customers'), except=['customer']) }}
from {{ ref('dim_customers') }}
where customer = 'cust_1'