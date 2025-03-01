import pandas as pd

import file_adapter
import repositories_adapter
import statistics_calculator

# Run
repositories = repositories_adapter.fetchRepositories()
if repositories:
    df = repositories_adapter.processData(repositories)
    STATISTICS_CALCULATOR_VALUES = df[['Estrelas', 'Releases', 'Pull Requests Aceitos', 'Total de Issues']]
    REPOS_LAST_UPDATE_VALUES = df[['Última Atualização']]
    REPOSITORIES_CREATION_DATE = df[['Data de Criação']]
    REPOSITORIES_MAIN_LANGUAGES = df[['Linguagem Principal']]

    if df is not None:
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        file_adapter.csv_writer(df.to_dict('records'), 'repos.csv')
        media = statistics_calculator.calculate_mean(STATISTICS_CALCULATOR_VALUES)
        mediana = statistics_calculator.calculate_median(STATISTICS_CALCULATOR_VALUES)
        moda = statistics_calculator.calculate_mode(STATISTICS_CALCULATOR_VALUES)
        repositories_middle_age = statistics_calculator.calculate_repositories_middle_age(REPOSITORIES_CREATION_DATE)
        repos_last_update_statistics = statistics_calculator.calculate_last_update_statistics(REPOS_LAST_UPDATE_VALUES)
        languages_by_popularity = statistics_calculator.get_popular_languages(REPOSITORIES_MAIN_LANGUAGES)
        # print(df.to_string())
        # print("\n==================== MÉDIA ====================\n")
        # print(media)
        # print("\n==================== Mediana ====================\n")
        # print(mediana)
        # print("\n==================== IDADE MÉDIA REPOS ====================\n")
        # print(f"{repositories_middle_age} anos")
        # print("\n==================== ÚLTIMA ATUALIZAÇÃO ====================\n")
        # print(repos_last_update_statistics)
        # repositories_adapter.plotGraphs(df)
        # print("\n==================== LINGUAGENS POPULARES ====================\n")
        print(languages_by_popularity)



