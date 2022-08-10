# stdlib
from collections import namedtuple
from itertools import product, starmap
from typing import Dict, List

# third party
from dbt.adapters.factory import Adapter
from dbt.config.runtime import RuntimeConfig
from dbt.contracts.graph.manifest import Manifest

# first party
from dbt_dynamic_models.utils import get_results_from_sql


class _Strategy:
    def __init__(
        self,
        dynamic_model: Dict,
        config: RuntimeConfig,
        manifest: Manifest,
        adapter: Adapter,
        handle_iterable: str = 'product',
    ):
        self.dynamic_model = dynamic_model
        self.config = config
        self.manifest = manifest,
        self.adapter = adapter
        self.handle_iterable = handle_iterable
    
    @property
    def product_iterable(self):
        iterable = self.get_iterable()
        Product = namedtuple('Product', iterable.keys())
        named_tuples = starmap(Product, product(*iterable.values()))
        return [named_tuple._asdict() for named_tuple in named_tuples]
        
    def get_iterable(self) -> List[Dict]:
        raise NotImplementedError
    
    def execute(self):
        if self.handle_iterable == 'product':
            return self.product_iterable
        
        else:
            raise NotImplementedError


class ParamStrategy(_Strategy):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_iterable(self):
        params = {}
        for param in self.dynamic_model['params']:
            if 'values' in param:
                params[param['name']] = param['values']
            elif 'query' in param:
                response, table = get_results_from_sql(
                    self.adapter, param['query'], fetch=True
                )
                if response.code != 'SUCCESS':
                    raise ValueError(f'Query unsuccessful: {response}')
                
                params.update(**{
                    col.name.lower(): col.values() for col in table.columns
                })
            else:
                raise NotImplementedError
        return params
