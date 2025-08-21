import os
import re
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from datetime import datetime

class FootageRenamer:
    def __init__(self, root):
        self.root = root
        self.root.title("Footage Renamer")
        self.root.geometry("650x500")
        self.root.resizable(True, True)

        # Set dark theme
        self.style = ttk.Style()
        self.style.configure("TLabel", font=(".AppleSystemUIFont", 10))
        self.style.configure("TButton", font=(".AppleSystemUIFont", 10, "bold"))
        self.style.configure("Header.TLabel", font=(".AppleSystemUIFont", 12, "bold"))

        # Variables
        self.folder_path = tk.StringVar()
        self.camera_roll_var = tk.StringVar(value="J001")
        self.clip_prefix_var = tk.StringVar(value="Clip")
        self.date_var = tk.StringVar(value=datetime.now().strftime("%y%m%d"))
        self.files = []
        self.preview_data = []

        # Create UI
        self.create_widgets()

    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Folder selection
        folder_frame = ttk.LabelFrame(main_frame, text="Folder Selection", padding="10")
        folder_frame.pack(fill=tk.X, pady=10)

        ttk.Entry(folder_frame, textvariable=self.folder_path, width=50).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(folder_frame, text="Browse", command=self.browse_folder).pack(side=tk.RIGHT, padx=5)

        # Naming Options
        options_frame = ttk.LabelFrame(main_frame, text="Netflix Default Naming Options", padding="10")
        options_frame.pack(fill=tk.X, pady=10)

        ttk.Label(options_frame, text="Camera Roll:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(options_frame, textvariable=self.camera_roll_var, width=10).grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(options_frame, text="Clip Prefix:").grid(row=0, column=2, sticky=tk.W, pady=2)
        ttk.Entry(options_frame, textvariable=self.clip_prefix_var, width=10).grid(row=0, column=3, padx=5, pady=2)

        ttk.Label(options_frame, text="Date (YYMMDD):").grid(row=0, column=4, sticky=tk.W, pady=2)
        ttk.Entry(options_frame, textvariable=self.date_var, width=10).grid(row=0, column=5, padx=5, pady=2)

        # Action buttons
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=10)

        ttk.Button(action_frame, text="Preview", command=self.preview_renaming).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Rename Files", command=self.rename_files).pack(side=tk.RIGHT, padx=5)

        # Preview table
        preview_frame = ttk.LabelFrame(main_frame, text="Preview", padding="10")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        columns = ("original", "new")
        self.preview_tree = ttk.Treeview(preview_frame, columns=columns, show="headings", height=10)
        self.preview_tree.heading("original", text="Original Name")
        self.preview_tree.heading("new", text="New Name")
        self.preview_tree.column("original", width=250, anchor=tk.W)
        self.preview_tree.column("new", width=250, anchor=tk.W)
        self.preview_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.preview_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.preview_tree.configure(yscrollcommand=scrollbar.set)



    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path.set(folder_selected)
            self.load_files()

    def load_files(self):
        folder = self.folder_path.get()
        if not folder:
            return

        try:
            self.files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
            messagebox.showinfo("Success", f"Loaded {len(self.files)} files")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load files: {str(e)}")

    def extract_numbers(self, filename):
        # Extract all numbers from filename
        numbers = re.findall(r'\d+', filename)
        return '_'.join(numbers) if numbers else ""

    def generate_new_name(self, filename, index):
        name, ext = os.path.splitext(filename)

        camera_roll = self.camera_roll_var.get()
        clip_prefix = self.clip_prefix_var.get()
        date = self.date_var.get()

        # Extract numbers from original filename
        numbers = self.extract_numbers(filename)
        if numbers:
            clip_name = f"{clip_prefix}{numbers}"
        else:
            clip_name = f"{clip_prefix}{index:03d}"

        return f"{camera_roll}_{clip_name}_{date}{ext}"

    def preview_renaming(self):
        if not self.files:
            messagebox.showwarning("Warning", "No files loaded. Please select a folder first.")
            return

        # Clear previous preview
        for item in self.preview_tree.get_children():
            self.preview_tree.delete(item)

        self.preview_data = []

        for i, filename in enumerate(self.files, 1):
            new_name = self.generate_new_name(filename, i)
            self.preview_data.append((filename, new_name))
            self.preview_tree.insert("", tk.END, values=(filename, new_name))

    def rename_files(self):
        if not self.preview_data:
            messagebox.showwarning("Warning", "No preview available. Please generate a preview first.")
            return

        folder = self.folder_path.get()
        success_count = 0
        error_count = 0
        errors = []

        for original, new_name in self.preview_data:
            original_path = os.path.join(folder, original)
            new_path = os.path.join(folder, new_name)

            try:
                # Check if new name already exists
                if os.path.exists(new_path):
                    # Add a suffix to make it unique
                    name, ext = os.path.splitext(new_name)
                    unique_suffix = 1
                    while os.path.exists(os.path.join(folder, f"{name}_{unique_suffix}{ext}")):
                        unique_suffix += 1
                    new_path = os.path.join(folder, f"{name}_{unique_suffix}{ext}")

                os.rename(original_path, new_path)
                success_count += 1
            except Exception as e:
                error_count += 1
                errors.append(f"Failed to rename '{original}' to '{new_name}': {str(e)}")

        # Show results
        result_msg = f"Renaming completed. {success_count} files successfully renamed, {error_count} errors."
        if errors:
            result_msg += "\n\nErrors:\n" + "\n".join(errors)
            messagebox.showerror("Rename Results", result_msg)
        else:
            messagebox.showinfo("Rename Results", result_msg)

        # Refresh file list
        self.load_files()
        self.preview_renaming()

if __name__ == "__main__":
    root = tk.Tk()
    app = FootageRenamer(root)
    root.mainloop()