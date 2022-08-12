import time
from pathlib import Path
from dbt_dynamic_models.cli import models

start = time.time()
models(project_dir=Path.cwd() / 'tests/row_strategy')
end = time.time()
print(end - start)
