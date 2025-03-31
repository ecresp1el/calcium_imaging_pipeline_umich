import os
import json
import pandas as pd

class ProjectDataManager:
    """
    Loads and organizes a structured calcium imaging project based on the config.json file.

    Parameters:
    - project_folder (str): Path to the base project folder containing config.json
    """

    def __init__(self, project_folder):
        self.project_folder = project_folder
        self.config = self.load_config()
        self.directory_df = self.initialize_directory_df()

    def load_config(self):
        config_path = os.path.join(self.project_folder, "config.json")
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"No config.json found in {self.project_folder}")
        with open(config_path, "r") as f:
            return json.load(f)

    def initialize_directory_df(self):
        """Generate a flat DataFrame of all group and recording paths, including a session_id."""
        entries = []
        session_counter = 1
        for group in self.config['groups']:
            for rec in group['recordings']:
                entries.append({
                    "session_id": session_counter,
                    "group": group['group_name'],
                    "recording": rec['recording_name'],
                    "path": rec['path']
                })
                session_counter += 1Adds a new column session_id that starts at 1 and increments for every recording.
        return pd.DataFrame(entries)

    def show(self):
        """Print the dataframe of all recordings."""
        print(self.directory_df)