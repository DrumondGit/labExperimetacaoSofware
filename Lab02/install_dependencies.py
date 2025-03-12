import os
import subprocess
import sys
import venv

venv_dir = ".venv"

# Criar ambiente virtual, se não existir
if not os.path.exists(venv_dir):
    print("Criando ambiente virtual...")
    venv.create(venv_dir, with_pip=True)

# Determinar o executável do Python dentro do ambiente virtual
python_exec = os.path.join(venv_dir, "Scripts", "python.exe" if os.name == "nt" else "bin/python")

# Verificar se o pip está instalado corretamente
subprocess.run([python_exec, "-m", "ensurepip"], check=True)

# Instalar dependências dentro do ambiente virtual
subprocess.run([python_exec, "-m", "pip", "install", "--upgrade", "pip"], check=True)
subprocess.run([python_exec, "-m", "pip", "install", "-r", "requirements.txt"], check=True)

print("✅ Ambiente virtual configurado e dependências instaladas!")
