import json
import os
import time
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

def make_github_request(query, max_retries=5):
    """Faz uma requisição ao GitHub GraphQL com retry em caso de erro 502."""
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

def fetch_repositories():
    """Obtém os 200 repositórios mais populares no GitHub."""
    all_repos = []
    cursor = None
    total_repos = 200
    batch_size = 20
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
                  pullRequests(states: [MERGED, CLOSED], first: 100) {{
                    totalCount
                    nodes {{
                      reviews {{ totalCount }}
                    }}
                  }}
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
        if data and "data" in data:
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

def process_data(repositories):
    """Filtra PRs com pelo menos uma revisão e estrutura os dados em um DataFrame."""
    repo_list = []
    
    for repo in repositories:
        node = repo['node']
        pull_requests = [pr for pr in node['pullRequests']['nodes'] if pr['reviews']['totalCount'] > 0]
        
        if len(pull_requests) >= 100:
            repo_list.append({
                "Nome": node['name'],
                "Proprietário": node['owner']['login'],
                "Estrelas": node['stargazerCount'],
                "Linguagem Principal": node['primaryLanguage']['name'] if node['primaryLanguage'] else "Desconhecido",
                "Total PRs Revisados": len(pull_requests)
            })
    
    return pd.DataFrame(repo_list)