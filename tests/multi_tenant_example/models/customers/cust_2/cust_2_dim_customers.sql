{{ config(schema='cust_2', alias='dim_customers') }}

select {{ dbt_utils.star(ref('dim_customers'), except=['customer']) }}
from {{ ref('dim_customers') }}
where customer = 'cust_2'