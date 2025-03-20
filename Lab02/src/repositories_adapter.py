import json
import os
import shutil
import stat
import subprocess
import time
from datetime import datetime, timezone

import matplotlib.pyplot as plt
import pandas as pd
import requests
from dotenv import load_dotenv
from git import Repo
from pygount import ProjectSummary, SourceAnalysis

import quality_metrics_adapter

load_dotenv()
# token = os.getenv("GITHUB_TOKEN")
# github_SSH = os.getenv("GITHUB_SSH")
# ck_path = os.getenv("CK_REPO_PATH")

API_URL = os.environ.get("API_URL")
TOKEN = os.environ.get("TOKEN")
USERNAME = os.environ.get("GITHUB_USERNAME")
ck_path = os.environ.get("CK_REPO_URL")

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

#GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"


def fetchRepositories():
    """Faz a requisição GraphQL com paginação para obter 100 repositórios em 4 chamadas de 25."""
    allRepos = []
    cursor = None
    totalRepos = 2  # Número total de repositórios desejado
    batchSize = 1  # Repositórios por chamada
    numBatches = totalRepos // batchSize  # Total de chamadas necessárias

    for batch in range(numBatches):
        print(f"🔄 Buscando repositórios... (Chamada {batch + 1}/{numBatches})")

        query = f"""
        {{
          search(query: "stars:>10000 language:Java -topic:tutorial -topic:learning -topic:javaguide", type: REPOSITORY, first: {batchSize}, after: {json.dumps(cursor) if cursor else "null"}) {{
            edges {{
              node {{
                ... on Repository {{
                  name
                  owner {{ login }}
                  createdAt
                  updatedAt
                  stargazerCount
                  description
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
            response = requests.post(API_URL, json={"query": query}, headers=headers)

            if response.status_code == 200:
                data = response.json()
                repositories = data['data']['search']['edges']

                if not repositories:
                    print("⚠ Nenhum repositório encontrado.")
                    return None

                # Filtrar repositórios educacionais por palavras-chave na descrição ou nome
                filtered_repos = [
                    repo for repo in repositories
                    if not is_educational(repo['node'])
                ]

                allRepos.extend(filtered_repos)

                # Atualizar cursor para a próxima página
                pageInfo = data['data']['search']['pageInfo']
                cursor = pageInfo["endCursor"] if pageInfo["hasNextPage"] else None

                print(
                    f"✅ Chamada {batch + 1}/{numBatches} concluída com sucesso! ({len(allRepos)}/{totalRepos} repositórios coletados)\n")
                break

            else:
                print(f"⚠ Erro {response.status_code}: {response.text}. Tentativa {attempt + 1}/3...")
                time.sleep(5)

    return allRepos


def is_educational(repo):
    keywords = ["tutorial", "example", "guide", "learning", "course", "demo", "how-to"]

    name = repo.get("name", "").lower()
    description = (repo.get("description") or "").lower()

    return any(keyword in name or keyword in description for keyword in keywords)


def has_java_files(repo_path):
    for root, _, files in os.walk(repo_path):
        if any(file.endswith(".java") for file in files):
            return True
    return False


def processData(repositories):
    """Processa os dados da API para um DataFrame, excluindo repositórios sem arquivos .java."""
    repoList = []
    current_dir = os.path.dirname(__file__)

    print("🔄 Coletando dados dos repositórios...\n")

    for repo in repositories:
        node = repo['node']
        repo_age = calculate_repos_age(node['createdAt'])
        repo_url = f"https://github.com/{node['owner']['login']}/{node['name']}.git"
        clone_repo(current_dir, repo_url)
        repo_path = os.path.join("repo")
        cloned_repo_path = os.path.join(current_dir, "repo")
        output_path = os.path.join(repo_path, "ck_analysis/")
        print(cloned_repo_path)
        print("teste")
        print(repo_path)
    

        code_lines, comment_lines = count_lines(repo_path)
        quality_metrics_adapter.run_ck(repo_path, output_path, ck_path)
        quality_metrics = quality_metrics_adapter.summarize_ck_results(output_path)
        remove_repo(cloned_repo_path)

        repoList.append({
            "Nome": node['name'],
            "Proprietário": node['owner']['login'],
            "Idade": f"{repo_age} anos",
            "Estrelas": node['stargazerCount'],
            "Pull Requests Aceitos": node['pullRequests']['totalCount'],
            "Releases": node['releases']['totalCount'],
            "Linhas de código": code_lines,
            "Linhas de comentário": comment_lines,
            **quality_metrics
        })


    return pd.DataFrame(repoList)


def calculate_repos_age(creation_date):
    repo_age_timezone = datetime.now(timezone.utc) - pd.to_datetime(creation_date)
    repo_age = repo_age_timezone.days / 325.25
    return round(float(repo_age), 1)

def clone_repo(current_dir, repo_url):
    clone_path = os.path.join(current_dir, "repo")
    if not os.path.exists(clone_path):
        os.mkdir(clone_path)

    Repo.clone_from(repo_url, clone_path)

def count_lines(repo_path):
    summary = ProjectSummary()
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith(".java"):
                file_path = os.path.join(root, file)
                analysis = SourceAnalysis.from_file(file_path, "java", encoding="utf-8")
                summary.add(analysis)

    code_lines = summary.total_code_count
    comment_lines = summary.total_documentation_count

    return code_lines, comment_lines

def remove_readonly(func, path, _):
    os.chmod(path, stat.S_IWRITE)
    func(path)

def remove_repo(repo_path):
    try:
        subprocess.run(["git", "gc", "--prune=now"], cwd=repo_path, check=True)
    except Exception as e:
        print(f"⚠ Erro ao liberar repositório: {e}")

    try:
        shutil.rmtree(repo_path, onerror=remove_readonly)
    except Exception as e:
        print(f"⚠ Erro ao excluir repositório: {e}")

def plotGraphs(df):
    """Gera gráficos com base nos dados coletados, mostrando apenas o top 10."""
    if df is None or df.empty:
        print("⚠ Sem dados suficientes para gerar gráficos.")
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
        print("⚠ Sem dados suficientes para análise.")
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
        print("⚠ Sem dados suficientes para gerar gráficos.")
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


def save_repo_metrics_to_csv(df, repo_name, output_dir="output"):
    """Salva os dados de um repositório específico em um arquivo CSV."""
    if df is None or df.empty:
        print("⚠ Sem dados para salvar.")
        return
    
    if repo_name not in df["Nome"].values:
        print(f"⚠ Repositório '{repo_name}' não encontrado nos dados coletados.")
        return
    
    # Filtrar os dados do repositório desejado
    repo_data = df[df["Nome"] == repo_name]
    
    # Criar diretório de saída, se não existir
    os.makedirs(output_dir, exist_ok=True)
    
    # Caminho do arquivo CSV
    csv_path = os.path.join(output_dir, f"{repo_name}_metrics.csv")
    
    # Salvar em CSV
    repo_data.to_csv(csv_path, index=False, encoding="utf-8-sig")
    
    print(f"✅ Dados do repositório '{repo_name}' salvos em: {csv_path}")
