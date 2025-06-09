import repositories_adapter

# Run
repositories = repositories_adapter.fetchRepositories()
if repositories:
    df = repositories_adapter.processData(repositories)




