import pandas as pd

import repositories_adapter

repositories = repositories_adapter.fetchRepositories()
df = repositories_adapter.processData(repositories)
