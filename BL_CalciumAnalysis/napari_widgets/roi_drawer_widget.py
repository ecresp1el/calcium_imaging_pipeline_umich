"""
BL_CalciumAnalysis - Napari ROI Drawer Widget

This module defines a reproducible Napari widget using magicgui to:
1. Load a calcium imaging movie (e.g. TIFF or NPY file)
2. Compute the max Z-projection (projection over time)
3. Display both the full movie and projection
4. Enable manual ROI drawing using napari's shape layer
5. Save ROI polygon coordinates as JSON

This is meant to be launched programmatically (e.g. via CLI or script), and may later be modularized into a napari plugin.

Author: Your Name
"""

import numpy as np
import napari
from magicgui import magicgui
from tifffile import imread
import json
from pathlib import Path


@magicgui(call_button="Load Calcium Movie")
def load_movie_widget(file_path=Path()):
    """
    Load a calcium imaging movie and automatically compute the max Z-projection.

    Parameters
    ----------
    file_path : Path
        Path to the calcium imaging TIFF or NPY stack.
    """
    # Load movie based on extension
    if file_path.suffix.lower() == ".tif" or file_path.suffix.lower() == ".tiff":
        movie = imread(file_path)
    elif file_path.suffix.lower() == ".npy":
        movie = np.load(file_path)
    else:
        print(f"Unsupported file type: {file_path.suffix}")
        return

    if movie.ndim != 3:
        print("Movie must be a 3D array (time, height, width).")
        return

    # Clear any existing layers
    viewer.layers.clear()

    # Add raw calcium movie
    viewer.add_image(movie, name='Calcium Movie', colormap='gray', contrast_limits='auto')

    # Compute and add max Z-projection
    max_proj = np.max(movie, axis=0)
    viewer.add_image(max_proj, name='Max Projection', colormap='magma', contrast_limits='auto')

    # Add shapes layer for ROIs
    viewer.add_shapes(
        name='ROIs',
        shape_type='polygon',
        edge_color='yellow',
        face_color='transparent'
    )


@magicgui(call_button="Save ROIs")
def save_rois_widget(layer: napari.layers.Shapes, save_path=Path("rois.json")):
    """
    Save manually drawn ROIs from the shapes layer into a JSON file.

    Parameters
    ----------
    layer : napari.layers.Shapes
        The shapes layer containing user-drawn ROIs.
    save_path : Path
        Output path for saving the ROI coordinates as JSON.
    """
    if not layer.data:
        print("No ROIs to save.")
        return

    roi_data = [roi.tolist() for roi in layer.data]

    with open(save_path, 'w') as f:
        json.dump(roi_data, f)

    print(f"Saved {len(roi_data)} ROIs to {save_path}")


# Create viewer instance and attach widgets
viewer = napari.Viewer()
viewer.window.add_dock_widget(load_movie_widget, area='right')
viewer.window.add_dock_widget(save_rois_widget, area='right')

# Run napari event loop
napari.run()
