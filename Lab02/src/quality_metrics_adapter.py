import os
import subprocess

from git import Repo

ck_url = os.getenv("CK_REPO_URL")

# Diretório onde os repositórios estão clonados
# repos_dir = "/caminho/para/repositorios"
# Diretório de saída para os resultados do CK
# output_dir = "/caminho/para/saida"
# current_dir = os.path.dirname(__file__)
#
# ck_dir = os.path.join(current_dir, "ck")

def clone_ck_repo(current_dir):
    Repo.clone_from(ck_url, current_dir)

def generate_jar_files (current_dir, ck_dir):
    os.chdir(ck_dir)
    command = ["mvn", "clean", "install", "-U"]
    subprocess.run(command)

def run_ck(repo_path, output_path, ck_dir):
    ck_jar_path = os.path.join(ck_dir, "target/ck-0.7.1-SNAPSHOT-jar-with-dependencies.jar")

    command = [
        "java", "-jar", ck_jar_path,
        repo_path,
        "false",
        "0",
        "false",
        output_path
    ]
    subprocess.run(command)

# Percorre todos os repositórios no diretório especificado
# for repo_name in os.listdir(repos_dir):
#     repo_path = os.path.join(repos_dir, repo_name)
#     repo_output_dir = os.path.join(output_dir, repo_name)
#
#     # Cria o diretório de saída para o repositório atual
#     os.makedirs(repo_output_dir, exist_ok=True)
#
#     # Executa o CK no repositório atual
#     print(f"Analisando repositório: {repo_name}")
#     run_ck(repo_path, repo_output_dir)
#     print(f"Análise concluída para: {repo_name}")
#
# print("Análise de todos os repositórios concluída.")