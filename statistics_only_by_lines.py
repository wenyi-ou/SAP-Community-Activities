import re
import yaml
import pandas as pd

with open("config.yaml", "r") as config_file:
    config = yaml.load(config_file, Loader=yaml.FullLoader)


def split_into_sentences(text):
    str_list = re.split('(-:::-)|(\\n)|(\\\)n|,|(\.)|(\!)|(\?)|(\;)|(\.{3,6})', text)
    filter(None, str_list)
    filter(lambda x: not x.isspace(), str_list)
    map(lambda x: x.strip(), str_list)
    return str_list


def identify(row, regex_file, dict, activities_count):
    contributions = row.split(' CUSTOM-DELIMITER ')
    filter(None, contributions)
    for contribution in contributions:
        blocks = split_into_sentences(str(contribution))
        for index_regex, row_regex in regex_file.iterrows():
            regex = row_regex[config["regex-file-columns"]["regex"]]
            for content_block in blocks:
                if not isinstance(str(content_block), str):
                    continue
                if re.search(regex, str(content_block), re.IGNORECASE):
                    cat_name = config["regex-file-columns"]["subcategory"]
                    if not row_regex[cat_name] in dict:
                        dict[row_regex[cat_name]] = 1
                    else:
                        dict[row_regex[cat_name]] += 1


if __name__ == "__main__":
    print("Reading regex file...")
    regex_def = pd.read_csv(config["regex-file"], delimiter=' CUSTOM-DELIMITER ', engine='python')
    my_dict = {}
    activities_count = 0

    print("Identification running...")
    f = open(config["input-data"]["file-path"])
    line = f.readline()
    while line:
        row = f.readline()
        identify(row, regex_def, my_dict, activities_count)
    f.close()

    print("Completed, total activities count: ", activities_count)
    with open(config['statistics']['statistics-only'], 'w') as csv_file:
        for category in my_dict.keys():
            csv_file.write("%s, %s\n" % (category, my_dict[category]))

