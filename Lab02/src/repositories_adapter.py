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

TOKEN = os.getenv("GITHUB_TOKEN")
API_URL = os.getenv("GITHUB_API_URL")
ck_path = os.getenv("CK_REPO_PATH")


# API_URL = os.environ.get("API_URL")
# TOKEN = os.environ.get("TOKEN")
# USERNAME = os.environ.get("GITHUB_USERNAME")
# ck_path = os.environ.get("CK_REPO_URL")
GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}


def fetchRepositories():
    """Faz a requisição GraphQL com paginação para obter 100 repositórios em 4 chamadas de 25."""
    allRepos = []
    cursor = None
    totalRepos = 5  # Número total de repositórios desejado
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
            response = requests.post(GITHUB_GRAPHQL_URL, json={"query": query}, headers=headers)

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
    print(f"Verificando arquivos em: {repo_path}")
    for root, _, files in os.walk(repo_path):
        print(f"📂 Diretório: {root}")
        for file in files:
            print(f"    📄 {file}")
            if file.endswith(".java"):
                print("✅ Arquivo .java encontrado!")
                return True
    print("❌ Nenhum arquivo .java encontrado.")
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
        removed = repo_path
        cloned_repo_path = os.path.join(repo_path, "repo_name")
        if not os.path.exists(cloned_repo_path):
            subprocess.run(["git", "clone", repo_url, cloned_repo_path])
        output_path = os.path.join(cloned_repo_path, "ck_analysis/")
        print("passou aqui")
        print(output_path)

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

        
    remove_repo(cloned_repo_path)
    

    return pd.DataFrame(repoList)


def calculate_repos_age(creation_date):
    repo_age_timezone = datetime.now(timezone.utc) - pd.to_datetime(creation_date)
    repo_age = repo_age_timezone.days / 325.25
    return round(float(repo_age), 1)


def clone_repo(current_dir, repo_url):
    clone_path = os.path.join(current_dir, "repo")
    if not os.path.exists(clone_path):
        os.mkdir(clone_path)
    else:
        remove_repo(clone_path)
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

def remove_repo(repo_path):
    print("passou aqui no remove repoooooooooo")
    """Remove o repositório da pasta 'repo'."""
    try:
        # Rodar o comando de garbage collection do git para limpar o repositório, se necessário
        subprocess.run(["git", "gc", "--prune=now"], cwd=repo_path, check=True)
    except Exception as e:
        print(f"⚠ Erro ao rodar git gc no repositório {repo_path}: {e}")

    try:
        # Remover o repositório (diretório) usando shutil.rmtree
        shutil.rmtree(repo_path, onerror=remove_readonly)
        print(f"✅ Repositório {repo_path} removido com sucesso!")
    except Exception as e:
        print(f"⚠ Erro ao excluir repositório {repo_path}: {e}")

def remove_readonly(func, path, _):
    """Função para remover arquivos somente leitura durante o processo de remoção."""
    os.chmod(path, stat.S_IWRITE)
    func(path)


def plotGraphs(df):
    """Gera gráficos de popularidade x métricas de qualidade e maturidade x métricas de qualidade."""
    
    # Definindo as métricas de qualidade
    metrics = ['Média CBO (Classes)', 'Média DIT (Classes)', 'Média LCOM (Classes)']
    
    # Configuração para criar múltiplos gráficos
    fig, axes = plt.subplots(2, len(metrics), figsize=(15, 10))
    fig.suptitle('Popularidade vs Métricas de Qualidade e Maturidade vs Métricas de Qualidade')

    # Plotando os gráficos para cada métrica
    for i, metric in enumerate(metrics):
        # Gráfico de Popularidade vs Métrica de Qualidade
        ax1 = axes[0, i]
        ax1.scatter(df['Estrelas'], df[metric], color='blue', alpha=0.5)
        ax1.set_title(f'Popularidade vs {metric}')
        ax1.set_xlabel('Estrelas')
        ax1.set_ylabel(metric)
        ax1.grid(True)

        # Gráfico de Maturidade (Idade do Repositório) vs Métrica de Qualidade
        ax2 = axes[1, i]
        ax2.scatter(df['Idade'], df[metric], color='green', alpha=0.5)
        ax2.set_title(f'Maturidade vs {metric}')
        ax2.set_xlabel('Idade (anos)')
        ax2.set_ylabel(metric)
        ax2.grid(True)

    plt.tight_layout()
    plt.subplots_adjust(top=0.9)
    plt.show()




