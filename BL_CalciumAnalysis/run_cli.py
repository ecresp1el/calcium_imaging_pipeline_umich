from cli import ProjectDataManager

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Load and inspect a calcium imaging project.")
    parser.add_argument("project_path", help="Path to the project folder (must contain config.json)")
    args = parser.parse_args()

    project = ProjectDataManager(args.project_path)
    project.show()

if __name__ == "__main__":
    main()