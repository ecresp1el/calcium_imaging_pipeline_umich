
#Biolumi Calcium Imaging Analysis


# 📁 Project: mannyproject

Welcome to the **mannyproject** calcium imaging data repository. This folder contains a fully structured organization of raw data, metadata, processed results, analysis outputs, and figures, grouped by experimental condition and individual recording sessions.

This layout is designed to be consistent, easy to navigate, and friendly for both manual exploration and automated data processing.

---

## 🗂️ Folder Structure Overview
mannyproject/
├── control/
│   ├── recording_001/
│   │   ├── raw/
│   │   ├── metadata/
│   │   ├── processed/
│   │   ├── analysis/
│   │   ├── figures/
│   │   └── README.md
│   ├── recording_002/
│   │   └── … (same structure)
│   └── README.md
├── stimulated/
│   └── … (same structure as control)
├── config.json
└── README.md  ← (this file)

---

## 📌 Project-Level Contents

- `config.json`: Contains a structured summary of all experimental groups and recordings.
- `README.md`: You're reading it! Describes the structure and how to use this project.

---

## 📁 Group Folders (`control/`, `stimulated/`, etc.)

Each group folder represents a different **experimental condition** (e.g., Control, Drug Treated, Stimulated). Inside each are folders for every individual **recording session**.

Inside the group folder:
- `recording_001/`, `recording_002/`, etc.: One folder per data collection session.
- `README.md`: A group-level description you can edit to track metadata or observations.

---

## 📂 Recording Session Folders

Each recording folder has this structure:

| Folder       | Description                                                                 |
|--------------|-----------------------------------------------------------------------------|
| `raw/`       | Original data files (e.g. TIFFs, CSVs, videos)                              |
| `metadata/`  | Text or spreadsheet files describing the session (date, subject ID, notes)  |
| `processed/` | Cleaned or transformed data (e.g. ROI traces, motion corrected images)      |
| `analysis/`  | Results of data analysis (e.g. ΔF/F traces, statistical outputs)            |
| `figures/`   | Visualizations generated from analysis (plots, images, reports)             |
| `README.md`  | Auto-generated placeholder file for notes about the recording               |

---

## 🧠 How to Use

1. **Add raw data** into the `raw/` folder of each recording.
2. **Add metadata** files manually into `metadata/`.
3. **Processed outputs** and **analysis results** from your pipeline should be saved in their respective folders.
4. Use the `README.md` files to jot down notes, parameters, or manual observations.

---

## 🧰 Notes

- This structure was generated using an automated Python script to ensure consistency.
- You can modify folder names or add additional subfolders as needed for your workflow.
- The `config.json` file can be used by other scripts to automatically access and process your data.

---

Let us know if you modify the structure so downstream tools can be updated accordingly!