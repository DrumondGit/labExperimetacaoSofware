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