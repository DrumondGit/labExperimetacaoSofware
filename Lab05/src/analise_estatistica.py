import pandas as pd
from scipy import stats

# Carregar dados
df = pd.read_csv("resultados.csv")

# Separar REST e GraphQL
rest = df[df['API'] == 'REST']
graphql = df[df['API'] == 'GraphQL']

# Tempo de resposta
t_rest = rest['Tempo_ms']
t_graphql = graphql['Tempo_ms']

# Tamanho da resposta
size_rest = rest['Tamanho_bytes']
size_graphql = graphql['Tamanho_bytes']

# Teste t para tempo
t_stat_tempo, p_value_tempo = stats.ttest_rel(t_rest, t_graphql)
# Teste t para tamanho
t_stat_size, p_value_size = stats.ttest_rel(size_rest, size_graphql)

# Resultados
print("===== TEMPO DE RESPOSTA =====")
print(f"REST Média: {t_rest.mean():.2f} ms")
print(f"GraphQL Média: {t_graphql.mean():.2f} ms")
print(f"p-valor: {p_value_tempo}")

print("\n===== TAMANHO DA RESPOSTA =====")
print(f"REST Média: {size_rest.mean():.2f} bytes")
print(f"GraphQL Média: {size_graphql.mean():.2f} bytes")
print(f"p-valor: {p_value_size}")
