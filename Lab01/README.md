# labExperimetacaoSofware

## Relatório final do projeto

[Veja a documentação](/Lab01/docs)

## Configurar o ambiente

1. Crie um ambiente virtual usando o seguinte comando:

    ```bash
    pip install pandas file-adapter repositories-adapter statistics-calculator json5 requests python-dotenv matplotlib
    ```

2. Ative o ambiente virtual:
    - No macOS e Linux:
        ```bash
        source .venv/bin/activate
        ```
        ou

        ```bash
        source .venv/Scripts/activate
        ```         
  - No Windows:
      ```bash
      .venv\Scripts\activate
      ```
## Instalar dependências

De o seguinte comando:

```bash
pip install
```
Ou esse (so funciona se rodar o comando de run no terminal):

```bash
python install_dependencies.py
```
- Caso você esteja usando Power Shell e dê algum erro, habilite as permissões: 

```bash
Set-ExecutionPolicy Unrestricted -Scope Process
```

### Passo 3: Executar o script

Antes de executar o script principal do projeto, você precisa configurar algumas variáveis. 

1. Substitua os valores das seguintes variáveis no .env:

```
# Seu token do GitHub (crie um token em https://github.com/settings/tokens)
GITHUB_TOKEN = 'seutokenaqui'

# Nome do usuário no GitHub
GITHUB_USERNAME = 'nomedousuarioaqui'
```

- **GITHUB_TOKEN**: Para gerar seu token, vá até [Configurações de Tokens do GitHub](https://github.com/settings/tokens) e crie um novo token com as permissões necessárias. Esse token será usado para autenticar as requisições à API do GitHub.

- **GITHUB_USERNAME**: Aqui você pode colocar seu próprio nome de usuário do GitHub ou o nome de usuário de outra pessoa. Esse valor é usado para buscar os repositórios desse usuário na plataforma.

2. Após configurar essas variáveis, execute o script principal do projeto com o seguinte comando:

```bash
python main.py
```

## Integrantes do grupo

- Guilherme Drumond Silva
- Henrique Pinto Santos
