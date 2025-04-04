
import repositories_adapter

# Run
repositories = repositories_adapter.fetch_repositories()
if repositories:
    df = repositories_adapter.process_data(repositories)
    if df is not None:
        print(df.to_string())






