{{ config(schema='cust_1', alias='dim_suppliers') }}

select {{ dbt_utils.star(ref('dim_suppliers'), except=['customer']) }}
from {{ ref('dim_suppliers') }}
where customer = 'cust_1'