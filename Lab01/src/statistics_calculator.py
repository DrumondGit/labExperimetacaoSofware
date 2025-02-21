import pandas as pd


def calculate_mean(data):
    df = pd.DataFrame(data)
    mean_values = [{}]
    values_to_calculate_mean = df[['Estrelas', 'Releases', 'Pull Requests Aceitos', 'Total de Issues']]

    for key, values in values_to_calculate_mean.items():
        mean = values.mean()
        mean_values[0][key] = round(float(mean), 2)
    return pd.DataFrame(mean_values)


def calculate_median(data):
    df = pd.DataFrame(data)
    median_values = [{}]
    values_to_calculate_median = df[['Estrelas', 'Releases', 'Pull Requests Aceitos', 'Total de Issues']]

    for key, values in values_to_calculate_median.items():
        median = values.median()
        median_values[0][key] = round(float(median), 2)
    return pd.DataFrame(median_values)


def calculate_mode(data):
    df = pd.DataFrame(data)
    mode_values = [{}]
    values_to_calculate_mode = df[['Estrelas', 'Releases', 'Pull Requests Aceitos', 'Total de Issues']]

    for key, values in values_to_calculate_mode.items():
        mode = values.mode()
        mode_values[0][key] = mode.tolist()
    return pd.DataFrame(mode_values)
