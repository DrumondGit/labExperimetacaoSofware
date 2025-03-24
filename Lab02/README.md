# *Laboratório 02 - Características de repositórios populares*  

## *Objetivo*  

Este projeto tem como objetivo analisar a qualidade interna de repositórios Java open-source no GitHub, correlacionando-a com características do processo de desenvolvimento, como popularidade, maturidade, atividade e tamanho. Serão coletados dados dos 1.000 repositórios Java mais populares, utilizando métricas de qualidade (CBO, DIT, LCOM) obtidas com a ferramenta CK e métricas de processo (estrelas, linhas de código, releases, idade). O estudo busca responder quatro questões de pesquisa, identificando relações entre essas métricas para entender como práticas colaborativas impactam a qualidade do software.  

---

## *Questões de Pesquisa*  

- Qual a relação entre a popularidade dos repositórios e as suas características de
qualidade?   
- Qual a relação entre a maturidade do repositórios e as suas características de
qualidade ?  
- Qual a relação entre a atividade dos repositórios e as suas características de
qualidade?  
- Qual a relação entre o tamanho dos repositórios e as suas características de
qualidade?  

---

## *Configuração do Token da API GitHub*  

O script de coleta requer um *token de autenticação* do GitHub. O token pode ser configurado automaticamente via terminal ou salvo em um arquivo .env.config na raiz do projeto, no seguinte formato:


GITHUB_TOKEN=seu_token_aqui


Caso precise gerar um token, siga os passos:  
1. Acesse [GitHub Developer Settings](https://github.com/settings/tokens).  
2. Clique em *"Generate new token (classic)"*.  
3. Selecione as permissões:  
   - repo → Acesso a repositórios públicos  
   - read:org → Acesso a informações organizacionais (se necessário)  
4. Copie o token gerado e adicione ao projeto.  

---

## *Sprints do Projeto*  

### *Sprint 1 - Coleta de Dados e Análise Inicial*  

*Objetivos:*  
- Coletar *1000 repositórios Java* populares via *API do GitHub*.  
- Clonar os repositórios coletados automaticamente.  
- Extrair métricas de código usando a ferramenta *CK*.  
- Organizar e armazenar os dados coletados para análise.  

*Dependências:*  
```bash
  pip install --quiet json5 python-dotenv matplotlib pandas requests GitPython pygount
```

### *Como Executar*  

- *Clone o repositório:*  
``` bash
   git clone https://github.com/DrumondGit/labExperimetacaoSofware.git
```

- Navegue até o diretório *labExperimetacaoSofware/Lab02/src*: 
- Execute o main do projeto:
``` bash
   python main.py
```
- Caso queira consultar os resultados da nossa pipeline, acesse: [Pipeline](https://github.com/DrumondGit/labExperimetacaoSofware/actions/runs/14023141025)
---

## *Integrantes do Projeto*  

- Guilherme Drumond
- Henrique Pinto Santos
