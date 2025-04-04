"""
Test Script: Recording-Level Analysis

This script prompts the user to select a config.json file,
then loads the first recording in the first group listed and runs analysis.

Author: Emmanuel Luis Crespo
"""

import json
import sys
from pathlib import Path
import argparse
from tqdm import tqdm

# Ensure the BL_CalciumAnalysis package is discoverable
repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))

from tkinter import Tk, filedialog
from BL_CalciumAnalysis.analysis.group_recording_analysis import CalciumRecordingAnalysis

# === Step 1: Prompt user to select config file ===
print("[TEST] Please select your config.json file...")

root = Tk()
root.withdraw()  # Hide the root Tk window
config_path = filedialog.askopenfilename(title="Select config.json", filetypes=[("JSON files", "*.json")])
root.update()
root.destroy()  # Close the Tk instance after file selection

if not config_path:
    raise ValueError("No config.json selected.")

config_path = Path(config_path)
print(f"[TEST] Loaded config from: {config_path}")

# === Step 2: Load config and get first recording path ===
with open(config_path, "r") as f:
    config_data = json.load(f)

parser = argparse.ArgumentParser(description="Test recording-level calcium imaging analysis.")
parser.add_argument("--all", action="store_true", help="Run analysis for all groups and recordings in the config.")
args = parser.parse_args()

if not args.all:
    # === Run single recording (default) ===
    first_group = config_data["groups"][0]
    first_recording = first_group["recordings"][0]
    recording_path = Path(first_recording["path"])
    group_name = first_group["group_name"]

    print(f"[TEST] Running analysis on: {recording_path.name} (Group: {group_name})")
    analysis = CalciumRecordingAnalysis(recording_path)

    print("[TEST] Plotting and saving raw traces...")
    raw_plot_path = recording_path / "figures" / f"{group_name}_{recording_path.name}_raw_traces.png"
    analysis.plot_all_traces(save_path=raw_plot_path)
    print(f"[TEST] Saved raw trace plot to: {raw_plot_path}")

    sem_plot_path = recording_path / "figures" / f"{group_name}_{recording_path.name}_mean_sem.png"
    analysis.analyze_and_plot_mean_sem(save_path=sem_plot_path)
    print(f"[TEST] Saved SEM plot to: {sem_plot_path}")

    print("[TEST] Computing and plotting ΔF/F...")
    analysis.compute_and_plot_delta_f(group_name=group_name)
    print("[TEST] Plotting ΔF/F subset (first 10 frames)...")
    analysis.plot_delta_f_subset(group_name=group_name)
    print("[TEST ✅] Recording-level test complete.")

else:
    # === Run full group-level analysis ===
    print("[TEST] Running full analysis on all groups and recordings...")
    for group in tqdm(config_data["groups"], desc="Groups"):
        group_name = group["group_name"]
        print(f"[DEBUG] Processing group: {group_name}")
        for recording in tqdm(group["recordings"], desc=f"Recordings ({group_name})", leave=False):
            recording_path = Path(recording["path"])
            print(f"[DEBUG]  → Recording: {recording_path.name}")
            analysis = CalciumRecordingAnalysis(recording_path)

            raw_plot_path = recording_path / "figures" / f"{group_name}_{recording_path.name}_raw_traces.png"
            analysis.plot_all_traces(save_path=raw_plot_path)
            print(f"[DEBUG]     Saved raw trace plot to: {raw_plot_path}")

            sem_plot_path = recording_path / "figures" / f"{group_name}_{recording_path.name}_mean_sem.png"
            analysis.analyze_and_plot_mean_sem(save_path=sem_plot_path)
            print(f"[DEBUG]     Saved SEM plot to: {sem_plot_path}")

            analysis.compute_and_plot_delta_f(group_name=group_name)
            analysis.plot_delta_f_subset(group_name=group_name)
            print(f"[DEBUG]     Saved ΔF/F subset plots for: {recording_path.name}")
            print(f"[DEBUG]     Completed ΔF/F analysis for: {recording_path.name}")
    print("[TEST ✅] Full group and recording-level analysis complete.")

