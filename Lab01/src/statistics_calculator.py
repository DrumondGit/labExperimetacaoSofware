import pandas as pd


def calculate_mean(data):
    mean_values = [{}]

    for key, values in data.items():
        mean = values.mean()
        mean_values[0][key] = round(float(mean), 2)
    return pd.DataFrame(mean_values)


def calculate_median(data):
    median_values = [{}]

    for key, values in data.items():
        median = values.median()
        median_values[0][key] = round(float(median), 2)
    return pd.DataFrame(median_values)


def calculate_mode(data):
    mode_values = [{}]

    for key, values in data.items():
        mode = values.mode()
        mode_values[0][key] = mode.tolist()
    return pd.DataFrame(mode_values)
