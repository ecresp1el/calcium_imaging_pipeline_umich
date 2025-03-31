import os
import json
import tkinter as tk
from tkinter import filedialog

# 🛠️ Helper function to get user input with a default option
def get_user_input(prompt, default=None):
    """Prompt the user for input with an optional default value."""
    response = input(f"{prompt} [{default}]: ") or default
    return response

# 🏗️ Function to create a structured project directory
def create_directory_structure(project_root, group_info):
    """Creates a standardized directory structure for calcium imaging projects."""
    
    # Ensure the project root directory exists
    os.makedirs(project_root, exist_ok=True)

    project_config = {
        "project_root": project_root,
        "groups": []
    }

    for group_name, recordings_per_group in group_info.items():
        group_path = os.path.join(project_root, group_name)
        os.makedirs(group_path, exist_ok=True)

        group_data = {"group_name": group_name, "path": group_path, "recordings": []}

        for r in range(1, recordings_per_group + 1):
            recording_name = f"recording_{r:03d}"
            recording_path = os.path.join(group_path, recording_name)
            os.makedirs(recording_path, exist_ok=True)

            subdirs = ["raw", "metadata", "processed", "analysis", "figures"]
            for sub in subdirs:
                os.makedirs(os.path.join(recording_path, sub), exist_ok=True)

            with open(os.path.join(recording_path, "README.md"), "w") as readme:
                readme.write(f"# {recording_name}\n\nThis folder contains data for {recording_name}.")

            group_data["recordings"].append({"recording_name": recording_name, "path": recording_path})

        with open(os.path.join(group_path, "README.md"), "w") as readme:
            readme.write(f"# {group_name}\n\nThis folder contains multiple recording sessions.")

        project_config["groups"].append(group_data)

    with open(os.path.join(project_root, "README.md"), "w") as readme:
        readme.write(f"# {os.path.basename(project_root)}\n\nThis is a structured directory for calcium imaging data.")

    config_path = os.path.join(project_root, "config.json")
    with open(config_path, "w") as json_file:
        json.dump(project_config, json_file, indent=4)

    print(f"✅ Project structure created at: {project_root}")
    print(f"🔧 Configuration saved in: {config_path}")

# 🎯 Main function to prompt user input and create the directory
def main():
    print("🔹 Welcome to the Project Setup Script 🔹")

    # First ask for the project folder name
    project_name = get_user_input("Enter project directory name", "biolumi_project")

    # Then ask user to select base directory via file dialog
    root = tk.Tk()
    root.withdraw()  # Hide main window
    base_path = filedialog.askdirectory(title=f"Select base directory to create project folder '{project_name}'")
    if not base_path:
        print("❌ No folder selected. Exiting.")
        return

    project_root = os.path.join(base_path, project_name)
    config_path = os.path.join(project_root, "config.json")

    # Check if project is already initialized
    if os.path.exists(config_path):
        print(f"⚠️ A project already exists at {project_root}.")
        overwrite = get_user_input("Do you want to overwrite the existing project structure? (yes/no)", "no")
        if overwrite.lower() != "yes":
            print("🔁 Keeping existing project. Exiting without changes.")
            return

    # Gather structure details from user
    num_groups = int(get_user_input("How many groups?", "2"))

    group_info = {}
    for i in range(1, num_groups + 1):
        group_name = get_user_input(f"Enter name for group {i}", f"group_{i:03d}")
        recordings_per_group = int(get_user_input(f"How many recordings for {group_name}?", "2"))
        group_info[group_name] = recordings_per_group

    # Create structure
    create_directory_structure(project_root, group_info)

# 🚀 Run the script when executed
if __name__ == "__main__":
    main()