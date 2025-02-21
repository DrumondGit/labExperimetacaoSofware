import pandas as pd


def csv_writer(data, filename):
    dataframe = pd.DataFrame(data)
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        csvfile.write(dataframe.to_string(index=False))
