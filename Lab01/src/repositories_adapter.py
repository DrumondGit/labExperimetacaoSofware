import json
import os
import time
import matplotlib.pyplot as plt
import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("GITHUB_TOKEN")

if not token:
    raise ValueError("Erro: O token do GitHub não foi encontrado. Verifique o arquivo .env.")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"


def fetchRepositories():
    """Faz a requisição GraphQL com paginação para obter 100 repositórios em 4 chamadas de 25."""
    allRepos = []
    cursor = None
    totalRepos = 1000  # Número total de repositórios desejado
    batchSize = 25  # Repositórios por chamada
    numBatches = totalRepos // batchSize  # Total de chamadas necessárias

    for batch in range(numBatches):
        print(f"🔄 Buscando repositórios... (Chamada {batch + 1}/{numBatches})")

        query = f"""
        {{
          search(query: "stars:>10000", type: REPOSITORY, first: {batchSize}, after: {json.dumps(cursor) if cursor else "null"}) {{
            edges {{
              node {{
                ... on Repository {{
                  name
                  owner {{ login }}
                  createdAt
                  updatedAt
                  stargazerCount
                  primaryLanguage {{ name }}
                  pullRequests(states: MERGED) {{ totalCount }}
                  releases {{ totalCount }}
                  openIssues: issues(states:OPEN) {{ totalCount }}
                  closedIssues: issues(states:CLOSED) {{ totalCount }}
                }}
              }}
            }}
            pageInfo {{
              hasNextPage
              endCursor
            }}
          }}
        }}
        """

        for attempt in range(3):
            response = requests.post(GITHUB_GRAPHQL_URL, json={"query": query}, headers=headers, )

            if response.status_code == 200:
                data = response.json()
                repositories = data['data']['search']['edges']

                if not repositories:
                    print("⚠️ Nenhum repositório encontrado.")
                    return None

                allRepos.extend(repositories)

                # Atualizar cursor para a próxima página
                pageInfo = data['data']['search']['pageInfo']
                cursor = pageInfo["endCursor"] if pageInfo["hasNextPage"] else None

                print(
                    f"✅ Chamada {batch + 1}/{numBatches} concluída com sucesso! ({len(allRepos)}/{totalRepos} repositórios coletados)\n")
                break

            else:
                print(f"⚠️ Erro {response.status_code}: {response.text}. Tentativa {attempt + 1}/3...")
                time.sleep(5)

    return allRepos


def processData(repositories):
    """Processa os dados da API para um DataFrame."""
    repoList = []

    for repo in repositories:
        node = repo['node']
        repoList.append({
            "Nome": node['name'],
            "Proprietário": node['owner']['login'],
            "Data de Criação": node['createdAt'],
            "Última Atualização": node['updatedAt'],
            "Estrelas": node['stargazerCount'],
            "Pull Requests Aceitos": node['pullRequests']['totalCount'],
            "Releases": node['releases']['totalCount'],
            "Total de Issues Abertas": node['openIssues']['totalCount'],
            "Total de Issues Fechadas": node['closedIssues']['totalCount'],
            "Linguagem Principal": node['primaryLanguage']['name'] if node['primaryLanguage'] else "Desconhecido"
        })

    return pd.DataFrame(repoList)

def plotGraphs(df):
    """Gera gráficos com base nos dados coletados, mostrando apenas o top 10."""
    if df is None or df.empty:
        print("⚠️ Sem dados suficientes para gerar gráficos.")
        return

    plt.rcParams.update({'font.size': 10})

    # Selecionar apenas o top 10 por estrelas
    df_top10 = df.sort_values(by="Estrelas", ascending=False).head(10)

    # Gráfico de barras: Estrelas por repositório (Top 10)
    plt.figure(figsize=(12, 6))
    plt.barh(df_top10["Nome"], df_top10["Estrelas"], color="skyblue")
    plt.xlabel("Número de Estrelas")
    plt.ylabel("Repositório")
    plt.title("Top 10 Repositórios por Número de Estrelas")
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.show()

    # Gráfico de pizza: Linguagens mais usadas (Top 10 repositórios)
    languageCounts = df_top10["Linguagem Principal"].value_counts()
    plt.figure(figsize=(8, 8))
    languageCounts.plot(kind="pie", autopct="%1.1f%%", startangle=140, cmap="Set3")
    plt.title("Distribuição das Linguagens de Programação (Top 10 Repositórios)")
    plt.ylabel("")
    plt.tight_layout()
    plt.show()

    # Gráfico de dispersão: PRs x Issues (Top 10 repositórios)
    plt.figure(figsize=(8, 6))
    plt.scatter(df_top10["Pull Requests Aceitos"], df_top10["Total de Issues Abertas"], color="orange", alpha=0.7)
    plt.xlabel("Pull Requests Aceitos")
    plt.ylabel("Total de Issues")
    plt.title("Pull Requests Aceitos vs Total de Issues (Top 10 Repositórios)")
    plt.tight_layout()
    plt.show()

    # ======= NOVO: Análise das Linguagens mais populares =======
    top_languages = df["Linguagem Principal"].value_counts().head(10)

    print("\n==================== Linguagens Mais Populares ====================\n")
    print(top_languages.to_string(header=False))

    plt.figure(figsize=(10, 5))
    top_languages.sort_values().plot(kind='barh', color='royalblue')
    plt.xlabel("Número de Repositórios")
    plt.ylabel("Linguagem")
    plt.title("Top 10 Linguagens Mais Utilizadas")
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.show()

    # Gráfico de barras agrupadas por linguagem
    top_languages = df["Linguagem Principal"].value_counts().head(5).index
    df_lang = df[df["Linguagem Principal"].isin(top_languages)]
    df_metrics = df_lang.groupby("Linguagem Principal")[["Pull Requests Aceitos", "Releases"]].sum()
    df_metrics["Dias Desde Última Atualização"] = (pd.to_datetime("today") - pd.to_datetime(df_lang.groupby("Linguagem Principal")["Última Atualização"].max()).dt.tz_localize(None)).dt.days

    
    df_metrics.plot(kind='bar', figsize=(10, 6), colormap='viridis')
    plt.title("Métricas por Linguagem Popular")
    plt.ylabel("Quantidade")
    plt.xlabel("Linguagem")
    plt.xticks(rotation=45)
    plt.legend(["PR Aceitos", "Releases", "Dias Desde Última Atualização"])
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.show()
    


def printLanguageStats(df):
    """Exibe uma tabela com as 10 linguagens mais populares, média de PRs aceitos, média de releases e média de dias desde a última atualização."""
    if df is None or df.empty:
        print("⚠️ Sem dados suficientes para análise.")
        return

    # Converter a coluna de data para datetime
    df["Última Atualização"] = pd.to_datetime(df["Última Atualização"])
    df["Dias Desde Última Atualização"] = (pd.to_datetime("today", utc=True) - df["Última Atualização"]).dt.total_seconds() / (60 * 60 * 24)


    # Filtrar as 10 linguagens mais populares
    top_languages = df["Linguagem Principal"].value_counts().head(10).index
    df_top_languages = df[df["Linguagem Principal"].isin(top_languages)]
    
    # Agrupar por linguagem e calcular médias
    df_stats = df_top_languages.groupby("Linguagem Principal").agg(
        Média_PRs_Aceitos=("Pull Requests Aceitos", "mean"),
        Média_Releases=("Releases", "mean"),
        Média_Dias_Desde_Última_Atualização=("Dias Desde Última Atualização", "mean")
    ).round(2)
    
    # Exibir a tabela
    print("\n==================== Estatísticas das 10 Linguagens Mais Populares ====================\n")
    print(df_stats)

    return df_stats

def plot_top_languages(df):
    """Gera um gráfico com as 10 linguagens mais populares nos repositórios coletados."""
    if df is None or df.empty:
        print("⚠️ Sem dados suficientes para gerar gráficos.")
        return

    # Contar as ocorrências das linguagens e pegar o top 10
    top_languages = df["Linguagem Principal"].value_counts().head(10)

    # Criando o gráfico
    plt.figure(figsize=(12, 6))
    top_languages.sort_values().plot(kind='barh', color='royalblue', edgecolor='black')

    # Adicionando rótulos e título
    plt.xlabel("Número de Repositórios")
    plt.ylabel("Linguagem")
    plt.title("Top 10 Linguagens Mais Utilizadas nos Repositórios do GitHub")

    # Melhorando a legibilidade
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.gca().invert_yaxis()

    # Exibir gráfico
    plt.show()