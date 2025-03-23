import pandas as pd

import repositories_adapter

repositories = repositories_adapter.fetchRepositories()

if repositories:
    df = repositories_adapter.processData(repositories)


    if df is not None:
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)

        print(df.to_string())

        graphs = repositories_adapter.plotGraphs(df)
        repositories_adapter.generate_html_report(df, graphs)