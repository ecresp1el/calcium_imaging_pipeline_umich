"""
BL_CalciumAnalysis - Group and Recording Level Analysis Module

This module defines classes and methods for programmatic, reproducible analysis of calcium imaging data.
It uses the `config.json` structure to derive project paths, loads calcium trace data from CSV files,
and provides utilities to visualize and summarize calcium dynamics at both the single-recording and group level.

Author: Emmanuel Luis Crespo
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from typing import List, Optional


class CalciumRecordingAnalysis:
    """
    Represents a single recording session for calcium imaging analysis.

    Responsible for loading and plotting calcium traces from the recording's trace CSV file.
    """

    def __init__(self, recording_path: Path):
        """
        Initialize the analysis object with a path to a specific recording.

        Parameters
        ----------
        recording_path : Path
            Full path to the recording directory containing the processed/ folder.
        """
        self.recording_path = recording_path
        self.traces_csv_path = recording_path / "processed" / "calcium_traces.csv"
        self.trace_df: Optional[pd.DataFrame] = None

    def load_trace_data(self):
        """
        Load calcium trace data from the recording's CSV file.

        The CSV should contain a 'frame' column and one column per ROI (e.g., roi_1, roi_2, ...).
        """
        if not self.traces_csv_path.exists():
            raise FileNotFoundError(f"Trace CSV not found: {self.traces_csv_path}")
        self.trace_df = pd.read_csv(self.traces_csv_path)
        print(f"[DEBUG] Loaded trace data from: {self.traces_csv_path}")

    def plot_all_traces(self, save_path: Optional[Path] = None):
        """
        Plot all ROI traces from the recording.

        Parameters
        ----------
        save_path : Path, optional
            If provided, save the plot to this path. Otherwise, show interactively.
        """
        if self.trace_df is None:
            self.load_trace_data()

        plt.figure(figsize=(12, 5))
        for col in self.trace_df.columns:
            if col != "frame":
                plt.plot(self.trace_df["frame"], self.trace_df[col], label=col)
        plt.xlabel("Frame")
        plt.ylabel("Mean Intensity")
        plt.title(f"Calcium Traces - {self.recording_path.name}")
        plt.legend()
        plt.tight_layout()

        if save_path:
            save_path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path)
            print(f"[DEBUG] Saved trace plot to: {save_path}")
        else:
            plt.show()


class CalciumGroupAnalysis:
    """
    Performs group-level analysis across multiple recordings defined in a config.json file.

    Loads individual recordings via `CalciumRecordingAnalysis` and summarizes trends across the group.
    """

    def __init__(self, config_path: Path, group_name: str):
        """
        Initialize the group-level analyzer using the project config file.

        Parameters
        ----------
        config_path : Path
            Path to the config.json file that defines the project.
        group_name : str
            Name of the group to analyze (must match one defined in config).
        """
        with open(config_path, "r") as f:
            config = json.load(f)

        self.group_info = next((g for g in config["groups"] if g["group_name"] == group_name), None)
        if self.group_info is None:
            raise ValueError(f"Group '{group_name}' not found in config.")

        self.recording_paths = [Path(r["path"]) for r in self.group_info["recordings"]]
        self.recording_analyses = [CalciumRecordingAnalysis(p) for p in self.recording_paths]
        self.group_name = group_name

    def compute_mean_trace_across_recordings(self) -> pd.DataFrame:
        """
        Compute the mean ROI trace (averaged across ROIs) for each recording in the group.

        Returns
        -------
        pd.DataFrame
            DataFrame where each column is a recording, and each row is the mean ROI intensity per frame.
        """
        summary = {}
        for analysis in self.recording_analyses:
            try:
                analysis.load_trace_data()
                df = analysis.trace_df.copy()
                mean_trace = df.drop(columns=["frame"]).mean(axis=1)
                summary[analysis.recording_path.name] = mean_trace
            except Exception as e:
                print(f"[WARNING] Skipping {analysis.recording_path.name}: {e}")

        return pd.DataFrame(summary)

    def plot_group_summary(self, save_path: Optional[Path] = None):
        """
        Plot mean traces of all recordings in the group.

        Parameters
        ----------
        save_path : Path, optional
            If provided, saves the figure to this path. Otherwise, shows it interactively.
        """
        summary_df = self.compute_mean_trace_across_recordings()

        plt.figure(figsize=(10, 6))
        for recording_name in summary_df.columns:
            plt.plot(summary_df.index, summary_df[recording_name], label=recording_name)

        plt.xlabel("Frame")
        plt.ylabel("Mean Intensity")
        plt.title(f"Group Summary - {self.group_name}")
        plt.legend()
        plt.tight_layout()

        if save_path:
            save_path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path)
            print(f"[DEBUG] Saved group summary to: {save_path}")
        else:
            plt.show()
