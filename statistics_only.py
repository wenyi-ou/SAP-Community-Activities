import re
import yaml
import pandas as pd
from tqdm import tqdm


with open("config.yaml", "r") as config_file:
    config = yaml.load(config_file, Loader=yaml.FullLoader)


def split_into_sentences(text):
    str_list = re.split('(-:::-)|(\\n)|(\\\)n|(\.)|(\!)|(\?)|(\;)|(\.{3,6})', text)
    # str_list = re.split('(-:::-)|(\\n)|(\\\)n|,|(\.)|(\!)|(\?)|(\;)|(\.{3,6})', text)
    filter(None, str_list)
    filter(lambda x: not x.isspace(), str_list)
    map(lambda x: x.strip(), str_list)
    return str_list


def identify(input_data, regex_file):
    row_count = len(input_data.index)
    print("Running regex identification... Questions count: ", str(row_count))
    processed = 0
    activities_count = 0
    my_dict = {}
    for index_output, row_output in (tqdm_iterator := tqdm(input_data.iterrows())):
        processed += 1
        tqdm_iterator.set_description("{:.2%}".format(processed / row_count))

        for content in row_output[config["input-data"]["contributions"]]:
            blocks = split_into_sentences(str(content))
            activities_count += len(blocks)
            for index_regex, row_regex in regex_file.iterrows():
                regex = row_regex[config["regex-file-columns"]["regex"]]
                for content_block in blocks:
                    if not isinstance(str(content_block), str):
                        continue
                    if re.search(regex, str(content_block), re.IGNORECASE):
                        cat_name = config["regex-file-columns"]["subcategory"]
                        if not row_regex[cat_name] in my_dict:
                            my_dict[row_regex[cat_name]] = 1
                        else:
                            my_dict[row_regex[cat_name]] += 1

    print("Categorization finished, total activities count: ", activities_count)
    with open(config['statistics']['statistics-only'], 'w') as csv_file:
        for category in my_dict.keys():
            csv_file.write("%s, %s\n" % (category, my_dict[category]))


if __name__ == "__main__":
    print("Reading regex file...")
    regex_def = pd.read_csv(config["regex-file"], delimiter=' CUSTOM-DELIMITER ', engine='python')

    print("Reading data from dataframe...")
    df = pd.read_csv(config["input-data"]["file-path"], delimiter=' CUSTOM-DELIMITER ', engine='python')

    identify(df, regex_def)
