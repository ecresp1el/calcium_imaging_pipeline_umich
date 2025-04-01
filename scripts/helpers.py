def summarize_project_structure(project_manager):
    """
    Print a summary of the project structure: groups, number of recordings, and their names.

    Parameters:
    - project_manager (ProjectDataManager): The initialized project object.
    """
    df = project_manager.directory_df
    group_summary = df.groupby("group").size()

    print("\n📊 Project Summary")
    print(f"- Total groups: {len(group_summary)}")
    for group, count in group_summary.items():
        print(f"  - {group}: {count} recordings")
    print(f"- Total recordings: {len(df)}\n")