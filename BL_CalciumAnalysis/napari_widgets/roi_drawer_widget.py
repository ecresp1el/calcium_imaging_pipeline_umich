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

    recording = group_info["recordings"][0]
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
    roi_layer.mode = "add_polygon_lasso"

    def label_new_roi(event):
        try:
            n_shapes = len(roi_layer.data)
            current_labels = roi_layer.properties["label"]

            print(f"[DEBUG] ROI data count: {n_shapes}")
            print(f"[DEBUG] ROI label count: {len(current_labels)}")
            print(f"[DEBUG] Existing labels before update: {current_labels.tolist()}")

            # Check if label count matches but last label is still 0 (placeholder)
            if len(current_labels) == n_shapes and current_labels[-1] == 0:
                new_label = max(current_labels) + 1
                current_labels[-1] = new_label
                roi_layer.properties["label"] = current_labels
                print(f"[DEBUG] Replaced placeholder label with: {new_label}")

            elif len(current_labels) < n_shapes:
                next_label = max(current_labels.tolist() + [0]) + 1
                updated_labels = np.append(current_labels, next_label)
                roi_layer.properties["label"] = updated_labels
                print(f"[DEBUG] Added new ROI label: {next_label}")

            else:
                print("[DEBUG] Shape added, but label count already matches and is valid.")

            print(f"[DEBUG] Updated labels: {roi_layer.properties['label'].tolist()}")

        except Exception as e:
            print(f"[DEBUG] ROI label assignment error: {e}")

    roi_layer.events.data.connect(label_new_roi)
    print("[DEBUG] ROI drawing layer with dynamic labeling initialized.")

    widget_state["current_recording_index"] = 0  # or set manually per selector later

viewer.window.add_dock_widget(load_config_widget, area='right')
viewer.window.add_dock_widget(group_selector, area='right')
viewer.window.add_dock_widget(generate_max_projection, area='right')

# Run napari event loop
napari.run()