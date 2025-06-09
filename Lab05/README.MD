# GraphQL vs REST - Experimento Controlado

Este projeto tem como objetivo comparar, de forma controlada, o desempenho de APIs GraphQL e REST. A comparação será realizada com foco em duas métricas principais:

- **RQ1**: Tempo de resposta das requisições
- **RQ2**: Tamanho das respostas em bytes

## Estrutura do Projeto

├── backend/
│ ├── rest/ # Código da API REST
│ └── graphql/ # Código da API GraphQL
├── scripts/
│ └── measure.py # Script para medir tempo e tamanho das respostas
├── data/
│ └── results.csv # Resultados dos experimentos (futuramente)
├── Lab05S01_Experimento_GraphQL_vs_REST.md # Desenho e preparação do experimento
└── README.md

## Tecnologias

- Node.js + Express (REST)
- Apollo Server (GraphQL)
- SQLite (ou dados mockados)
- Python (para medição)
  - `requests`
  - `time`
  - `csv` / `pandas`

## Como Executar (em construção)

1. Instale as dependências do backend:
   ```
   cd backend/rest
   npm install

   cd ../graphql
   npm install
    ```
    
2. Rode os servidores:   
    ```
    node index.js 
    ```

3. Execute os scripts de medição (em breve):    
    ```
    python scripts/measure.py
    ```
