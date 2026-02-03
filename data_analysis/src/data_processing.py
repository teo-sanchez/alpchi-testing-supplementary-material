import os
import json
import pandas as pd
from typing import NewType, List
import pdb
from datetime import datetime
import numpy as np
stop = pdb.set_trace

class DataLoader:
    def __init__(self, participants=None):
        self.participants = participants or [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
        self.pid_offset = -2
        self.classes = ["Agricultural area", "Forest", "Industrial or commercial area", "Public square or park", "Railway", "Residential area", "Road", "Waterbody"]

    def import_all_data(self) -> dict:
        results = {}
        results["training_set"] = self.import_training_set()
        results["test_sets"] = self.import_test_sets()
        results["baseline_test_sets"] = self.import_baseline_test_sets()
        results["user_interactions"] = self.import_user_interactions()
        results["questionnaire"] = self.import_questionnaire_answers_sosci()
        return results
    
    def import_training_set(self, directory: str = "../data/training_set") -> pd.DataFrame:
        filepath = os.path.join(directory, "training-set.db")
        with open(filepath, 'r') as file:
            data = [json.loads(line) for line in file]
        return pd.DataFrame(data)

    def import_test_sets(self, directory: str = "../data/test_sets") -> pd.DataFrame:
        dataframes = []
        for filename in os.listdir(directory):
            if filename.startswith("instances-test-set-") and filename.endswith(".db"):
                file_path = os.path.join(directory, filename)
                # Extract participant ID from filename
                participant_id = int(filename.split('-')[-1].replace('.db', ''))
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
        merged = merged[merged["participant_id"].isin(self.participants)]
        # Convert Confidence of the predicted label (str XX%) in to int
        merged['Confidence of the predicted label (in %)'] = merged['Confidence of the predicted label'].str.replace('%', '').astype(int)
        # Convert createdAt from 2024-07-10T12:45:50.346Z to datetime
        merged['createdAt'] = df["createdAt"].apply(lambda x: datetime.fromisoformat(x).strftime('%Y-%m-%d %H:%M:%S.%f'))
        # Convert updatedAt from {'$$date': 1720691021643} to datetime
        merged['updatedAt'] = df['updatedAt'].apply(lambda x: datetime.fromtimestamp(x['$$date']/1000.0, tz=None).strftime('%Y-%m-%d %H:%M:%S.%f'))
        # Drop useless columns
        merged.drop(columns=['_id', "datasetName", "Confidence of the predicted label"], inplace=True)
        # Apply offset to the participant_id
        merged['participant_id'] = merged['participant_id'] + self.pid_offset
        return merged
    
    def import_baseline_test_sets(self, directory: str = "../data/baseline_test_sets") -> pd.DataFrame:
        dataframes = []
        # Iterate over all files in the directory
        for filename in os.listdir(directory):
            if filename.startswith("instances-test-set-") and filename.endswith(".db"):
                file_path = os.path.join(directory, filename)
                # Extract participant ID from filename
                participant_id = int(filename.split('-')[-1].replace('.db', ''))
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
        # Convert Confidence of the predicted label (str XX%) in to int
        merged['Confidence of the predicted label (in %)'] = merged['Confidence of the predicted label'].str.replace('%', '').astype(int)
        # Convert createdAt from 2024-07-10T12:45:50.346Z to datetime
        merged['createdAt'] = df["createdAt"].apply(lambda x: x['$$date'])
        # Convert updatedAt from {'$$date': 1720691021643} to datetime
        merged['updatedAt'] = df['updatedAt'].apply(lambda x: datetime.fromtimestamp(x['$$date']/1000.0, tz=None).strftime('%Y-%m-%d %H:%M:%S.%f'))
        # Drop useless columns
        merged["Pass/Fail"] = (merged["Label"] == merged["Predicted label"]).replace({True: "🔵 Pass", False: "❌ Fail"})
        merged.drop(columns=['_id', "datasetName", "Confidence of the predicted label"], inplace=True)
        return merged

    def import_user_interactions(self, directory: str = "../data/user_interactions") -> pd.DataFrame:
        # Your implementation with slight modifications for encapsulation.
        dataframes = []
        # Iterate over all files in the directory
        for filename in os.listdir(directory):
            if filename.startswith("user-interaction-") and filename.endswith(".db"):
                file_path = os.path.join(directory, filename)
                
                # Extract participant ID from filename
                participant_id = int(filename.split('-')[-1].replace('.db', ''))
                
                # Read the NeDB file
                with open(file_path, 'r') as file:
                    data = [json.loads(line) for line in file]
                
                # Convert list of dictionaries to DataFrame
                df = pd.DataFrame(data)

                # Normalize the timestamp (subtract the first timestamp)
                df['timestamp'] = df['timestamp'] - df['timestamp'].min()
                
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

        df = merged[["participant_id", "action", "timestamp"]]
        # For each participants: Get the last timestamp (most recent event) if the action "init" and substract it to all the timestamps of the participant
        # Take the first timestamp that is not zero (remove zeros in the timestamp column, then take the first)
        df = df[df["timestamp"] != 0]
        # Delete row where (df["participant_id"] == 7) & (df["action"] == "init") & (df["timestamp"] == df["timestamp"].min()
        df = df.drop(df[(df["participant_id"] == 7) & (df["action"] == "init") & (df["timestamp"] == df["timestamp"].min())].index)
        df = df.drop(df[(df["participant_id"] == 7) & (df["action"] == "init") & (df["timestamp"] == df["timestamp"].min())].index)

        last_inits = df[df["action"] == "init"].groupby("participant_id")["timestamp"].min().reset_index(name="Last init")
        
        df = pd.merge(df, last_inits, on="participant_id", how="left")
        merged["timestamp"] = (df["timestamp"] - df["Last init"]) / (1000*60) # Convert to seconds
            
        # Drop useless columns
        merged.drop(columns=['_id'], inplace=True)

        # Apply offset to the participant_id
        merged['participant_id'] = merged['participant_id'] + self.pid_offset
        return merged

    def code2meaning(self, data,
                variable_df,
                response_df,
                meaning_column_names: bool = True,
                meaning_values: bool = True):
        column_renaming_mapping = {}
        for var in data.columns:
            if var in variable_df['VAR'].values:
                # Replace column code with the corresponding meaning
                column_meaning = variable_df[variable_df["VAR"] == var]["LABEL"].values[0]
                column_renaming_mapping[var] = column_meaning
                # Value mapping
                if var in response_df["VAR"].values:
                    value_renaming_mapping : dict = {}
                    for _, row in response_df[response_df["VAR"] == var].iterrows():
                        value_renaming_mapping[row["RESPONSE"]] = row["MEANING"]
                    # Apply the mapping on the right column
                    if meaning_values:
                        data[var] = data[var].map(value_renaming_mapping, na_action='ignore')
        if meaning_column_names:
            data.rename(columns=column_renaming_mapping, inplace=True)                    
        return data
    
    def get_mental_model_score(self, row: pd.Series) -> int:
        score= 0
        if row['Most challenging classes: Road'] == "Checked":
            score+=1
        if row['Most challenging classes: Public square or park'] == "Checked":
            score+=1
        if row['Most challenging classes: Forest'] == "Checked":
            score+=1
        if row['Easiest class: Waterbody'] == "Checked":
            score+=1
        if row['Easiest class: Residential area'] == "Checked":
            score+=1
        if row['Easiest class: Railway'] == "Checked":
            score+=1
        if row["Confident prediction"] == "Image 2":
            score+=1
        return score

    def get_expertise(self, row: pd.Series) -> int:
        score = 0
        raise NotImplementedError("Not implemented yet")

    # def get_questions(self, variables_filepath: str = "../data/questionnaire_answers/data_ML_Auditing_2024-08-27_13-26.csv") -> dict:
        

    def import_questionnaire_answers_sosci(self, data_filepath: str = "../data/questionnaire_answers/data_ML_Auditing_2025-01-06_19-11.csv", 
                                    variables_listing_filepath: str = "../data/questionnaire_answers/variables_ML_Auditing_2024-08-27_13-26.csv",
                                    response_listing_filepath: str = "../data/questionnaire_answers/values_ML_Auditing_2024-08-27_13-26.csv",
                                    change_column_names: bool = True,
                                    change_values: bool = True) -> pd.DataFrame:
        # Function to map coded responses to their meanings
        
        df = pd.read_csv(data_filepath, encoding="utf-16", delimiter='\t')
        # Remove row index 0 and shift the index
        df = df.drop(0).reset_index(drop=True)
        
        variables_listing = pd.read_csv(variables_listing_filepath, encoding="utf-16", delimiter='\t')
        response_listing = pd.read_csv(response_listing_filepath, encoding="utf-16", delimiter='\t')
        data_df = self.code2meaning(df, variables_listing, response_listing, change_column_names, change_values)

        if change_column_names:
            data_df["Participant ID: ID"] = df["Participant ID: ID"].astype(int)
            data_df = df[df["Participant ID: ID"].isin(self.participants)].copy()
            # Rename into "participant_id"
            data_df.rename(columns={"Participant ID: ID": "participant_id"}, inplace=True)
            # Convert "participant_id" to int64
            data_df["participant_id"] = data_df["participant_id"].astype(int)
            # Take the min of the participant and apply offset
            data_df["participant_id"] = data_df["participant_id"].apply(lambda x: x + self.pid_offset)
            # Place participant_id in first position of the data
            cols = data_df.columns.tolist()
            pid_index = cols.index("participant_id")
            cols = cols[pid_index:pid_index+1] + cols[:pid_index] + cols[pid_index+1:]
            data_df = data_df[cols]
        return data_df


class Metrics:
    def __init__(self, data: dict):
        self.data = data
    # * Number of test added
    def get_test_added_per_participant(self) -> pd.DataFrame:
        df = self.data["user_interactions"]
        return df[df["action"] == "add"].groupby("participant_id").size().reset_index(name='Total test cases added').astype(int)
    
    def get_number_of_fails_per_participant(self) -> pd.DataFrame:
        df = self.data["test_sets"]
        return df[df["Pass/Fail"] == "❌ Fail"].groupby("participant_id").size().reset_index(name='Number of fails uncovered').astype(int)
        
    
    # * Number of test deleted
    def get_test_deleted_per_participant(self) -> pd.DataFrame:
        df = self.data["user_interactions"]
        deletions = df[df["action"] == "remove"][["participant_id", "numberOfItemsAffected"]]
        deletions = deletions.groupby(by="participant_id").sum()
        return deletions.squeeze().reset_index(name="Total test cases deleted").astype(int)

    # * Number of test checked
    def get_checks_per_participant(self) -> pd.DataFrame:
        df = self.data["user_interactions"]
        return df[df["action"] == "check"].groupby("participant_id").size().reset_index(name='Total checks').astype(int)
    
    # * Ratio of test cases added / number of checks
    def get_ratio_checks_added_per_participant(self) -> pd.DataFrame:
        checks = self.get_checks_per_participant()
        added = self.get_test_added_per_participant()
        merged = pd.merge(added, checks, on="participant_id", how="outer").fillna(0)
        merged["Ratio checks/added"] = (merged["Total checks"] / merged["Total test cases added"]) * 100
        return merged[["participant_id", "Ratio checks/added"]]

    # * Final number of tests
    def get_final_number_of_tests_per_participant(self) -> pd.DataFrame:
        added = self.get_test_added_per_participant()
        deleted = self.get_test_deleted_per_participant()
        merged = pd.merge(added, deleted, on="participant_id", how="outer").fillna(0)
        merged["Total test cases"] = (merged["Total test cases added"] - merged["Total test cases deleted"]).astype(int)
        return merged[["participant_id", "Total test cases"]]
    
    #* Finale number of tests (baseline)
    def get_final_number_of_tests_per_participant_baseline(self) -> pd.DataFrame:
        df_test = self.data["baseline_test_sets"]
        total_tests = df_test.groupby("participant_id").size().reset_index(name="Total test cases")
        return total_tests
    
    # * Final number of tests per class
    def get_final_number_of_tests_per_class(self) -> pd.DataFrame:
        df_test = self.data["test_sets"]
        return df_test.groupby("Label").size().reset_index(name="Total test cases")

    # * Final number of tests per participant per class
    def get_final_number_of_tests_per_participant_per_class(self) -> pd.DataFrame:
        df_test = self.data["test_sets"].groupby(["participant_id", "Label"]).size().reset_index(name="Total test cases")
        df_test = df_test.pivot(index="Label", columns="participant_id", values="Total test cases").fillna(0).astype(int)
        return df_test
    
    # * Final number of tests per participant per class (baseline)
    def get_final_number_of_tests_per_participant_per_class_baseline(self) -> pd.DataFrame:
        df_test = self.data["baseline_test_sets"].groupby(["participant_id", "Label"]).size().reset_index(name="Total test cases")
        df_test = df_test.pivot(index="Label", columns="participant_id", values="Total test cases").fillna(0).astype(int)
        return df_test

    # * Fail count per participant per class
    def get_fail_count_per_participant_per_class(self) -> pd.DataFrame:
        df_test = self.data["test_sets"]
        failed = df_test[df_test["Pass/Fail"] == "❌ Fail"]
        return failed.groupby(["participant_id", "Label"])["Pass/Fail"].count().reset_index(name="Failed test cases")
    
    # * Fail count per class
    def get_fail_count_per_class(self) -> pd.DataFrame:
        df_test = self.data["test_sets"]
        failed = df_test[df_test["Pass/Fail"] == "❌ Fail"]
        return failed.groupby("Label").size().reset_index(name="Failed test cases")
    
    # * Fail ratio per participant
    def get_fail_ratio_per_participant(self) -> pd.DataFrame:
        df_test = self.data["test_sets"]
        
        # Count the number of fails per participant
        fail_count = df_test.groupby('participant_id')["Pass/Fail"].apply(lambda x: (x == '❌ Fail').sum()).reset_index(name="Fails")
        
        # Count the total number of test cases per participant
        test_count = df_test.groupby('participant_id').size().reset_index(name="Total tests")
        
        # Merge the counts
        merged = pd.merge(fail_count, test_count, on='participant_id')
        
        # Calculate fail ratio
        merged["Fail ratio"] = (merged["Fails"] / merged["Total tests"]) * 100
        
        return merged[["participant_id", "Fail ratio"]]
    
    # * Fail ratio per participant (baseline)
    def get_fail_ratio_per_participant_baseline(self) -> pd.DataFrame:
        df_test = self.data["baseline_test_sets"]
        
        # Count the number of fails per participant
        fail_count = df_test.groupby('participant_id')["Pass/Fail"].apply(lambda x: (x == '❌ Fail').sum()).reset_index(name="Fails")
        
        # Count the total number of test cases per participant
        test_count = df_test.groupby('participant_id').size().reset_index(name="Total tests")
        
        # Merge the counts
        merged = pd.merge(fail_count, test_count, on='participant_id')
        
        # Calculate fail ratio
        merged["Fail ratio"] = (merged["Fails"] / merged["Total tests"]) * 100
        
        return merged[["participant_id", "Fail ratio"]]
    
    def get_fail_count_per_participant(self) -> pd.DataFrame:
        df_test = self.data["test_sets"]
        return df_test[df_test["Pass/Fail"] == "❌ Fail"].groupby("participant_id").size().reset_index(name="Failed test cases")
    
    # * Fail ratio per class
    def get_fail_ratio_per_class(self) -> pd.DataFrame:
        test_count = self.get_final_number_of_tests_per_class()
        fail_count = self.get_fail_count_per_class()
        merged = pd.merge(test_count, fail_count, on="Label", how="outer").fillna(0)
        merged["Fail ratio"] = (merged["Failed test cases"] / merged["Total test cases"])
        merged.drop(columns=["Failed test cases", "Total test cases"], inplace=True)
        return merged

    # * Fail ratio per participant per class 
    def get_fail_ratio_per_class_per_participant(self) -> pd.DataFrame:
        fail_count = self.get_fail_count_per_participant_per_class()
        total_count = self.get_final_number_of_tests_per_participant_per_class()

        # Reshape total_count to have "participant_id" as a column
        total_count = total_count.reset_index().melt(
            id_vars=["Label"], 
            var_name="participant_id", 
            value_name="Total test cases"
        )

        # Merge the two DataFrames
        merged = pd.merge(fail_count, total_count, on=["participant_id", "Label"], how="outer").fillna(0)
        
        # Calculate the fail ratio
        merged["Fail ratio"] = merged["Failed test cases"] / merged["Total test cases"]

        # Drop unnecessary columns
        merged.drop(columns=["Failed test cases", "Total test cases"], inplace=True)
        
        # Pivot the DataFrame so that Labels are rows, participants are columns
        pivoted = merged.pivot(index="Label", columns="participant_id", values="Fail ratio").fillna(0)
        
        return pivoted
    
    # * Gini impurity per participant (from total number of test cases per class)
    def get_gini_impurity_per_participant(self) -> pd.DataFrame:
        """
        Computes the Gini impurity index for each participant based on the distribution
        of test cases per class.
        
        Returns:
            pd.DataFrame: A DataFrame with `participant_id` and `Gini impurity` columns.
        """
        # Get the final number of tests per participant per class
        data = self.get_final_number_of_tests_per_participant_per_class()
        
        # Normalize counts to proportions for each participant
        data = data.div(data.sum(axis=0), axis=1)
        
        # Define Gini impurity computation
        def compute_gini(x):
            if x.sum() > 0:
                return 1 - np.sum(x**2)
            return np.nan  # Handle columns with invalid data (e.g., all zeros)

        # Compute Gini impurity for each participant (column-wise)
        gini_index = data.apply(compute_gini, axis=0)
        
        # Convert to DataFrame
        gini_df = gini_index.reset_index()
        gini_df.columns = ["participant_id", "Gini impurity"]
        
        return gini_df
    
    # * Effort per participant per class
    def get_effort_per_participant_per_class(self) -> pd.DataFrame:
        test_sets = self.data["test_sets"]
    
        # Get unique participants and classes
        participants = test_sets["participant_id"].unique()
        classes = test_sets["Label"].unique()
        
        # Create a complete grid of participants and classes
        complete_grid = pd.DataFrame([(p, c) for p in participants for c in classes], 
                                    columns=["participant_id", "Label"])
        
        # Count tests per participant and class
        tests_per_class = test_sets.groupby(["participant_id", "Label"]).size().reset_index(name="Tests")
        
        # Merge the complete grid with tests_per_class (fills missing combinations with NaN)
        effort = complete_grid.merge(tests_per_class, on=["participant_id", "Label"], how="left").fillna(0)
        
        # Calculate total tests per participant
        total_tests_per_participant = effort.groupby("participant_id")["Tests"].sum().reset_index(name="Total tests")
        
        # Merge back to compute effort
        effort = effort.merge(total_tests_per_participant, on="participant_id")
        effort["Effort"] = effort["Tests"] / effort["Total tests"]
        
        # Handle cases where Total tests = 0 (avoid division by zero)
        effort.loc[effort["Total tests"] == 0, "Effort"] = 0

        return effort[["participant_id", "Label", "Effort"]]
    
    # * Efficiency per participant per class
    def get_efficiency_per_participant_per_class(self) -> pd.DataFrame:
        test_sets = self.data["test_sets"]
    
        # Get unique participants and classes
        participants = test_sets["participant_id"].unique()
        classes = test_sets["Label"].unique()
        
        # Create a complete grid of participants and classes
        complete_grid = pd.DataFrame([(p, c) for p in participants for c in classes], 
                                    columns=["participant_id", "Label"])
        
        # Count errors per participant and class
        errors_per_class = test_sets[test_sets["Pass/Fail"] == "❌ Fail"].groupby(["participant_id", "Label"]).size().reset_index(name="Errors")
        
        # Merge the complete grid with errors_per_class (fills missing combinations with NaN)
        efficiency = complete_grid.merge(errors_per_class, on=["participant_id", "Label"], how="left").fillna(0)
        
        # Total errors per participant
        total_errors_per_participant = efficiency.groupby("participant_id")["Errors"].sum().reset_index(name="Total Errors")
        
        # Merge back to compute efficiency
        efficiency = efficiency.merge(total_errors_per_participant, on="participant_id")
        efficiency["Efficiency"] = efficiency["Errors"] / efficiency["Total Errors"]
        
        # Handle cases where Total Errors = 0 (avoid division by zero)
        efficiency.loc[efficiency["Total Errors"] == 0, "Efficiency"] = 0

        return efficiency[["participant_id", "Label", "Efficiency"]]
    
    def get_reflection_time(self, threshold: float = 30,
                             selected_actions: List[str] = ["add", "check", ["drag", "zoom", "center", "randomize"]]) -> pd.DataFrame:
        df_ui = self.data["user_interactions"]
        reflexions = df_ui[df_ui["action"].isin(selected_actions)]
        # For each participant, sort by timestamp
        reflexions = reflexions.sort_values(by=["participant_id", "timestamp"], ascending=True)
        # Calculate the time difference between each action
        reflexions["time_diff"] = reflexions.groupby("participant_id")["timestamp"].diff()
        reflexions["start_time"] = reflexions["timestamp"] - reflexions["time_diff"]
        # Reflexion times (time_diff > 30 seconds)
        return reflexions[reflexions["time_diff"] > threshold/60][["participant_id", "start_time", "time_diff"]]