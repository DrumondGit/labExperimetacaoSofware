# Caracterização do Dataset - Firefox Bugs

## Base de dados utilizada
- https://github.com/av9ash/gitbugs/blob/main/firefox/Firefox_bugs.csv.zip

## Introdução
Business Intelligence (BI) é um conjunto de tecnologias e práticas que permite a coleta, análise e visualização de dados com o objetivo de apoiar a tomada de decisões estratégicas. No contexto deste trabalho, aplicamos técnicas de BI por meio da ferramenta Microsoft Power BI para realizar uma análise exploratória de uma base pública de dados de bugs do projeto Firefox. O foco desta etapa é caracterizar os principais aspectos da base de dados utilizada, facilitando o entendimento de seus padrões e distribuição.

## Metodologia / Descrição da base

A base utilizada neste trabalho foi obtida no repositório público GitHub Bug Dataset, disponível via Zenodo (https://zenodo.org/record/3964980). Ela contém informações extraídas do sistema de rastreamento de bugs Bugzilla, com foco em projetos de código aberto, incluindo o navegador Firefox. O arquivo utilizado está em formato CSV e contém registros de bugs com atributos como:

- ID do bug (id)
- Prioridade (priority)
- Status atual (bug_status)
- Componente relacionado (component)
- Data de criação (creation_ts)
- Última modificação (delta_ts)
- Produto associado (product)

Após a obtenção do arquivo, realizamos um pré-processamento básico para garantir a integridade das colunas e facilitar a importação no Power BI. Foram removidos valores nulos e formatadas colunas de data e texto.

## Resultados

- Foram criadas diversas visualizações no Power BI para caracterizar o conjunto de dados. Abaixo, descrevemos os principais achados:
- Distribuição por Prioridade: A maior parte dos bugs relatados possui prioridade P3, seguida por P2 e P1. Isso indica que a maioria dos bugs tem prioridade intermediária.
- Bugs por Status: Os status mais frequentes são RESOLVED e CLOSED, representando a maioria dos casos. Também há uma quantidade relevante de bugs com status NEW.
- Bugs por Componente: Os componentes “General” e “Graphics” concentram um volume elevado de bugs, sugerindo áreas de maior atividade ou complexidade no projeto.
- Evolução Temporal: A distribuição dos bugs ao longo do tempo mostra maior atividade de criação de bugs entre os anos de 2009 e 2013, com uma redução progressiva nos anos seguintes.

## Discussão

A caracterização da base mostra que o projeto Firefox possui um processo estruturado de triagem de bugs, com grande parte dos problemas tendo um status de resolução definido. A predominância de prioridades intermediárias pode sugerir que muitas falhas não são críticas, ou que a categorização pode ser feita de forma conservadora. A concentração de bugs em poucos componentes reforça a ideia de áreas mais sensíveis no projeto. O padrão temporal sugere que a base cobre um intervalo histórico amplo, com uma possível diminuição da atividade ao longo do tempo.

Essa análise inicial fornece insumos relevantes para estudos futuros e a formulação de questões de pesquisa mais específicas a partir dos dados.