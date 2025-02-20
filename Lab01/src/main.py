import pandas as pd

import file_adapter
import respositories_adapter

# Run
repositories = respositories_adapter.fetchRepositories()
if repositories:
    df = respositories_adapter.processData(repositories)
    if df is not None:
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        file_adapter.csv_writer(df.to_dict('records'), 'repos.csv')
        print(df.to_string())
