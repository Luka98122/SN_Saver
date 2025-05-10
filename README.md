# Subnautica Save Backup & Viewer

A Python GUI tool for backing up and managing (Steam installed) Subnautica save data.  
Features include one-click backups, automatic backup scheduling, visual save inspection, and easy restore from ZIP.

## Features

- 📦 **Create Backups**  
  Saves the contents of `SNAppData` to `%LOCALAPPDATA%\SNBACKUP\SNAppDataX.zip`  
  🔄 **Backs up all save slots**

- 💾 **View Saved Backups**  
  Displays thumbnails for each backup ZIP.

- 📷 **Visual Slot Inspection**  
  Shows `screenshot.jpg` from each save slot inside the ZIP, organized in a clean table.

- 🔁 **Load Backup**  
  **1.** Exit to main menu.  
  **2.** Click a zip file or thumbnail, and restore it to the `SNAppData` by clicking **Load Save**.

- ⏱️ **Auto Backup Mode**  
  Automatically create backups every N minutes (configurable from 1–60).  
  ⚠️ **Note:** You must **save in-game** for the save to be backed up.


- 🧠 **Confirmation Dialogs**  
  Prevent accidental overwrites with confirmation prompts.

---

## Installation

### ✅ Easy Installation — EXE File

[📥 Download SN_Saver.exe](https://github.com/Luka98122/SN_Saver/releases/download/tested/main.exe)  
Then double-click to run the app.
> ⚠️ You may need to allow the file through Windows Defender or SmartScreen.

### 💻 Advanced — From Source

1. Install dependencies:

```bash
pip install pillow
```

2. Run the script
```bash
python main.py
```