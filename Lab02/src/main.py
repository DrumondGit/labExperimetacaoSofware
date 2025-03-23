import pandas as pd

import repositories_adapter

repositories = repositories_adapter.fetchRepositories()

if repositories:
    df = repositories_adapter.processData(repositories)
    STATISTICS_CALCULATOR_VALUES = df[
        ['Estrelas', 'Releases', 'Pull Requests Aceitos', 'Idade']]

    if df is not None:
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)

        print(df.to_string())

        repositories_adapter.plotGraphs(df)