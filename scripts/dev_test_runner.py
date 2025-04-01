# scripts/dev_test_runner.py

# 🧭 Make sure the project root is in the Python path so we can import modules like 'cli' and 'image_analysis_processor'
import sys
import os

# Append the parent directory of this script to sys.path so Python can find your project modules
# This lets us run this script from *any* directory without module import errors
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import classes from the main analysis package
from BL_CalciumAnalysis.cli import ProjectDataManager, SessionImageProcessor

# 🗂️ Accept the project path from the command line
# This lets you reuse this script for different projects without editing the code each time
# Example usage:
#   python scripts/dev_test_runner.py ~/Desktop/calcium_imaging_projectfolder
# If no path is passed, it falls back to a placeholder
PROJECT_PATH = sys.argv[1] if len(sys.argv) > 1 else "/path/to/your/project"

print(f"\n🔍 Loading project from: {PROJECT_PATH}")

# Load the project metadata and directory structure
project = ProjectDataManager(PROJECT_PATH)
project.show()  # Show basic project info and session structure

# Create a processor object to run analyses on this project
processor = SessionImageProcessor(project)

# 📐 Step 1: Extract dimensions (x, y, z) from available TIFF files
print("\n📐 Running TIFF dimension analysis:")
processor.add_tiff_dimensions()

# Display the new columns with TIFF metadata
print(project.directory_df[['session_id', 'x_dim', 'y_dim', 'z_dim_frames']])

# 🖼️ Step 2: Run a test max projection on session 1 to confirm processing works
print("\n🖼️ Running max projection for session 1:")
result = processor.analyze_session_max_projection(1)
print(f"Result: {result}")