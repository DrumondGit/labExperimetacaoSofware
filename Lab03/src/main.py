import repositories_adapter
import pandas as pd
from scipy.stats import spearmanr

def calcular_correlacoes_rqs(df):
    """
    Calcula a correlação de Spearman entre as métricas dos RQs e o feedback final ou número de revisões,
    e também calcula média e mediana dos valores.
    """
    rqs = {
        # A. Feedback Final das Revisões (Status do PR)
        "RQ 01 - Relação entre o tamanho dos PRs e o feedback final das revisões": (df['total_additions'] + df['total_deletions'], df['feedback_score']),
        "RQ 02 - Relação entre o tempo de análise dos PRs e o feedback final das revisões": (df['analysis_time_hours'], df['feedback_score']),
        "RQ 03 - Relação entre a descrição dos PRs e o feedback final das revisões": (df['description_length'], df['feedback_score']),
        "RQ 04 - Relação entre as interações nos PRs e o feedback final das revisões": (df['total_comments'] + df['total_participants'], df['feedback_score']),

        # B. Número de Revisões
        "RQ 05 - Relação entre o tamanho dos PRs e o número de revisões realizadas": (df['total_additions'] + df['total_deletions'], df['total_reviews']),
        "RQ 06 - Relação entre o tempo de análise dos PRs e o número de revisões realizadas": (df['analysis_time_hours'], df['total_reviews']),
        "RQ 07 - Relação entre a descrição dos PRs e o número de revisões realizadas": (df['description_length'], df['total_reviews']),
        "RQ 08 - Relação entre as interações nos PRs e o número de revisões realizadas": (df['total_comments'] + df['total_participants'], df['total_reviews']),
    }

    resultados = {}

    for nome_rq, (x, y) in rqs.items():
        # Remover valores nulos ou infinitos
        dados_validos = pd.DataFrame({'x': x, 'y': y}).replace([float('inf'), -float('inf')], pd.NA).dropna()

        if not dados_validos.empty:
            correlacao, p_valor = spearmanr(dados_validos['x'], dados_validos['y'])

            media_x = round(dados_validos['x'].mean(), 2)
            mediana_x = round(dados_validos['x'].median(), 2)
            media_y = round(dados_validos['y'].mean(), 2)
            mediana_y = round(dados_validos['y'].median(), 2)

            resultados[nome_rq] = {
                "Correlação (Spearman)": round(correlacao, 3) if pd.notna(correlacao) else None,
                "p-valor": round(p_valor, 5) if pd.notna(p_valor) else None,
                "Média (x)": media_x,
                "Mediana (x)": mediana_x,
                "Média (y)": media_y,
                "Mediana (y)": mediana_y
            }
        else:
            resultados[nome_rq] = {
                "Correlação (Spearman)": None,
                "p-valor": None,
                "Média (x)": None,
                "Mediana (x)": None,
                "Média (y)": None,
                "Mediana (y)": None
            }

    return resultados

# Código principal
repositories = repositories_adapter.fetch_repositories()

if repositories:
    df = repositories_adapter.process_data(repositories)
    if df is not None:
        print(df.to_string())

        # Coletar dados dos PRs
        pr_dados = []
        for repo in repositories:
            pr_dados.extend(repositories_adapter.collect_repository_metrics(repo))

        if pr_dados:
            df_prs = pd.DataFrame(pr_dados)

            # Calcular e mostrar resultados
            resultados = calcular_correlacoes_rqs(df_prs)
            print("\n📊 Resultados (Correlação de Spearman, Média e Mediana):")
            for campo, valores in resultados.items():
                print(f"\n{campo}:")
                print(f" - Correlação: {valores['Correlação (Spearman)']}")
                print(f" - p-valor: {valores['p-valor']}")
                print(f" - Média (x): {valores['Média (x)']} | Mediana (x): {valores['Mediana (x)']}")
                print(f" - Média (y): {valores['Média (y)']} | Mediana (y): {valores['Mediana (y)']}")
        else:
            print("⚠️ Nenhum dado de Pull Request coletado.")
