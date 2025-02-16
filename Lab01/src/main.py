import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Carregar o token e a URL da API do arquivo .env
token = os.getenv("GITHUB_TOKEN")
apiBaseURL = os.getenv("GITHUB_API_URL")

# Montar a URL completa da API
apiURL = f"{apiBaseURL}/games"

# Cabeçalhos com o token de autenticação
headers = {
    "Authorization": f"Bearer {token}"  # Corrigido: adicionando o espaço entre Bearer e o token
}

# Parâmetros da requisição
params = {
    'per_page': 100
}

# Enviar a requisição GET para a API
response = requests.get(apiURL, headers=headers, params=params)

# Verificar se a requisição foi bem-sucedida
if response.status_code == 200:
    print(response.json())  # Exibir a resposta JSON
else:
    print(f"Erro {response.status_code}: {response.text}")  # Exibir erro caso a requisição falhe
