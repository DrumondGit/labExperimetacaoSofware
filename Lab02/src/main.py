import argparse
import pandas as pd
import repositories_adapter

def main():
    # Argumentos para start, end e quiet
    parser = argparse.ArgumentParser()
    parser.add_argument('--start', type=int, default=0, help='Índice de início')
    parser.add_argument('--end', type=int, default=1000, help='Índice final')
    parser.add_argument('--quiet', action='store_true', help='Suprimir a saída no terminal')
    args = parser.parse_args()

    # Condicional para suprimir a saída se o --quiet for fornecido
    if not args.quiet:
        print("Iniciando a coleta de dados dos repositórios...")

    # Passar start e end para fetchRepositories
    repositories = repositories_adapter.fetchRepositories(args.start, args.end)

    if repositories:
        df = repositories_adapter.processData(repositories)

        if df is not None:
            pd.set_option('display.max_rows', None)
            pd.set_option('display.max_columns', None)

            # Exibe a tabela no terminal se não for 'quiet'
            if not args.quiet:
                print(df.to_string())

            graphs = repositories_adapter.plotGraphs(df)
            repositories_adapter.generate_html_report(df, graphs)

if __name__ == "__main__":
    main()
