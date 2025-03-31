from cli import ProjectDataManager
from image_analysis_processor import SessionImageProcessor  # assumes you saved the new class in this file

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Inspect or process a calcium imaging project.")
    parser.add_argument("project_path", help="Path to the project folder (must contain config.json)")
    parser.add_argument("--process_max_projections", action="store_true",
                        help="Run max projection processing on all sessions")
    args = parser.parse_args()

    # Load the project
    project = ProjectDataManager(args.project_path)
    project.show()

    # Optional: Run image analysis
    if args.process_max_projections:
        processor = SessionImageProcessor(project)
        results = processor.analyze_all_sessions()
        print("\n🔍 Max Projection Processing Results:")
        for sid, outcome in results.items():
            print(f"Session {sid}: {outcome}")

if __name__ == "__main__":
    main()