import pandas as pd

if __name__ == "__main__":
    print("Reading regex file...")
    regex_def = pd.read_csv('regex.csv', delimiter=' CUSTOM-DELIMITER ', engine='python')
    regex_def.to_csv('regex_formatted.csv')

