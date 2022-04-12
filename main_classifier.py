import re
import csv
import yaml
import pandas as pd
from tqdm import tqdm

with open("config.yaml", "r") as config_file:
    config = yaml.load(config_file, Loader=yaml.FullLoader)

index_primary = {}
index_secondary = {}


def categorize(field, is_primary):
    if is_primary:
        dictionary = index_primary
    else:
        dictionary = index_secondary
    if field in dictionary:
        dictionary[field] += 1
    else:
        dictionary[field] = 1


'''
pattern_domain = re.compile(r"(?:http://|https://)?(?:[\w](?:[\w\-]{0,61}[\w])?\.)+[a-zA-Z]{2,6}/")
pattern_ip = pattern = re.compile(r"((?:(?:25[0-5]|2[0-4]\d|[01]?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d?\d))")
pattern_date = re.compile(r"\d{4}(?:-|/|.)\d{1,2}(?:-|/|.)\d{1,2}")
pattern_email = re.compile(r"[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+")
regex_dict = {
    r'^[0-9]*$': 'Numbers',
    r'^\d{7,}$': 'Numeric String',
}
def identify(regex_dict, text):
    for key, value in regex_dict.items():
        pattern = re.compile(str(key))
        matches = pattern.finditer(text)
        matches_list = []

        for match in matches:
            matches_list.append(match.group(0))

        if len(matches_list) != 0:
            print(value + ' - ' + str(matches_list))
'''


def split_into_sentences(text):
    # text = re.sub('([\.\!\?])([^”’])', r"\1\n\2", text)
    # text = re.sub('(\.{3,6})([^”’])', r"\1\n\2", text)
    # text = re.sub('([\.\!\?][”’])([^\.\!\?])', r'\1\n\2', text)
    # text = re.sub(r'(<.*?>)|(\[\')|(\'\])', '', text) # remove HTML tags
    # text = text.rstrip()  # remove line breaks
    # return text.split("\n")

    str_list = re.split('(-:::-)|(\\n)|(\\\)n|(\.)|(\!)|(\?)|(\;)|(\.{3,6})', text)
    # str_list = re.split('(-:::-)|(\\n)|(\\\)n|,|(\.)|(\!)|(\?)|(\;)|(\.{3,6})', text)
    filter(None, str_list)
    filter(lambda x: not x.isspace(), str_list)
    map(lambda x: x.strip(), str_list)
    return str_list


def identify(input_data, regex_file):
    category = []
    subcategory = []
    regex_output = []
    my_dict_primary = {}
    my_dict_secondary = {}

    row_count = len(input_data.index)
    print("Running regex identification... Questions count: ", str(row_count))
    processed = 0
    activities_count = 0
    for index_output, row_output in (tqdm_iterator := tqdm(input_data.iterrows())):
        processed += 1
        tqdm_iterator.set_description("{:.2%}".format(processed / row_count))

        temp_category = []
        temp_sub_category = []
        temp_regex = []

        for content in row_output[config["input-data"]["contributions"]]:
            blocks = split_into_sentences(str(content))
            filter(None, blocks)
            filter(lambda x: not x.isspace(), blocks)
            map(lambda x: x.strip(), blocks)
            activities_count += len(blocks)
            for index_regex, row_regex in regex_file.iterrows():
                regex = row_regex[config["regex-file-columns"]["regex"]]
                for content_block in blocks:
                    if not isinstance(str(content_block), str):
                        continue
                    if re.search(regex, str(content_block), re.IGNORECASE):
                        temp_regex.append(regex)
                        if not row_regex[config["regex-file-columns"]["regex"]] == "None":
                            if not row_regex[config["regex-file-columns"]["subcategory"]] in temp_sub_category:
                                cat = row_regex[config["regex-file-columns"]["subcategory"]]
                                if cat not in my_dict_secondary:
                                    my_dict_secondary[cat] = []
                                my_dict_secondary[cat].append(content_block)
                                temp_sub_category.append(cat)
                                categorize(row_regex[config["regex-file-columns"]["subcategory"]], False)
                        if not row_regex[config["regex-file-columns"]["category"]] in temp_category:
                            cat = row_regex[config["regex-file-columns"]["category"]]
                            if cat not in my_dict_primary:
                                my_dict_primary[cat] = []
                            my_dict_primary[cat].append(content_block)
                            temp_category.append(cat)
                            categorize(row_regex[config["regex-file-columns"]["category"]], True)

        category.append(", ".join(temp_category))
        subcategory.append(", ".join(temp_sub_category))
        regex_output.append(", ".join(temp_regex))

    input_data["Category"] = category
    input_data["Subcategory"] = subcategory
    input_data["Regex"] = regex_output

    input_data_unmatched = input_data[input_data["Category"] != ""]
    input_data_unmatched.to_csv(config["output-data"]["unmatched"], index=False)
    input_data.to_csv(config["output-data"]["file-path"], index=False)

    with open(config["output-data"]["categorized-primary"], "w") as output_file:
        csv_writer = csv.writer(output_file)
        csv_writer.writerow(my_dict_primary.keys())
        csv_writer.writerows(zip(*my_dict_primary.values()))
    with open(config["output-data"]["categorized-secondary"], "w") as output_file:
        csv_writer = csv.writer(output_file)
        csv_writer.writerow(my_dict_secondary.keys())
        csv_writer.writerows(zip(*my_dict_secondary.values()))

    print(index_primary)
    print(index_secondary)
    primary_analysis = pd.DataFrame(index_primary.items(), columns=['Category', 'Count'])
    primary_analysis.to_csv(config['statistics']['category'], index=False)
    secondary_analysis = pd.DataFrame(index_secondary.items(), columns=['Subcategory', 'Count'])
    secondary_analysis.to_csv(config['statistics']['subcategory'], index=False)

    print("Categorization finished, total activities count: ", activities_count)


if __name__ == "__main__":
    print("Reading regex file...")
    regex_def = pd.read_csv(config["regex-file"], delimiter=' CUSTOM-DELIMITER ', engine='python')

    print("Reading data from dataframe...")
    df = pd.read_csv(config["input-data"]["file-path"], delimiter=' CUSTOM-DELIMITER ', engine='python')

    identify(df, regex_def)
