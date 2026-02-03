import os
import json
import pandas as pd
import pdb
stop = pdb.set_trace

def importDatasets(directory: str = "data"):
    """ Import all datasets from the given directory

    Args:
        directory (str, optional): Directory containing the datasets. Defaults to "/data".
    """
    # List to store individual DataFrames
    dataframes = []
    # Iterate over all files in the directory
    for filename in os.listdir(directory):
        if filename.startswith("instances-test-set-") and filename.endswith(".db"):
            file_path = os.path.join(directory, filename)
            
            # Extract participant ID from filename
            participant_id = filename.split('-')[-1].replace('.db', '')
            
            # Read the NeDB file
            with open(file_path, 'r') as file:
                data = [json.loads(line) for line in file]
            
            # Convert list of dictionaries to DataFrame
            df = pd.DataFrame(data)
            
            # Add a column for participant ID
            df['participant_id'] = participant_id

            # Place the participant_id column at the beginning
            cols = df.columns.tolist()
            cols = cols[-1:] + cols[:-1]

            # Reorder the columns
            df = df[cols]

            # Append to the list of DataFrames
            dataframes.append(df)

    merged = pd.concat(dataframes, ignore_index=True)
    merged.drop(columns=['_id', "datasetName", "Square or park confidence"], inplace=True)
    return merged


def importInteractions(directory: str = "data"):
    """ Import all datasets from the given directory

    Args:
        directory (str, optional): Directory containing the datasets. Defaults to "/data".
    """
    # List to store individual DataFrames
    dataframes = []
    # Iterate over all files in the directory
    for filename in os.listdir(directory):
        if filename.startswith("user-interaction-") and filename.endswith(".db"):
            file_path = os.path.join(directory, filename)
            
            # Extract participant ID from filename
            participant_id = filename.split('-')[-1].replace('.db', '')
            
            # Read the NeDB file
            with open(file_path, 'r') as file:
                data = [json.loads(line) for line in file]
            
            # Convert list of dictionaries to DataFrame
            df = pd.DataFrame(data)
            
            # Add a column for participant ID
            df['participant_id'] = participant_id

            # Place the participant_id column at the beginning
            cols = df.columns.tolist()
            cols = cols[-1:] + cols[:-1]

            # Reorder the columns
            df = df[cols]

            # Append to the list of DataFrames
            dataframes.append(df)

    merged = pd.concat(dataframes, ignore_index=True)
    return merged