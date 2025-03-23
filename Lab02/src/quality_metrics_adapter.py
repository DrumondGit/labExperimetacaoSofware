import os
import subprocess

import pandas as pd


def run_ck(repo_path, output_path, ck_dir):
    print(ck_dir)
    ck_jar_path = os.path.join("ck-0.7.1-SNAPSHOT-jar-with-dependencies.jar")

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    command = [
        "java", "-jar", ck_jar_path,
        repo_path,
        "true",
        "0",
        "true",
        output_path
    ]
    subprocess.run(command)


def summarize_ck_results(output_path):
    if not os.path.exists(output_path) or not os.path.isdir(output_path):
        raise FileNotFoundError(f"Diretório {output_path} não encontrado!")

    csv_files = [f for f in os.listdir(output_path) if f.endswith(".csv")]

    if not csv_files:
        raise FileNotFoundError(f"Nenhum arquivo CSV encontrado no diretório {output_path}!")

    metrics_summary = {
        "Média CBO (Classes)": None,
        "Média DIT (Classes)": None,
        "Média LCOM (Classes)": None,
        "Média CBO (Métodos)": None,
    }

    for csv_file in csv_files:
        file_path = os.path.join(output_path, csv_file)
        df = pd.read_csv(file_path)

        if csv_file.__contains__("class"):
            metrics_summary["Média CBO (Classes)"] = df["cbo"].mean()
            metrics_summary["Média DIT (Classes)"] = df["dit"].mean()
            metrics_summary["Média LCOM (Classes)"] = df["lcom"].mean()
        elif csv_file.__contains__("method"):
            metrics_summary["Média CBO (Métodos)"] = df["cbo"].mean()

    return metrics_summary
