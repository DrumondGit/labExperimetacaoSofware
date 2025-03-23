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
import argparse

# Carregar variáveis de ambiente
load_dotenv()

# TOKEN = os.getenv("GITHUB_TOKEN")
# API_URL = os.getenv("GITHUB_API_URL")
# ck_path = os.getenv("CK_REPO_PATH")

API_URL = os.environ.get("API_URL")
TOKEN = os.environ.get("TOKEN")
ck_path = os.environ.get("CK_REPO_URL")

GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Limite máximo de caminho para Windows
MAX_PATH_LENGTH = 260

def fetchRepositories(start, end):
    """Faz a requisição GraphQL com paginação para obter repositórios em intervalos definidos."""
    allRepos = []
    cursor = None
    totalRepos = end - start  # Número total de repositórios desejado
    batchSize = 20  # Repositórios por chamada
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
        for file in files:
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

        repo_name = node['name']
        if len(repo_name) > 100:  
            print(f"❌ Repositório {repo_name} ignorado (nome muito longo)")
            continue
        clean_name = clean_repo_name(repo_name)

        repo_url = f"https://github.com/{node['owner']['login']}/{clean_name}.git"

        repo_owner = node['owner']['login']  
        current_dir = os.getcwd()
        parent_path = os.path.dirname(current_dir)
        repo_path = os.path.join(current_dir + "\\Lab02\\src\\repo", clean_name)

        clone_repo(repo_path, repo_url)  # Clonando para o caminho certo

        output_path = os.path.join(current_dir  + "\\Lab02\\src\\repo", clean_name)
        output_path2 = os.path.join(current_dir  + "\\Lab02\\src\\repo")

        if os.path.exists(output_path2) and has_java_files(repo_path):
            code_lines, comment_lines = count_lines(repo_path)
            quality_metrics_adapter.run_ck(repo_path, output_path, ck_path)
            quality_metrics = quality_metrics_adapter.summarize_ck_results(output_path2)
            remove_repo(output_path2)

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

    remove_repo(output_path2)

    return pd.DataFrame(repoList)

import re
def clean_repo_name(repo_name):
    clean_name = re.sub(r'[^\w\s-]', '_', repo_name)  
    clean_name = clean_name.strip()  
    return clean_name

def calculate_repos_age(creation_date):
    repo_age_timezone = datetime.now(timezone.utc) - pd.to_datetime(creation_date)
    repo_age = repo_age_timezone.days / 325.25
    return round(float(repo_age), 1)

def clone_repo(clone_path, repo_url):
    if os.path.exists(clone_path):
        remove_repo(clone_path)

    try:
        Repo.clone_from(repo_url, clone_path)
    except Exception as e:
        print(f"⚠ Erro ao clonar o repositório: {e}")

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
    """Remove um repositório clonado."""
    try:
        shutil.rmtree(repo_path, onerror=remove_readonly)
        print(f"✅ Repositório {repo_path} removido com sucesso!")
    except Exception as e:
        print(f"⚠ Erro ao excluir repositório {repo_path}: {e}")

def remove_readonly(func, path, _):
    os.chmod(path, stat.S_IWRITE)
    func(path)

def plotGraphs(df, output_dir='Lab02/reports'):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    metrics = ['Média CBO (Classes)', 'Média DIT (Classes)', 'Média LCOM (Classes)']
    graph_paths = []

    fig, axes = plt.subplots(2, len(metrics), figsize=(15, 10))
    fig.suptitle('Popularidade vs Métricas de Qualidade e Maturidade vs Métricas de Qualidade')

    for i, metric in enumerate(metrics):
        ax1 = axes[0, i]
        ax1.scatter(df['Estrelas'], df[metric], color='blue', alpha=0.5)
        ax1.set_title(f'Popularidade vs {metric}')
        ax1.set_xlabel('Estrelas')
        ax1.set_ylabel(metric)
        ax1.grid(True)

        ax2 = axes[1, i]
        ax2.scatter(df['Idade'], df[metric], color='green', alpha=0.5)
        ax2.set_title(f'Maturidade vs {metric}')
        ax2.set_xlabel('Idade (anos)')
        ax2.set_ylabel(metric)
        ax2.grid(True)

    for i in range(len(metrics)):
        svg_output = io.StringIO()
        fig.savefig(svg_output, format='svg')
        svg_output.seek(0)

        svg_content = svg_output.getvalue()
        encoded_svg = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
        
        graph_paths.append(f"data:image/svg+xml;base64,{encoded_svg}")

    plt.tight_layout()
    plt.subplots_adjust(top=0.9)
    plt.close(fig)

    return graph_paths

def generate_html_report(df, graphs, report_path='Lab02/reports/report.html'):
    html_content = """
    <html>
    <head>
        <title>Relatório de Repositórios</title>
        <style>
            body { font-family: Arial, sans-serif; }
            h1 { color: #2c3e50; }
            table { width: 100%; border-collapse: collapse; }
            th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background-color: #f2f2f2; }
            .graph { width: 100%; height: 400px; margin-top: 30px; }
        </style>
    </head>
    <body>
        <h1>Relatório de Repositórios GitHub</h1>
        <h2>Dados dos Repositórios</h2>
        <table>
            <thead>
                <tr>
                    <th>Nome</th>
                    <th>Proprietário</th>
                    <th>Idade</th>
                    <th>Estrelas</th>
                    <th>Pull Requests Aceitos</th>
                    <th>Releases</th>
                    <th>Linhas de Código</th>
                    <th>Linhas de Comentário</th>
                    <th>Média CBO (Classes)</th>
                    <th>Média DIT (Classes)</th>
                    <th>Média LCOM (Classes)</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for _, row in df.iterrows():
        html_content += f"""
        <tr>
            <td>{row['Nome']}</td>
            <td>{row['Proprietário']}</td>
            <td>{row['Idade']}</td>
            <td>{row['Estrelas']}</td>
            <td>{row['Pull Requests Aceitos']}</td>
            <td>{row['Releases']}</td>
            <td>{row['Linhas de código']}</td>
            <td>{row['Linhas de comentário']}</td>
            <td>{row['Média CBO (Classes)']}</td>
            <td>{row['Média DIT (Classes)']}</td>
            <td>{row['Média LCOM (Classes)']}</td>
        </tr>
        """
    
    html_content += """
            </tbody>
        </table>
    """
    
    html_content += "<h2>Gráficos</h2>"
    
    for i, graph in enumerate(graphs):
        html_content += f"""
        <div class="graph">
            <h3>Gráfico {i + 1}</h3>
            <img src="{graph}" alt="Gráfico {i + 1}">
        </div>
        """
    
    html_content += """
    </body>
    </html>
    """
    
    with open(report_path, 'w') as file:
        file.write(html_content)
