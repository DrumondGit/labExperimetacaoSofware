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

# Carregar variáveis de ambiente
load_dotenv()

API_URL = os.environ.get("API_URL")
TOKEN = os.environ.get("TOKEN")
USERNAME = os.environ.get("GITHUB_USERNAME")
ck_path = os.environ.get("CK_REPO_URL")

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}


def fetchRepositories():
    """Faz a requisição GraphQL com paginação para obter 100 repositórios em 4 chamadas de 25."""
    allRepos = []
    cursor = None
    totalRepos = 3  # Número total de repositórios desejado
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

                print(f"✅ Chamada {batch + 1}/{numBatches} concluída com sucesso! ({len(allRepos)}/{totalRepos} repositórios coletados)\n")
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
        repo_url = f"{API_URL}{node['owner']['login']}/{node['name']}.git"
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

        if os.path.exists(cloned_repo_path) and has_java_files(repo_path):
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
        else:
            print(f"❌ Repositório {node['name']} ignorado (não contém arquivos .java)")

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

    fig, ax = plt.subplots()

    # Gráfico MATURIDADE X MÉTRICAS DE QUALIDADE
    cbo = df['Média CBO (Classes)']
    dit = df['Média DIT (Classes)']
    lcom = df['Média LCOM (Classes)']
    popularidade = df['Idade'].tolist()

    ax.plot(popularidade, cbo, label='CBO')
    ax.plot(popularidade, dit, label='DIT')
    ax.plot(popularidade, lcom, label='LCOM')

    ax.set_xlabel('Maturidade (Idade dos repositórios)')
    ax.set_ylabel('Métricas de Qualidade')
    ax.set_title('Métricas de Qualidade vs Popularidade')
    ax.legend()

    plt.show()

