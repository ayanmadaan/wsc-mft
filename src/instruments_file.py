import json
import pandas as pd

# Create the DataFrame from the given data
df = pd.read_csv('Instruments.csv')

# Create a dictionary with tradingsymbol as key and instrument_token as value
output_dict = dict(zip(df['tradingsymbol'], df['instrument_token']))

# Write the dictionary to a JSON file
output_file_path = "D:/Finance/WSC/quant22/Flowus/final_infra/src/instruments.json"
with open(output_file_path, 'w') as file:
    json.dump(output_dict, file)

output_file_path
