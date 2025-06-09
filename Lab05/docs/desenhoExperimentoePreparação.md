# Lab05S01 - GraphQL vs REST: Desenho e Preparação do Experimento

## 1. Desenho do Experimento

### A. Hipóteses
- **Hipótese Nula (H0)**: Não há diferença significativa entre GraphQL e REST em termos de tempo de resposta e tamanho da resposta.
- **Hipótese Alternativa (H1)**: Há diferença significativa entre GraphQL e REST em termos de tempo de resposta e/ou tamanho da resposta.

### B. Variáveis Dependentes
- **Tempo de resposta** (em milissegundos).
- **Tamanho da resposta** (em bytes).

### C. Variáveis Independentes
- **Tipo de API utilizada**: REST ou GraphQL.

### D. Tratamentos
- **Tratamento 1**: Requisições feitas à API REST.
- **Tratamento 2**: Requisições equivalentes feitas à API GraphQL.

### E. Objetos Experimentais
- Um mesmo sistema backend disponibilizando as duas APIs (REST e GraphQL).
- Exemplo: GitHub API (REST e GraphQL) ou backend próprio com banco de dados simulado contendo entidades como Usuário, Posts e Comentários.

### F. Tipo de Projeto Experimental
- **Experimento controlado com medidas repetidas**: Cada operação será realizada diversas vezes com ambos os tipos de API em um mesmo ambiente, controlando variáveis externas.

### G. Quantidade de Medições
- Para cada tipo de requisição (ex.: `getAllUsers`, `getUserWithPosts`), serão feitas **30 execuções** para REST e **30 execuções** para GraphQL, totalizando 60 medições por tipo de operação.

### H. Ameaças à Validade
- **Validade interna**:
  - Variação de rede pode afetar o tempo de resposta → mitigado executando localmente ou em rede estável.
  - Caching pode influenciar → mitigar com aquecimento e limpeza de cache entre execuções.
- **Validade externa**:
  - Resultados podem não generalizar para APIs em larga escala.
- **Validade de construção**:
  - As requisições REST e GraphQL devem ser semanticamente equivalentes para garantir a comparabilidade.

---

## 2. Preparação do Experimento

### Ferramentas e Tecnologias
- **Backend REST/GraphQL**: Backend próprio com Node.js + Express (REST) e Apollo Server (GraphQL), ou uso da GitHub API.
- **Banco de dados**: SQLite ou mock em JSON.
- **Ferramentas de medição**:
  - Scripts Python com `requests` (REST) e `gql` ou `httpx` (GraphQL).
  - `time.perf_counter()` para medir tempo.
  - `len(response.content)` para medir tamanho da resposta.

### Etapas de Preparação
1. **Criar backend** (caso não use GitHub):
   - Entidades: Usuário, Post, Comentário.
   - API REST: Endpoints como `/users`, `/users/:id/posts`.
   - API GraphQL: Queries como `users`, `user(id) { posts }`.

2. **Desenvolver scripts de teste**:
   - Script Python que:
     - Executa a mesma consulta via REST e GraphQL.
     - Mede o tempo de resposta.
     - Mede o tamanho da resposta.
     - Salva os dados em CSV para posterior análise.

3. **Preparar ambiente controlado**:
   - Executar localmente para minimizar interferência de rede.
   - Desligar serviços paralelos que possam afetar a performance.
   - Realizar "aquecimento" das APIs antes das medições principais.

---