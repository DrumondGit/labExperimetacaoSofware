import os
import subprocess

import pandas as pd


import os
import subprocess

def run_ck(repo_path, output_path, ck_dir):
    print(ck_dir)
    ck_jar_path = "Lab02/src/ck-0.7.1-SNAPSHOT-jar-with-dependencies.jar"

    # Verifica se o caminho de saída existe, se não, cria
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # Monta o comando Java para executar o CK
    command = [
        "java", "-jar", ck_jar_path,
        repo_path,
        "true",
        "0",
        "true",
        output_path
    ]

    try:
        # Executa o comando Java
        subprocess.run(command, check=True)
        print(f"Análise concluída para o repositório {repo_path}. Resultados em {output_path}")
    except subprocess.CalledProcessError as e:
        # Captura qualquer erro de execução do subprocess
        print(f"Erro ao executar o CK para o repositório {repo_path}: {e}")
    except Exception as e:
        # Captura qualquer outra exceção
        print(f"Erro inesperado ao rodar o CK para o repositório {repo_path}: {e}")


import os
import pandas as pd

def summarize_ck_results(output_path):
    if not os.path.exists(output_path) or not os.path.isdir(output_path):
        raise FileNotFoundError(f"Diretório {output_path} não encontrado!")

    csv_files = [f for f in os.listdir(output_path) if f.endswith(".csv")]

    if not csv_files:
        raise FileNotFoundError(f"Nenhum arquivo CSV encontrado no diretório {output_path} !")

    metrics_summary = {
        "Média CBO (Classes)": None,
        "Média DIT (Classes)": None,
        "Média LCOM (Classes)": None,
        "Média CBO (Métodos)": None,
    }

    for csv_file in csv_files:
        file_path = os.path.join(output_path, csv_file)
        
        # Verificar se o arquivo não está vazio antes de tentar ler
        if os.path.getsize(file_path) == 0:
            print(f"⚠ O arquivo {csv_file} está vazio e foi ignorado.")
            continue  # Ignora o arquivo vazio
        
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            print(f"Erro ao ler o arquivo {csv_file}: {e}")
            continue  # Ignora arquivos que não puderam ser lidos

        if csv_file.__contains__("class"):
            if "cbo" in df.columns and "dit" in df.columns and "lcom" in df.columns:
                metrics_summary["Média CBO (Classes)"] = df["cbo"].mean()
                metrics_summary["Média DIT (Classes)"] = df["dit"].mean()
                metrics_summary["Média LCOM (Classes)"] = df["lcom"].mean()
            else:
                print(f"⚠ O arquivo {csv_file} não contém as colunas esperadas.")
        elif csv_file.__contains__("method"):
            if "cbo" in df.columns:
                metrics_summary["Média CBO (Métodos)"] = df["cbo"].mean()
            else:
                print(f"⚠ O arquivo {csv_file} não contém a coluna 'cbo'.")

    return metrics_summary
