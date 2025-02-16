import os
import venv

venv_dir = ".venv"

# Criar ambiente virtual, se não existir
if not os.path.exists(venv_dir):
    print("Criando ambiente virtual...")
    venv.create(venv_dir, with_pip=True)

# Instalar dependências dentro do ambiente virtual
pip_exec = os.path.join(venv_dir, "Scripts" if os.name == "nt" else "bin", "pip")
os.system(f"{pip_exec} install -r requirements.txt")

print("Ambiente virtual configurado e dependências instaladas!")
