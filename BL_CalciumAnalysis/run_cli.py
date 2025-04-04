"""
run_cli.py

This script allows you to interact with a calcium imaging analysis pipeline from the command line.
You can inspect a project (by printing its metadata/config) and optionally run image processing
(max projection generation) across all sessions in the project.

Usage:
    python run_cli.py /path/to/project_folder --process_max_projections
"""

# Import the project manager class from cli.py
import sys 
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

#combine both imports into one line
from cli import ProjectDataManager, SessionImageProcessor
from scripts.helpers import summarize_project_structure

def main():
    import argparse  # argparse is a built-in Python library for parsing command-line arguments

    # Set up the command-line interface
    parser = argparse.ArgumentParser(description="Inspect or process a calcium imaging project.")
    
    # Required argument: the path to the project folder (must contain a config.json file)
    parser.add_argument("project_path", help="Path to the project folder (must contain config.json)")
    
    # Optional flag: if used, it will trigger the processing of max projections
    parser.add_argument("--process_max_projections", action="store_true",
                        help="Run max projection processing on all sessions")
    
    # Parse the command-line arguments into an `args` object
    args = parser.parse_args()

    # Load the project using the provided path
    project = ProjectDataManager(args.project_path)
    project.show()  # Print project details to the terminal

    # If the user passed the --process_max_projections flag, run image processing
    if args.process_max_projections:
        processor = SessionImageProcessor(project)

        # NEW: Run TIFF dimension analysis
        print("Running TIFF dimension analysis...")
        processor.add_tiff_dimensions()
        print(project.directory_df[['session_id', 'x_dim', 'y_dim', 'z_dim_frames']])

        results = processor.analyze_all_sessions()
        
        # Display the results of the analysis
        print("\n🔍 Max Projection Processing Results:")
        for sid, outcome in results.items():
            print(f"Session {sid}: {outcome}")

# Entry point for the script
if __name__ == "__main__":
    main()