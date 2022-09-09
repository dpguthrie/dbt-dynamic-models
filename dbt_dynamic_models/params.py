# stdlib
import logging
from collections import namedtuple
from itertools import product, starmap
from typing import Dict

# third party
from dbt.adapters.factory import Adapter

# first party
from dbt_dynamic_models.utils import get_results_from_sql

logger = logging.getLogger(__name__)


class Param:
    def __init__(
        self,
        dynamic_model: Dict,
        adapter: Adapter,
    ):
        self.dynamic_model = dynamic_model
        self.adapter = adapter
        self.strategy = self.dynamic_model.get('strategy', 'product')

    STRATEGY_FUNCTION = {
        'product': product,
        'row': zip,
    }

    def _format_params(self):
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

                params.update(
                    **{col.name.lower(): col.values() for col in table.columns}
                )
            else:
                raise NotImplementedError
        return params

    def product_check(self, params):
        pass

    def row_check(self, params: Dict):
        iterables = [v for k, v in params.items()]
        length = len(iterables[0])
        if any(len(ls) != length for ls in iterables):
            logger.warning('The parameters are of unequal lengths!')

    def get_iterable(self):
        params = self._format_params()

        # Check params
        strategy_check = f'{self.strategy}_check'
        getattr(self, strategy_check)(params)

        # Hard error for undefined strategies
        func = self.STRATEGY_FUNCTION[self.strategy]

        # Get appropriate iterable based on strategy
        Iterable = namedtuple('Iterable', params.keys())
        named_tuples = starmap(Iterable, func(*params.values()))
        return [named_tuple._asdict() for named_tuple in named_tuples]
