import re
import yaml
import numpy as np
import pandas as pd
from sqlalchemy import create_engine

with open("config.yaml", "r") as config_file:
    config = yaml.load(config_file, Loader=yaml.FullLoader)


def process_data():
    print("Processing database...")
    query = open(config["query-file"], 'r', encoding='utf-8').read()
    db_con = create_engine(config['input-data']['database'], encoding='utf-8')
    dataframe = pd.read_sql(query, db_con)
    return dataframe


def clean_data():
    print("Cleaning data...")
    df['QuestionText'] = df['QuestionText'].map(lambda x:
                                                '' if x is None else re.sub(r'<.*?>', '', x[2:-2])[34:-30])
    df['QuestionComments'] = df['QuestionComments'].map(lambda x:
                                                        '' if x is None else re.sub(r'<.*?>|\[\'|\'\]', '', x))
    df['AnswerComments'] = df['AnswerComments'].map(lambda x:
                                                    '' if x is None else re.sub(r'<.*?>|\[\'|\'\]', '', x))


if __name__ == "__main__":
    df = process_data()
    clean_data()

    data_headers = ''
    count_columns = len(df.columns)
    for i in range(0, count_columns):
        data_headers = data_headers + str(df.columns[i])
        if i != count_columns - 1:
            data_headers = data_headers + ' CUSTOM-DELIMITER '
    np.savetxt(config["input-data"]["file-path"], df, header=data_headers,
               delimiter=' CUSTOM-DELIMITER ', fmt='%s', encoding='utf-8')
