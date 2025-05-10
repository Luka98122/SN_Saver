import os
import zipfile
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import io
import shutil
import threading


SOURCE_FOLDER = r"C:\\Program Files (x86)\Steam\steamapps\\common\Subnautica\SNAppData"
BACKUP_DIR = Path(os.getenv('LOCALAPPDATA')) / "SNBACKUP"
COUNT_FILE = BACKUP_DIR / "count.txt"
THUMB_SIZE = (100, 60)
import json

OPTIONS_FILE = BACKUP_DIR / "options.json"
selected_row = None
selected_zip_path = None

def zip_folder(source_folder, zip_path):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(source_folder):
            for file in files:
                filepath = os.path.join(root, file)
                arcname = os.path.relpath(filepath, source_folder)
                zipf.write(filepath, arcname)

def ensure_backup_dir_and_count():
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    if not COUNT_FILE.exists():
        with open(COUNT_FILE, "w") as f:
            f.write("0")

def read_count():
    with open(COUNT_FILE, "r") as f:
        return int(f.read().strip())

def write_count(count):
    with open(COUNT_FILE, "w") as f:
        f.write(str(count))

def create_backup():
    ensure_backup_dir_and_count()
    if not os.path.exists(SOURCE_FOLDER):
        messagebox.showerror("Error", f"Source folder not found:\n{SOURCE_FOLDER} (SN is probably not installed)")
        return
    count = read_count()
    zip_filename = BACKUP_DIR / f"SNAppData{count}.zip"
    zip_folder(SOURCE_FOLDER, zip_filename)
    write_count(count + 1)
    update_table()

def get_zip_saves():
    data = []
    all_slots = set()
    zip_files = sorted(
        BACKUP_DIR.glob("SNAppData*.zip"),
        key=lambda f: int(''.join(filter(str.isdigit, f.stem)))
    )
    for file in zip_files:
        entry = {
            "name": file.name,
            "path": file,
            "timestamp": datetime.fromtimestamp(file.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            "saveslots": {}
        }
        try:
            with zipfile.ZipFile(file, 'r') as zf:
                for item in zf.namelist():
                    if item.startswith("SavedGames/slot") and item.endswith("screenshot.jpg"):
                        slot_name = item.split("/")[1]
                        all_slots.add(slot_name)
                        entry["saveslots"][slot_name] = zf.read(item)
        except Exception as e:
            print(f"Error reading {file.name}: {e}")
        data.append(entry)
    return data, sorted(all_slots)

def on_row_click(row_widgets, zip_path):
    global selected_row, selected_zip_path
    if selected_row:
        for widget in selected_row:
            widget.config(bg="SystemButtonFace")
    for widget in row_widgets:
        widget.config(bg="lightblue")
    selected_row = row_widgets
    selected_zip_path = zip_path

auto_backup_enabled = False
auto_backup_thread = None
auto_backup_interval = 5  # default to 5 minutes

def load_backup():
    if not selected_zip_path:
        messagebox.showwarning("No Selection", "Please select a save to load.")
        return
    confirm = messagebox.askyesno("Confirm Load", f"Are you sure you want to load:\n{selected_zip_path.name}?\nThis will overwrite your current save.")
    if not confirm:
        return
    try:
        if os.path.exists(SOURCE_FOLDER):
            shutil.rmtree(SOURCE_FOLDER)
        with zipfile.ZipFile(selected_zip_path, 'r') as zipf:
            zipf.extractall(SOURCE_FOLDER)
        messagebox.showinfo("Success", f"Backup {selected_zip_path.name} loaded!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load backup:\n{e}")

def load_options():
    if OPTIONS_FILE.exists():
        try:
            with open(OPTIONS_FILE, "r") as f:
                options = json.load(f)
                return options
        except Exception as e:
            print(f"Error loading options: {e}")
    return {"auto_backup_enabled": False, "auto_backup_interval": 5}

def save_options():
    options = {
        "auto_backup_enabled": auto_backup_var.get(),
        "auto_backup_interval": auto_backup_interval
    }
    try:
        with open(OPTIONS_FILE, "w") as f:
            json.dump(options, f)
    except Exception as e:
        print(f"Error saving options: {e}")

def auto_backup_loop():
    while auto_backup_enabled:
        create_backup()
        for _ in range(auto_backup_interval * 60):
            if not auto_backup_enabled:
                return
            root.after(1000, lambda: None) 
            time.sleep(1)



def toggle_auto_backup():
    global auto_backup_enabled, auto_backup_thread, auto_backup_interval
    auto_backup_enabled = auto_backup_var.get()
    if auto_backup_enabled:
        try:
            minutes = int(auto_backup_entry.get())
            if not 1 <= minutes <= 60:
                raise ValueError()
            auto_backup_interval = minutes
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number between 1 and 60.")
            auto_backup_var.set(False)
            return

        auto_backup_thread = threading.Thread(target=auto_backup_loop, daemon=True)
        auto_backup_thread.start()
    else:
        auto_backup_enabled = False
    save_options()  # Save the updated options

def update_table():
    for widget in table_frame.winfo_children():
        widget.destroy()

    saves, all_slots = get_zip_saves()

    # Header row
    tk.Label(table_frame, text="Save File", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky="w")
    tk.Label(table_frame, text="Last Modified", font=("Arial", 10, "bold")).grid(row=0, column=1, padx=5, pady=5, sticky="w")
    for col_idx, slot_name in enumerate(all_slots):
        tk.Label(table_frame, text=slot_name, font=("Arial", 10, "bold")).grid(row=0, column=col_idx + 2, padx=5, pady=5)

    for row_idx, save in enumerate(saves, start=1):
        row_widgets = []

        lbl_name = tk.Label(table_frame, text=save["name"], anchor="w", width=25)
        lbl_name.grid(row=row_idx, column=0, padx=5, pady=5, sticky="w")
        row_widgets.append(lbl_name)

        lbl_time = tk.Label(table_frame, text=save["timestamp"], anchor="w")
        lbl_time.grid(row=row_idx, column=1, padx=5, pady=5, sticky="w")
        row_widgets.append(lbl_time)

        for col_idx, slot_name in enumerate(all_slots):
            slot_data = save["saveslots"].get(slot_name)
            if slot_data:
                try:
                    img = Image.open(io.BytesIO(slot_data))
                    img.thumbnail(THUMB_SIZE)
                    img_tk = ImageTk.PhotoImage(img)
                    img_label = tk.Label(table_frame, image=img_tk)
                    img_label.image = img_tk
                    img_label.grid(row=row_idx, column=col_idx + 2, padx=5, pady=5)
                    row_widgets.append(img_label)
                except:
                    err_label = tk.Label(table_frame, text="[Img Err]")
                    err_label.grid(row=row_idx, column=col_idx + 2)
                    row_widgets.append(err_label)
            else:
                none_label = tk.Label(table_frame, text="[No Img]")
                none_label.grid(row=row_idx, column=col_idx + 2)
                row_widgets.append(none_label)

        # Bind row click
        for widget in row_widgets:
            widget.bind("<Button-1>", lambda e, w=row_widgets, p=save["path"]: on_row_click(w, p))

# GUI Setup
import time  # Needed for time.sleep()
root = tk.Tk()
root.title("Subnautica Save Viewer")

def on_close():
    save_options()
    root.quit()

root.protocol("WM_DELETE_WINDOW", on_close)

main_frame = tk.Frame(root, padx=10, pady=10)
main_frame.pack(fill=tk.BOTH, expand=True)

bottom_frame = tk.Frame(main_frame)
bottom_frame.pack(fill=tk.X, pady=(10, 0))

auto_backup_var = tk.BooleanVar()
auto_backup_check = tk.Checkbutton(bottom_frame, text="Auto Backup", variable=auto_backup_var, command=toggle_auto_backup)
auto_backup_check.pack(side=tk.LEFT)



tk.Label(bottom_frame, text="Interval (min):").pack(side=tk.LEFT, padx=(10, 2))
auto_backup_entry = tk.Entry(bottom_frame, width=5)
auto_backup_entry.insert(0, "5")
auto_backup_entry.pack(side=tk.LEFT)


options = load_options()


auto_backup_var.set(options["auto_backup_enabled"])
auto_backup_interval = options["auto_backup_interval"]
auto_backup_entry.delete(0, tk.END)
auto_backup_entry.insert(0, str(auto_backup_interval))

top_buttons = tk.Frame(main_frame)
top_buttons.pack(fill=tk.X, pady=(0, 10))

btn_backup = tk.Button(top_buttons, text="Create Backup", command=create_backup)
btn_backup.pack(side=tk.LEFT, padx=(0, 10))

btn_load = tk.Button(top_buttons, text="Load Backup", command=load_backup)
btn_load.pack(side=tk.LEFT)

# Scrollable canvas for table
canvas = tk.Canvas(main_frame)
scroll_y = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
scroll_x = tk.Scrollbar(main_frame, orient="horizontal", command=canvas.xview)
canvas.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

table_frame = tk.Frame(canvas)
canvas.create_window((0, 0), window=table_frame, anchor='nw')

def on_mousewheel(event):
    if event.delta:  # Windows & macOS
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    else:  # Linux (event.num is used instead of delta)
        if event.num == 4:
            canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            canvas.yview_scroll(1, "units")

# Windows & macOS
canvas.bind_all("<MouseWheel>", on_mousewheel)

# Linux (uses Button-4 and Button-5)
canvas.bind_all("<Button-4>", on_mousewheel)
canvas.bind_all("<Button-5>", on_mousewheel)


def on_configure(event):
    canvas.configure(scrollregion=canvas.bbox('all'))

table_frame.bind("<Configure>", on_configure)

# Initial setup
ensure_backup_dir_and_count()
if (options["auto_backup_enabled"]):
    create_backup()
update_table()

root.mainloop()
