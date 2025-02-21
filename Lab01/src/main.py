import pandas as pd

import file_adapter
import repositories_adapter
import statistics_calculator
# Run
repositories = repositories_adapter.fetchRepositories()
if repositories:
    df = repositories_adapter.processData(repositories)
    if df is not None:
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        file_adapter.csv_writer(df.to_dict('records'), 'repos.csv')
        media = statistics_calculator.calculate_mean(df.to_dict('records'))
        mediana = statistics_calculator.calculate_median(df.to_dict('records'))
        moda = statistics_calculator.calculate_mode(df.to_dict('records'))
        print(df.to_string())
        print("\n==================== MÉDIA ====================\n")
        print(media)
        print("\n==================== Mediana ====================\n")
        print(mediana)



