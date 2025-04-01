import os
import json
import pandas as pd
from PIL import Image
import numpy as np
from pathlib import Path

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
                session_counter += 1
        return pd.DataFrame(entries)

    def show(self):
        """Print the dataframe of all recordings."""
        print(self.directory_df)
    
    def is_valid_structure(self):
        """
        Checks whether the expected folder structure exists for all groups and recordings.
        Returns True if everything is in place, False otherwise.
        """
        try:
            # Load config
            for group in self.config["groups"]:
                if not os.path.isdir(group["path"]):
                    return False
                for recording in group["recordings"]:
                    rec_path = recording["path"]
                    required_subdirs = ["raw", "metadata", "processed", "analysis", "figures"]
                    if not os.path.isdir(rec_path):
                        return False
                    for sub in required_subdirs:
                        if not os.path.isdir(os.path.join(rec_path, sub)):
                            return False
            return True
        except Exception as e:
            print(f"Validation error: {e}")
            return False      
class SessionImageProcessor:
    """
    A processing class that interfaces with ProjectDataManager to apply image analysis functions
    to each session's raw data (specifically multi-frame TIFs located in the 'raw/' folder).
    """

    def __init__(self, project_data_manager):
        self.project = project_data_manager

    def get_session_raw_data(self, session_id):
        """
        Locate the first .tif file in the 'raw/' folder of the session.

        Parameters:
        session_id (int): Numerical session identifier.

        Returns:
        str or None: Path to the TIF file if found, else None.
        """
        session_row = self.project.directory_df[self.project.directory_df['session_id'] == session_id]
        if session_row.empty:
            print(f"No session found with ID {session_id}")
            return None

        group = session_row.iloc[0]['group']
        recording = session_row.iloc[0]['recording']
        raw_folder = os.path.join(self.project.project_folder, group, recording, 'raw')
        if not os.path.exists(raw_folder):
            print(f"Raw folder does not exist for session {session_id}")
            return None

        for file in os.listdir(raw_folder):
            if file.endswith('.tif') or file.endswith('.tiff'):
                return os.path.join(raw_folder, file)

        print(f"No TIF files found in session {session_id} raw folder")
        return None

    def max_projection_mean_values(self, tif_path):
        """
        Generates a mean projection from a multi-frame TIF and saves it.
        """
        with Image.open(tif_path) as img:
            sum_image = np.zeros((img.height, img.width), dtype=np.float32)

            for i in range(img.n_frames):
                img.seek(i)
                sum_image += np.array(img, dtype=np.float32)

            mean_image = sum_image / img.n_frames

        # Store result in session-level 'processed/' folder
        session_dir = os.path.dirname(os.path.dirname(tif_path))
        processed_dir = os.path.join(session_dir, 'processed')
        os.makedirs(processed_dir, exist_ok=True)

        # Clean up filename to avoid extra periods
        p = Path(tif_path)
        safe_name = p.stem.replace('.', '_')
        output_name = f"{safe_name}_max_projection.tif"
        max_proj_image_path = os.path.join(processed_dir, output_name)

        Image.fromarray(mean_image.astype(np.uint8)).save(max_proj_image_path)
        print(f"Max projection saved: {max_proj_image_path}")
        return max_proj_image_path

    def analyze_session_max_projection(self, session_id):
        tif_path = self.get_session_raw_data(session_id)
        if isinstance(tif_path, str) and tif_path.endswith('.tif'):
            session_dir = os.path.dirname(os.path.dirname(tif_path))
            processed_dir = os.path.join(session_dir, 'processed')
            p = Path(tif_path)
            safe_name = p.stem.replace('.', '_')
            max_proj_filename = f"{safe_name}_max_projection.tif"
            max_proj_path = os.path.join(processed_dir, max_proj_filename)

            if os.path.exists(max_proj_path):
                print(f"Max projection already exists for session {session_id}. Skipping.")
                return max_proj_path
            else:
                print(f"Processing max projection for session {session_id}...")
                return self.max_projection_mean_values(tif_path)
        else:
            return f"No valid TIF found for session {session_id}"

    def analyze_all_sessions(self):
        results = {}
        for session_id in self.project.directory_df['session_id']:
            try:
                results[session_id] = self.analyze_session_max_projection(session_id)
            except Exception as e:
                print(f"Error processing session {session_id}: {e}")
                results[session_id] = str(e)
        return results