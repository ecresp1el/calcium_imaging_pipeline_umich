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

    def analyze_and_plot_mean_sem(self, save_path: Optional[Path] = None):
        """
        Compute the mean and SEM across all ROIs at each frame, save the data and plot.

        Output:
        - analysis/mean_sem_summary.csv : stores 'frame', 'mean', and 'sem' for each frame.
        - figures/mean_sem_plot.png     : plot of mean ± SEM over time.
        """
        if self.trace_df is None:
            self.load_trace_data()

        df = self.trace_df.copy()
        frames = df["frame"]
        roi_values = df.drop(columns=["frame"])
        mean = roi_values.mean(axis=1)
        sem = roi_values.sem(axis=1)

        # Combine into summary DataFrame
        summary_df = pd.DataFrame({
            "frame": frames,
            "mean": mean,
            "sem": sem
        })

        # Save CSV
        analysis_dir = self.recording_path / "analysis"
        analysis_dir.mkdir(parents=True, exist_ok=True)
        csv_path = analysis_dir / "mean_sem_summary.csv"
        summary_df.to_csv(csv_path, index=False)
        print(f"[DEBUG] Saved mean/SEM data to: {csv_path}")

        # Plot and save figure
        if save_path:
            save_path.parent.mkdir(parents=True, exist_ok=True)
            fig_path = save_path
        else:
            fig_dir = self.recording_path / "figures"
            fig_dir.mkdir(parents=True, exist_ok=True)
            fig_path = fig_dir / "mean_sem_plot.png"

        plt.figure(figsize=(10, 5))
        plt.plot(frames, mean, label="Mean", color="blue")
        plt.fill_between(frames, mean - sem, mean + sem, alpha=0.3, color="blue", label="±SEM")
        plt.xlabel("Frame")
        plt.ylabel("Mean Intensity")
        plt.title(f"Mean ± SEM Calcium Trace - {self.recording_path.name}")
        plt.legend()
        plt.tight_layout()
        plt.savefig(fig_path)
        print(f"[DEBUG] Saved plot to: {fig_path}")
        plt.close()

    def compute_and_plot_delta_f(self, group_name: str):
        '''
        Compute and plot ΔF/F traces, excluding the first ROI (assumed background).

        This method:
        - Computes ΔF/F relative to the first frame for each ROI.
        - Plots individual traces with a bold mean trace.
        - Plots mean ± SEM with shaded error bars.
        - Saves plots and CSV summaries to the appropriate subfolders.
        '''
        if self.trace_df is None:
            self.load_trace_data()

        df = self.trace_df.copy()
        frames = df["frame"]
        roi_signals = df.drop(columns=["frame"])

        # Exclude the first ROI (assumed to be background)
        roi_signals = roi_signals.iloc[:, 1:]

        # Compute ΔF/F using first frame as F0
        f0 = roi_signals.iloc[0]
        delta_f = (roi_signals - f0) / f0

        # Save delta F/F data
        dff_df = pd.concat([frames, delta_f], axis=1)
        dff_csv_path = self.recording_path / "analysis" / "delta_f_traces.csv"
        dff_df.to_csv(dff_csv_path, index=False)
        print(f"[DEBUG] Saved ΔF/F data to: {dff_csv_path}")

        # Plot all traces with mean overlay
        plt.figure(figsize=(12, 5))
        for col in delta_f.columns:
            plt.plot(frames, delta_f[col], color="gray", alpha=0.3, linewidth=0.8)
        mean_trace = delta_f.mean(axis=1)
        plt.plot(frames, mean_trace, color="black", linewidth=2.0, label="Mean ΔF/F")
        plt.xlabel("Frame")
        plt.ylabel("ΔF/F")
        plt.title(f"ΔF/F Traces - {self.recording_path.name}")
        plt.legend()
        plt.tight_layout()
        trace_fig_path = self.recording_path / "figures" / f"{group_name}_{self.recording_path.name}_deltaF_traces.png"
        trace_fig_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(trace_fig_path)
        print(f"[DEBUG] Saved ΔF/F trace plot to: {trace_fig_path}")
        plt.close()

        # Compute mean and SEM for ΔF/F
        mean_dff = delta_f.mean(axis=1)
        sem_dff = delta_f.sem(axis=1)

        # Save summary
        dff_summary_df = pd.DataFrame({
            "frame": frames,
            "mean": mean_dff,
            "sem": sem_dff
        })
        dff_summary_csv_path = self.recording_path / "analysis" / "delta_f_summary.csv"
        dff_summary_df.to_csv(dff_summary_csv_path, index=False)
        print(f"[DEBUG] Saved ΔF/F mean/SEM summary to: {dff_summary_csv_path}")

        # Plot mean ± SEM
        plt.figure(figsize=(10, 5))
        plt.plot(frames, mean_dff, label="Mean ΔF/F", color="blue")
        plt.fill_between(frames, mean_dff - sem_dff, mean_dff + sem_dff, alpha=0.3, color="blue", label="±SEM")
        plt.xlabel("Frame")
        plt.ylabel("ΔF/F")
        plt.title(f"Mean ± SEM ΔF/F - {self.recording_path.name}")
        plt.legend()
        plt.tight_layout()
        sem_fig_path = self.recording_path / "figures" / f"{group_name}_{self.recording_path.name}_deltaF_mean_sem.png"
        plt.savefig(sem_fig_path)
        print(f"[DEBUG] Saved ΔF/F mean/SEM plot to: {sem_fig_path}")
        plt.close()

    def plot_delta_f_subset(self, group_name: str, n_frames: int = 15):
        """
        Plot ΔF/F traces and mean ± SEM for the first `n_frames` frames only.

        Parameters
        ----------
        group_name : str
            Name of the group for filename labeling.
        n_frames : int
            Number of frames to include in the plot (default is 10).
        """
        if self.trace_df is None:
            self.load_trace_data()

        df = self.trace_df.copy()
        frames = df["frame"]
        roi_signals = df.drop(columns=["frame"])

        # Exclude the first ROI (background)
        roi_signals = roi_signals.iloc[:, 1:]

        # Compute ΔF/F using first frame
        f0 = roi_signals.iloc[0]
        delta_f = (roi_signals - f0) / f0

        # Subset to first `n_frames`
        delta_f_subset = delta_f.iloc[:n_frames]
        frames_subset = frames.iloc[:n_frames]
        mean_subset = delta_f_subset.mean(axis=1)
        sem_subset = delta_f_subset.sem(axis=1)

        # Plot subset traces
        plt.figure(figsize=(10, 5))
        for col in delta_f_subset.columns:
            plt.plot(frames_subset, delta_f_subset[col], color="gray", alpha=0.3, linewidth=0.8)
        plt.plot(frames_subset, mean_subset, color="black", linewidth=2.0, label="Mean ΔF/F")
        plt.xlabel("Frame")
        plt.ylabel("ΔF/F")
        plt.title(f"ΔF/F Traces (first {n_frames} frames) - {self.recording_path.name}")
        plt.legend()
        plt.tight_layout()
        trace_fig = self.recording_path / "figures" / f"{group_name}_{self.recording_path.name}_deltaF_subset_traces.png"
        trace_fig.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(trace_fig)
        print(f"[DEBUG] Saved ΔF/F subset trace plot to: {trace_fig}")
        plt.close()

        # Plot mean ± SEM for subset
        plt.figure(figsize=(10, 5))
        plt.plot(frames_subset, mean_subset, label="Mean ΔF/F", color="blue")
        plt.fill_between(frames_subset, mean_subset - sem_subset, mean_subset + sem_subset, alpha=0.3, color="blue", label="±SEM")
        plt.xlabel("Frame")
        plt.ylabel("ΔF/F")
        plt.title(f"ΔF/F Mean ± SEM (first {n_frames} frames) - {self.recording_path.name}")
        plt.legend()
        plt.tight_layout()
        sem_fig = self.recording_path / "figures" / f"{group_name}_{self.recording_path.name}_deltaF_subset_mean_sem.png"
        plt.savefig(sem_fig)
        print(f"[DEBUG] Saved ΔF/F subset mean/SEM plot to: {sem_fig}")
        plt.close()


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
