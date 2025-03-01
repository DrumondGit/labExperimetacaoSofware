from datetime import datetime, timezone

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


def calculate_last_update_statistics(data):
    data_values = data.values
    last_update_values = []

    for value in data_values:
        last_update = pd.to_datetime(value[0])
        last_update_values.append(last_update)

    series_value = pd.Series(last_update_values)
    mean = series_value.mean()
    median = series_value.median()
    mode = series_value.mode()

    return {
        'mean': mean,
        'median': median,
        'mode': mode
    }


def calculate_repositories_middle_age(data):
    repos_age = []
    data_values = data.values

    for value in data_values:
        creation_date = pd.to_datetime(value[0])
        age = datetime.now(timezone.utc) - creation_date
        repos_age.append(age.days)

    series_value = pd.Series(repos_age)
    middle_age = series_value.mean() / 365.25
    return round(float(middle_age), 1)

def get_popular_languages(data):
    data_values = data.values
    ignored_values = ['Desconhecido', 'Markdown']

    languages = [item[0] for item in data_values]
    languages_series = pd.Series(languages)
    filtered_languages = languages_series[~languages_series.isin(ignored_values)]
    languages_by_popularity = filtered_languages.value_counts()

    return pd.DataFrame(languages_by_popularity)