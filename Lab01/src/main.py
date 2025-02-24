import pandas as pd

import file_adapter
import repositories_adapter
import statistics_calculator
# Run
repositories = repositories_adapter.fetchRepositories()
if repositories:
    df = repositories_adapter.processData(repositories)
    STATISTICS_CALCULATOR_VALUES = df[['Estrelas', 'Releases', 'Pull Requests Aceitos', 'Total de Issues']]
    REPOSITORIES_CRIATION_DATE = df[['Data de Criação']]

    if df is not None:
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        file_adapter.csv_writer(df.to_dict('records'), 'repos.csv')
        media = statistics_calculator.calculate_mean(STATISTICS_CALCULATOR_VALUES)
        mediana = statistics_calculator.calculate_median(STATISTICS_CALCULATOR_VALUES)
        moda = statistics_calculator.calculate_mode(STATISTICS_CALCULATOR_VALUES)
        repositories_middle_age = statistics_calculator.claculate_repositories_middle_age(REPOSITORIES_CRIATION_DATE)
        print(df.to_string())
        print("\n==================== MÉDIA ====================\n")
        print(media)
        print("\n==================== Mediana ====================\n")
        print(mediana)
        print("\n==================== IDADE MÉDIA REPOS ====================\n")
        print(f"{repositories_middle_age} anos")
        repositories_adapter.plotGraphs(df)





