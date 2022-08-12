# stdlib
from pathlib import Path
import json

# third party
from dbt.adapters.factory import get_adapter
from dbt.lib import get_dbt_config, parse_to_manifest
import dbt.clients.agate_helper
import dbt.tracking
import typer
import yaml

# first party
from dbt_dynamic_models.base import DynamicModel


app = typer.Typer()

DBT_PROFILES_DIR = typer.Option(
    None,
    envvar='DBT_PROFILES_DIR',
    help='Location of your profiles.yml file'
)
DBT_PROJECT_DIR = typer.Option(
    Path.cwd(), help='Location of your dbt_project.yml file'
)


@app.command()
def models(
    profiles_dir: str = DBT_PROFILES_DIR,
    project_dir=DBT_PROJECT_DIR,
    test_sql: bool = typer.Option(
        False, help='Test the generated SQL for each model prior to saving.'
    )
):
    # Set this as an environment variable so dbt knows where to look
    # if profiles_dir is not None:
    #     os.environ['DBT_PROFILES_DIR'] = profiles_dir
    
    print(project_dir)
    # Get config to pass to an adapter, let user change the project_dir
    config = get_dbt_config(project_dir)
    
    # Get your current adapter
    adapter = get_adapter(config)
    adapter.acquire_connection()
    
    # Initialize active_user (next line will fail without this)
    dbt.tracking.initialize_from_flags()

    manifest = parse_to_manifest(config)

    DynamicModel(config, manifest, adapter, test_sql).execute()
    
    
@app.command(
    context_settings={'allow_extra_args': True, 'ignore_unknown_options': True}
)
def profile(
    ctx: typer.Context,
    profile_name: str = typer.Option(..., help='Name of profile from dbt_project.yml'),
    target_name: str = typer.Option('default', help='Name of the active target'),
):
    if len(ctx.args) % 2 != 0:
        raise RuntimeError('Invalid number of arguments given')    
    
    target_config = {}
    key = None
    for i, extra_arg in enumerate(ctx.args):
        if i % 2 == 0:
            key = extra_arg.lstrip('-')
        else:
            target_config[key] = extra_arg
        
    profile_config = {
        profile_name: {
            'outputs': {
                target_name: target_config
            },
            'target': target_name
        }
    }
    typer.echo(yaml.dump(profile_config))


def main():
    app()
