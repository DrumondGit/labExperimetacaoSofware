import datetime
import json
import os
import time

import pandas as pd
import requests
import seaborn as sns
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from scipy.stats import spearmanr

load_dotenv()
token = os.getenv("GITHUB_TOKEN")

if not token:
    raise ValueError("Erro: O token do GitHub não foi encontrado. Verifique o arquivo .env.")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"

def make_github_request(query, max_retries=5):
    retries = 0
    while retries < max_retries:
        response = requests.post(GITHUB_GRAPHQL_URL, json={"query": query}, headers=headers)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 502:
            wait_time = 2 ** retries
            print(f"⚠️ Erro 502: Tentando novamente em {wait_time} segundos...")
            time.sleep(wait_time)
            retries += 1
        else:
            print(f"⚠️ Erro {response.status_code}: {response.text}")
            break
    return None

def fetch_repositories(total_repos=2, batch_size=1):
    all_repos = []
    cursor = None
    num_batches = total_repos // batch_size

    for batch in range(num_batches):
        print(f"🔄 Buscando repositórios... (Chamada {batch + 1}/{num_batches})")
        query = f"""
        {{
          search(query: "stars:>10000", type: REPOSITORY, first: {batch_size}, after: {json.dumps(cursor) if cursor else "null"}) {{
            edges {{
              node {{
                ... on Repository {{
                  name
                  owner {{ login }}
                  stargazerCount
                  primaryLanguage {{ name }}
                  url
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

        data = make_github_request(query)
        if data and "data" in data and data["data"].get("search"):
            repositories = data['data']['search']['edges']
            if not repositories:
                print("⚠️ Nenhum repositório encontrado.")
                break
            all_repos.extend(repositories)
            page_info = data['data']['search']['pageInfo']
            cursor = page_info["endCursor"] if page_info["hasNextPage"] else None
        else:
            print("❌ Erro ao buscar repositórios, encerrando a busca.")
            break

    return all_repos

def fetch_pull_requests(repository, max_pages=3):
    repo_name = repository['node']['name']
    owner = repository['node']['owner']['login']
    cursor = None
    reviewed_prs = []
    page_count = 0

    while page_count < max_pages:
        print(f"🔍 Buscando PRs revisados para {owner}/{repo_name} (Página {page_count + 1})")
        query = f"""
        {{
          repository(owner: "{owner}", name: "{repo_name}") {{
            pullRequests(states: [MERGED, CLOSED], first: 100, after: {json.dumps(cursor) if cursor else "null"}) {{
              nodes {{
                number
                title
                reviews(first: 1) {{
                  totalCount
                }}
              }}
              pageInfo {{
                hasNextPage
                endCursor
              }}
            }}
          }}
        }}
        """

        data = make_github_request(query)

        if data and "data" in data and data["data"].get("repository"):
            prs = data['data']['repository']['pullRequests']['nodes']
            reviewed_prs.extend([
                {"number": pr['number'], "title": pr['title']}
                for pr in prs
                if pr['reviews']['totalCount'] > 0
            ])

            page_info = data['data']['repository']['pullRequests']['pageInfo']
            cursor = page_info["endCursor"] if page_info["hasNextPage"] else None
            if not cursor:
                break
        else:
            print(f"⚠️ Erro ao buscar PRs para {owner}/{repo_name}.")
            break

        page_count += 1

    return reviewed_prs

def fetch_pr_details(owner, repo_name, pr_number):
    query = f"""
    {{
      repository(owner: "{owner}", name: "{repo_name}") {{
        pullRequest(number: {pr_number}) {{
          number
          title
          state
          bodyText
          createdAt
          closedAt
          mergedAt
          comments {{ totalCount }}
          participants {{ totalCount }}
          reviews {{ totalCount }}
          files(first: 100) {{
            totalCount
            nodes {{
              additions
              deletions
            }}
          }}
        }}
      }}
    }}
    """
    data = make_github_request(query)
    if data and "data" in data:
        return data["data"]["repository"]["pullRequest"]
    return None

def calculate_pr_metrics(pr_data):
    if not pr_data:
        return None

    created_at = datetime.datetime.strptime(pr_data['createdAt'], '%Y-%m-%dT%H:%M:%SZ')
    end_time = pr_data['mergedAt'] if pr_data['state'] == 'MERGED' else pr_data['closedAt']
    if not end_time:
        return None

    end_time = datetime.datetime.strptime(end_time, '%Y-%m-%dT%H:%M:%SZ')
    analysis_time = (end_time - created_at).total_seconds() / 3600
    if analysis_time < 1:
        return None

    total_files = pr_data['files']['totalCount']
    total_additions = sum(file['additions'] for file in pr_data['files']['nodes'])
    total_deletions = sum(file['deletions'] for file in pr_data['files']['nodes'])
    total_comments = pr_data['comments']['totalCount']
    total_participants = pr_data['participants']['totalCount']
    description_length = len(pr_data['bodyText']) if pr_data['bodyText'] else 0

    return {
        "pr_number": pr_data['number'],
        "state": pr_data['state'],
        "analysis_time_hours": analysis_time,
        "total_files": total_files,
        "total_additions": total_additions,
        "total_deletions": total_deletions,
        "description_length": description_length,
        "total_comments": total_comments,
        "total_participants": total_participants,
        "total_reviews": pr_data['reviews']['totalCount']
    }

def collect_repository_metrics(repository, max_prs=100):
    repo_name = repository['node']['name']
    owner = repository['node']['owner']['login']
    all_metrics = []
    print(f"\n📊 Coletando métricas para {owner}/{repo_name}...")
    reviewed_prs = fetch_pull_requests(repository)

    for pr in reviewed_prs[:max_prs]:
        pr_details = fetch_pr_details(owner, repo_name, pr['number'])
        metrics = calculate_pr_metrics(pr_details)
        if metrics:
            metrics.update({
                "repo_owner": owner,
                "repo_name": repo_name
            })
            all_metrics.append(metrics)

    return all_metrics

def process_data(repositories):
    repo_list = []
    for repo in repositories:
        repo_name = repo['node']['name']
        owner = repo['node']['owner']['login']
        reviewed_prs = fetch_pull_requests(repo)
        reviewed_pr_count = len(reviewed_prs)
        print(f"📌 {owner}/{repo_name} - PRs Revisados: {reviewed_pr_count}")
        pr_metrics = collect_repository_metrics(repo, max_prs=10) if reviewed_pr_count > 0 else []

        avg_metrics = {
            "avg_analysis_time": 0, "avg_files": 0, "avg_additions": 0,
            "avg_deletions": 0, "avg_description": 0, "avg_comments": 0,
            "avg_participants": 0, "avg_reviews": 0, "merge_rate": 0
        }

        if pr_metrics:
            df_metrics = pd.DataFrame(pr_metrics)
            analyze_correlations(df_metrics)
            avg_metrics = {
                "avg_analysis_time": df_metrics['analysis_time_hours'].mean(),
                "avg_files": df_metrics['total_files'].mean(),
                "avg_additions": df_metrics['total_additions'].mean(),
                "avg_deletions": df_metrics['total_deletions'].mean(),
                "avg_description": df_metrics['description_length'].mean(),
                "avg_comments": df_metrics['total_comments'].mean(),
                "avg_participants": df_metrics['total_participants'].mean(),
                "avg_reviews": df_metrics['total_reviews'].mean(),
                "merge_rate": len(df_metrics[df_metrics['state'] == 'MERGED']) / len(df_metrics)
            }

        node = repo['node']
        repo_data = {
            "Nome": node['name'],
            "Proprietário": node['owner']['login'],
            "Estrelas": node['stargazerCount'],
            "Linguagem Principal": node['primaryLanguage']['name'] if node['primaryLanguage'] else "Desconhecido",
            "Total PRs Revisados": reviewed_pr_count,
            "URL": node['url'],
            "Tempo Médio Análise (horas)": round(avg_metrics['avg_analysis_time'], 2),
            "Arquivos Médios por PR": round(avg_metrics['avg_files'], 1),
            "Linhas Adicionadas Média": round(avg_metrics['avg_additions'], 1),
            "Linhas Removidas Média": round(avg_metrics['avg_deletions'], 1),
            "Tamanho Médio Descrição": round(avg_metrics['avg_description'], 1),
            "Comentários Médios": round(avg_metrics['avg_comments'], 1),
            "Participantes Médios": round(avg_metrics['avg_participants'], 1),
            "Revisões Médias": round(avg_metrics['avg_reviews'], 1),
            "Taxa de Merge": f"{round(avg_metrics['merge_rate'] * 100, 1)}%",
        }
        repo_list.append(repo_data)

    return pd.DataFrame(repo_list)

def analyze_correlations(df):
    metrics = [
        "analysis_time_hours", "total_files", "total_additions",
        "total_deletions", "description_length", "total_comments",
        "total_participants", "total_reviews"
    ]
    corr_matrix = pd.DataFrame(index=metrics, columns=metrics)
    for i in range(len(metrics)):
        for j in range(len(metrics)):
            m1, m2 = metrics[i], metrics[j]
            corr, _ = spearmanr(df[m1], df[m2])
            corr_matrix.loc[m1, m2] = round(corr, 2)
    corr_matrix = corr_matrix.astype(float)
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", vmin=-1, vmax=1)
    plt.title("Matriz de Correlação (Spearman) entre Métricas dos Pull Requests")
    plt.tight_layout()
    plt.show()
    return corr_matrix
