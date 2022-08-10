# Dynamic Models

Generate dbt models dynamically from config!

This package is useful if you have the same SQL query that you need parameterized to create 1 -> N number of models.  The benefit of this approach is that we still get to leverage the best of dbt:  using `ref`s and `source`s, testing, and documentation!

## Overview

This is a simple CLI tool that allows a user to dynamically create models within your dbt project.

## Requirements

Python 3.7+

- Typer - Library for building CLI applications
- PyYAML - Fully-featured YAML framework for python

## Installation

`pip install dbt-dynamic-models`

## Basic Usage

The CLI can be accessed with `dbtgen` and there are two commands available:

- `models` - Dynamically generate models
- `profile` - Create the yml to be inserted into your profiles.yml file

The `models` command is keyed off a specific config inside a yml file in your dbt_project

### config

Inside 1 or more yml files within your models directory, you'll include the following top-level key:

```yml
dynamic_models:
```

Within the top-level `dynamic_models` key, you'll need the following required arguments:
- `name` - This is the name of the model dbt will create
- `location` - This is where dbt will create the model file
- `params` - This is what we'll use to parameterize our SQL
- `sql` - This is the SQL that will be included within each file

Here's an example of what that looks like:

```yml
dynamic_models:
  - name: '{customer}_{model}'
    location: customers/{customer}/
    params:
      - name: customer
        query: |
          select lower(schema_name) as customer
          from doug_demo.information_schema.schemata
          where schema_name like 'CUST_%'
      - name: model
        values:
          - dim_customers
          - dim_parts
          - dim_suppliers
          - fct_order_items
          - fct_orders
    sql: |
      {{{{ config(schema='{customer}', alias='{model}') }}}}

      select {{{{ dbt_utils.star(ref('{model}'), except=['customer']) }}}}
      from {{{{ ref('{model}') }}}}
      where customer = '{customer}'
```

A few things you should notice from the code above:

- The placeholders within each string for name, location, and sql are being derived from the name of the parameters themselves.  **You can see we're also able to use SQL to parameterize our models!**
- We have parameterized our model name - dbt expects each model name to be unique
- Slight inconvenience - our jinja has to be escaped so python doesn't look for it as a placeholder.  For instance, `{{ ref('some_model') }}` becomes `{{{{ ref('some_model') }}}}` because we use a curly brace to escape a curly brace we want to exist within our string.
- **All placeholders are lowercase**

### dbt-Core

To run this locally, simply `pip install dbt-dynamic-models` alongside your project, create your `dynamic_models` config, and then run this command:

```bash
dbtgen models
```

*This assumes that your profiles.yml file is located at `~/.dbt`*

### dbt Cloud

Currently, this can only be run via a github action, or the similar verbiage for different git providers.  An example action is located [here](/.github/workflows/test.yml)

At a high-level, the action does the following:

- Checkout your repo
- Install python
- Install dependencies - `pip install dbt-dynamic-models[snowflake]`.
- Generate a profiles.yml file
- Generate models

## To-Do

Allow for dynamic creation of yml files for models created - tests, descriptions, etc.