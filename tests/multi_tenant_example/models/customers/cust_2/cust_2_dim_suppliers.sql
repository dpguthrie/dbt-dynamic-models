{{ config(schema='cust_2', alias='dim_suppliers') }}

select {{ dbt_utils.star(ref('dim_suppliers'), except=['customer']) }}
from {{ ref('dim_suppliers') }}
where customer = 'cust_2'