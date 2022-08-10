# stdlib
from pathlib import Path
from typing import Dict

# third party
from dbt.adapters.factory import Adapter
from dbt.config.runtime import RuntimeConfig
from dbt.contracts.graph.manifest import Manifest
from dbt.lib import execute_sql

# first party
import dbt_dynamic_models.strategies as strategies
from dbt_dynamic_models.utils import get_results_from_sql


class DynamicModel:
    def __init__(
        self,
        config: RuntimeConfig,
        manifest: Manifest,
        adapter: Adapter,
        test_sql: bool = False,
    ):
        self.config = config
        self.manifest = manifest
        self.adapter = adapter
        self.test_sql = test_sql
        self.project_root = config.project_root
        self.model_path = Path(f'{self.project_root}/{config.model_paths[0]}')
    
    # The strategies we have to template out SQL from 1:N
    STRATEGIES = {
        'params': strategies.ParamStrategy,
    }
    
    def _get_strategy(self, dynamic_model: Dict) -> strategies._Strategy:
        """Return a strategy to get an iterable given the config of a dynamic model"""
        strategy = list(self.STRATEGIES.keys() & dynamic_model.keys())
        if len(strategy) > 1:
            raise ValueError(f'Multiple strategies found: {", ".join(strategy)}')
        
        if len(strategy) == 0:
            raise ValueError(
                'Valid strategy not found.  Strategies include: '
                f'{", ".join(self.STRATEGIES.keys())}'
            )
        
        return self.STRATEGIES[strategy[0]]

    def _parse_manifest_for_dynamic_models(self):
        """Return only parts of the manifest that contain a dynamic models key"""
        return {
            k: v for k, v in self.manifest.to_dict()['files'].items()
                if v['parse_file_type'] == 'schema'
                and 'dynamic_models' in v['dfy'].keys()
                # check for project root, allow user to define
                # what projects to look in (default is root only,
                # 'all' is an option, and a list of projects)
        }

    def _get_operation_node(self, sql, model):
        from dbt.parser.manifest import process_node
        from dbt.parser.sql import SqlBlockParser

        block_parser = SqlBlockParser(
            project=self.config,
            manifest=self.manifest,
            root_project=self.config,
        )

        sql_node = block_parser.parse_remote(sql, model)
        process_node(self.config, self.manifest, sql_node)
        return sql_node

    def _execute_sql(self, sql, model):
        from dbt.task.sql import SqlExecuteRunner

        node = self._get_operation_node(sql, model)
        runner = SqlExecuteRunner(self.config, self.adapter, node, 1, 1)
        return runner.safe_run(self.manifest)
        
    def _compile_and_run(self, sql: str, model: str):        
        sql += ' limit 1'
        results = self._execute_sql(sql, model)
        if len(results.timing) != 2:
            raise RuntimeError('Bad result')
    
    def _write(self, model: str, location: str, sql: str):
        if model[-4:] != '.sql':
            model += '.sql'
        path = self.model_path / location
        path.mkdir(parents=True, exist_ok=True)
        filepath = path / model
        with filepath.open('w', encoding='utf-8') as f:
            f.writelines(sql)

    def execute(self):
        """Entrypoint to this class"""
        schema_dict = self._parse_manifest_for_dynamic_models()
        if not schema_dict:
            raise RuntimeError('No dynamic models found in your project')

        for _, dct in schema_dict.items():
            dynamic_models = dct['dfy']['dynamic_models']
            for dynamic_model in dynamic_models:
                strategy = self._get_strategy(dynamic_model)(
                    dynamic_model, self.config, self.manifest, self.adapter
                )
                iterable = strategy.execute()
                for item in iterable:
                    model = dynamic_model['name'].format(**item)
                    location = dynamic_model['location'].format(**item)
                    sql = dynamic_model['sql'].format(**item)
                    if self.test_sql:
                        self._compile_and_run(sql, model)
                    self._write(model, location, sql)
