"""
BL_CalciumAnalysis - Napari ROI Drawer Widget

This module defines a reproducible Napari widget using magicgui to:
1. Load a calcium imaging movie from a structured project using config.json
2. Compute the max Z-projection (projection over time)
3. Display both the full movie and projection
4. Enable manual ROI drawing using napari's shape layer
5. Save ROI polygon coordinates as JSON in the /processed folder

Author: Your Name
"""

import numpy as np
import napari
from magicgui import magicgui
import json
from pathlib import Path
from skimage.io import imread
from qtpy.QtWidgets import QPushButton
import matplotlib.pyplot as plt

# Create viewer instance and attach widgets
viewer = napari.Viewer()

# Store state for config and current paths
widget_state = {
    "config": None,
    "project_root": None,
    "selected_group": None,
    "current_recording_index": 0
}

def select_group(group_name: str):
    print(f"[DEBUG] Group selected: {group_name}")
    widget_state["selected_group"] = group_name

    if widget_state["config"] is None:
        print("[DEBUG] No config loaded yet.")
        return

    groups = widget_state["config"]["groups"]
    group_info = next((g for g in groups if g["group_name"] == group_name), None)

    if not group_info:
        print(f"[DEBUG] Group '{group_name}' not found in config.")
        return

    recordings = group_info.get("recordings", [])
    print(f"[DEBUG] Number of recordings in '{group_name}': {len(recordings)}")
    print(f"[DEBUG] Recording names: {[r['recording_name'] for r in recordings]}")

    if recordings:
        first_recording = recordings[0]
        print(f"[DEBUG] Path to first recording: {first_recording['path']}")

group_selector = magicgui(
    select_group,
    call_button="Select Group"
)

@magicgui(call_button="Load Project Config")
def load_config_widget(config_path: Path = None):
    """
    Load the config.json file which defines the structure of the calcium imaging project.

    Parameters
    ----------
    config_path : Path
        Path to the config.json file at the root of the project folder.
    """
    if not config_path or not config_path.is_file():
        print("Please select a valid config.json file.")
        return

    with open(config_path, 'r') as f:
        config = json.load(f)

    widget_state["config"] = config
    widget_state["project_root"] = Path(config["project_root"])

    groups = [g["group_name"] for g in config["groups"]]
    group_selector.group_name.choices = groups
    group_selector.group_name.value = groups[0]

    print(f"[DEBUG] Loaded config from: {config_path}")
    print(f"Number of groups: {len(groups)}")
    print(f"Group names: {', '.join(groups)}")

    widget_state["selected_group"] = groups[0]

@magicgui(call_button="Generate Max Projection")
def generate_max_projection():
    global viewer
    if widget_state["config"] is None:
        print("[DEBUG] Config not loaded.")
        return

    selected_group = widget_state.get("selected_group")
    if not selected_group:
        print("[DEBUG] No group selected.")
        return

    groups = widget_state["config"]["groups"]
    group_info = next((g for g in groups if g["group_name"] == selected_group), None)
    if not group_info or not group_info.get("recordings"):
        print("[DEBUG] No recordings found for selected group.")
        return

    recording_index = widget_state["current_recording_index"]
    print(f"[DEBUG] Current recording index: {recording_index}")
    recording = group_info["recordings"][recording_index]
    print(f"[DEBUG] Recording name: {recording['recording_name']}")
    recording_path = Path(recording["path"])
    raw_dir = recording_path / "raw"
    processed_dir = recording_path / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    files = list(raw_dir.glob("*.tif")) + list(raw_dir.glob("*.npy"))
    if not files:
        print("[DEBUG] No .tif or .npy movie found in raw/")
        return

    movie_path = files[0]
    print(f"[DEBUG] Loading movie from: {movie_path}")
    if movie_path.suffix == ".npy":
        movie = np.load(movie_path)
    else:
        movie = imread(movie_path)

    print(f"[DEBUG] Finished loading movie: {movie_path.name}")
    print(f"[DEBUG] Movie shape: {movie.shape} (expecting 3D: T, H, W)")
    if movie.ndim != 3:
        print("[DEBUG] Movie must be 3D (time, height, width).")
        return

    max_proj = np.max(movie, axis=0)
    print(f"[DEBUG] Max projection shape: {max_proj.shape} (should be 2D)")
    save_path = processed_dir / "max_projection.npy"
    np.save(save_path, max_proj)
    print(f"[DEBUG] Max projection saved to: {save_path}")

    viewer.layers.clear()
    viewer.add_image(movie, name='Calcium Movie')
    viewer.add_image(max_proj, name='Max Projection')
    
    roi_layer = viewer.add_shapes(
        name="ROIs",
        shape_type="polygon",
        edge_color="yellow",
        face_color="transparent",
        properties={"label": np.array([], dtype=int)},
        text={"text": "{label}", "size": 14, "color": "white", "anchor": "center"},
        visible=True
    )
    
    # Track next label manually
    next_label = [1]  # use a mutable object to persist in closure

    def update_current_label(*args):
        roi_layer.current_properties = {"label": np.array([next_label[0]])}
        print(f"[DEBUG] Pre-assigning label {next_label[0]} for next ROI")

    def label_new_roi(event):
        try:
            n_shapes = len(roi_layer.data)
            if "label" not in roi_layer.properties:
                current_labels = np.array([], dtype=int)
            else:
                current_labels = roi_layer.properties["label"]

            print(f"[DEBUG] ROI data count: {n_shapes}")
            print(f"[DEBUG] Current labels: {current_labels.tolist()}")

            updated = False
            new_labels = current_labels.copy()

            # Check for duplicates or zero-labels
            needs_relabel = (
                len(current_labels) < n_shapes or
                len(set(current_labels)) != len(current_labels) or
                any(label == 0 for label in current_labels)
            )

            if needs_relabel:
                new_labels = np.arange(1, n_shapes + 1, dtype=int)
                updated = True
                for i, label in enumerate(new_labels):
                    print(f"[DEBUG] Assigned label {label} to ROI index {i}")

            if updated:
                roi_layer.properties["label"] = new_labels
                roi_layer.features = {"label": new_labels}
                next_label[0] = len(new_labels) + 1  # update next label
                print(f"[DEBUG] Updated labels: {new_labels.tolist()}")
            else:
                print("[DEBUG] No updates needed for labels.")

        except Exception as e:
            print(f"[DEBUG] ROI label assignment error: {e}")

    roi_layer.mode = "add_polygon_lasso"
    roi_layer.current_properties = {"label": np.array([1])}
    roi_layer.events.data.connect(label_new_roi)
    roi_layer.events.mode.connect(update_current_label)

    print("[DEBUG] ROI drawing layer with dynamic labeling initialized.")

@magicgui(call_button="Next Recording")
def recording_navigator():
    group_name = widget_state["selected_group"]
    if group_name is None:
        print("[DEBUG] No group selected.")
        return
    group_info = next((g for g in widget_state["config"]["groups"] if g["group_name"] == group_name), None)
    recordings = group_info["recordings"]
    current = widget_state["current_recording_index"]
    if current + 1 >= len(recordings):
        print("[DEBUG] Already at last recording.")
        return
    widget_state["current_recording_index"] += 1
    print(f"[DEBUG] Moving to recording index {widget_state['current_recording_index']}")
    print(f"[DEBUG] Now working on recording: {recordings[widget_state['current_recording_index']]['recording_name']}")
    generate_max_projection()

@magicgui(call_button="Save ROIs & Plot Traces")
def save_rois_and_plot():
    try:
        roi_layer = viewer.layers["ROIs"]
        movie_layer = viewer.layers["Calcium Movie"]

        shapes = roi_layer.data
        labels = roi_layer.properties["label"].tolist()
        print(f"[DEBUG] Saving {len(shapes)} ROIs with labels: {labels}")

        recording_index = widget_state["current_recording_index"]
        selected_group = widget_state["selected_group"]
        group_info = next((g for g in widget_state["config"]["groups"] if g["group_name"] == selected_group), None)
        recording = group_info["recordings"][recording_index]
        processed_dir = Path(recording["path"]) / "processed"
        processed_dir.mkdir(exist_ok=True)

        figures_dir = Path(recording["path"]) / "figures"
        figures_dir.mkdir(exist_ok=True)

        roi_json_path = processed_dir / "rois.json"
        roi_data = [{"label": int(label), "vertices": shape.tolist()} for label, shape in zip(labels, shapes)]
        with open(roi_json_path, "w") as f:
            json.dump(roi_data, f, indent=4)
        print(f"[DEBUG] ROIs saved to: {roi_json_path}")

        # Extract calcium traces
        movie = movie_layer.data  # shape (T, H, W)
        n_frames = movie.shape[0]
        traces = []

        for i, poly in enumerate(shapes):
            mask = np.zeros(movie.shape[1:], dtype=bool)
            rr, cc = np.round(poly[:, 0]).astype(int), np.round(poly[:, 1]).astype(int)
            rr = np.clip(rr, 0, mask.shape[0]-1)
            cc = np.clip(cc, 0, mask.shape[1]-1)
            mask[rr, cc] = True

            trace = movie[:, mask].mean(axis=1)
            traces.append(trace)
            print(f"[DEBUG] Extracted trace for ROI {labels[i]} with shape {trace.shape}")

        # Save calcium traces data
        traces_array = np.stack(traces)  # shape (num_rois, num_frames)
        trace_npy_path = processed_dir / "calcium_traces.npy"
        np.save(trace_npy_path, traces_array)
        print(f"[DEBUG] Traces saved to: {trace_npy_path}")

        # Also save as CSV for easier inspection
        trace_csv_path = processed_dir / "calcium_traces.csv"
        with open(trace_csv_path, "w") as f:
            header = ["frame"] + [f"roi_{label}" for label in labels]
            f.write(",".join(header) + "\n")
            for frame_idx in range(traces_array.shape[1]):
                row = [str(frame_idx)] + [f"{traces_array[roi_idx, frame_idx]:.4f}" for roi_idx in range(traces_array.shape[0])]
                f.write(",".join(row) + "\n")
        print(f"[DEBUG] Traces CSV saved to: {trace_csv_path}")

        fig, ax = plt.subplots()
        for i, trace in enumerate(traces):
            ax.plot(trace, label=f"ROI {labels[i]}")
        ax.set_title("Calcium Signal Traces")
        ax.set_xlabel("Frame")
        ax.set_ylabel("Mean Intensity")
        ax.legend()

        trace_fig_path = figures_dir / "calcium_traces.png"
        fig.savefig(trace_fig_path)
        print(f"[DEBUG] Trace figure saved to: {trace_fig_path}")

        viewer.window.add_dock_widget(fig.canvas, name="Calcium Traces", area="bottom")
        print("[DEBUG] Calcium traces plotted in napari.")

    except Exception as e:
        print(f"[DEBUG] Error saving ROIs or plotting traces: {e}")

viewer.window.add_dock_widget(load_config_widget, area='right')
viewer.window.add_dock_widget(group_selector, area='right')
viewer.window.add_dock_widget(generate_max_projection, area='right')
viewer.window.add_dock_widget(recording_navigator, area='right')

print("[DEBUG] Creating 'Save ROIs & Plot Traces' widget...")
viewer.window.add_dock_widget(save_rois_and_plot, area='right')
print("[DEBUG] 'Save ROIs & Plot Traces' widget added to Napari.")

# Run napari event loop
napari.run()