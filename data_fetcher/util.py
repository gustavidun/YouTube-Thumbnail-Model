import pandas as pd

from config import CHANNELS_PATH, OUTPUT_PATH, CSV_OUTPUT_PATH
from dataframe import filter_duration

def shuffle_channels(path):
    channels_df = pd.read_csv(path, sep = '\t')
    channels_df = channels_df.sample(frac=1).reset_index(drop=True)
    channels_df.to_csv(CHANNELS_PATH, sep = '\t')
    print("Channels shuffled.")

def add_column(pickle_file, csv_file, column_name, default_value):
    # Load the DataFrame from the pickle file
    df = pd.read_pickle(pickle_file)
    
    # Check if the row already exists
    if column_name in df.index:
        print(f"Row '{column_name}' already exists. No changes made.")
        return df

    # Add the row to the DataFrame
    df[column_name] = default_value

    # Save the updated DataFrame back to the pickle file
    df.to_pickle(pickle_file)
    df.to_csv(csv_file)
    
    print(f"Row '{column_name}' added successfully.")
    return df

if __name__ == "__main__":
    #shuffle_channels("data_fetcher/data/df_channels.tsv")
    #add_column(OUTPUT_PATH, CSV_OUTPUT_PATH, "duration", None)
    filter_duration()

