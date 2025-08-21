import os
import re
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from datetime import datetime
from typing import List, Tuple, Optional, Union

class FootageRenamer:
    """A tool for batch renaming footage files according to Netflix recommended naming conventions."""
    
    def __init__(self, root: tk.Tk):
        """Initialize the FootageRenamer application with the main window."""
        self.root = root
        self.root.title("Footage Renamer")
        self.root.geometry("650x500")
        self.root.minsize(600, 450)
        self.root.resizable(True, True)
        
        # Center the window on the screen
        self._center_window()

        # Set up styling
        self._setup_styles()

        # Variables
        self.folder_path = tk.StringVar()
        self.camera_roll_var = tk.StringVar(value="J001")
        self.clip_prefix_var = tk.StringVar(value="Clip")
        self.date_var = tk.StringVar(value=datetime.now().strftime("%y%m%d"))
        
        # Data storage
        self.files: List[str] = []
        self.preview_data: List[Tuple[str, str]] = []

        # Create UI
        self._create_widgets()
    
    def _center_window(self) -> None:
        """Center the application window on the screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def _setup_styles(self) -> None:
        """Configure styles for UI elements."""
        self.style = ttk.Style()
        self.style.configure("TLabel", font=(".AppleSystemUIFont", 10))
        self.style.configure("TButton", font=(".AppleSystemUIFont", 10, "bold"))
        self.style.configure("Header.TLabel", font=(".AppleSystemUIFont", 12, "bold"))
        
    def _create_widgets(self) -> None:
        """Create and arrange all UI elements."""
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Folder selection section
        self._create_folder_selection(main_frame)

        # Naming options section
        self._create_naming_options(main_frame)

        # Action buttons section
        self._create_action_buttons(main_frame)

        # Preview table section
        self._create_preview_table(main_frame)
    
    def _create_folder_selection(self, parent: ttk.Frame) -> None:
        """Create the folder selection UI elements."""
        folder_frame = ttk.LabelFrame(parent, text="Folder Selection", padding="10")
        folder_frame.pack(fill=tk.X, pady=10)

        ttk.Entry(folder_frame, textvariable=self.folder_path, width=50).pack(
            side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        browse_btn = ttk.Button(folder_frame, text="Browse", command=self.browse_folder)
        browse_btn.pack(side=tk.RIGHT, padx=5)
        
        # Add tooltip
        self._create_tooltip(browse_btn, "Select the folder containing footage files to rename")
    
    def _create_naming_options(self, parent: ttk.Frame) -> None:
        """Create the naming options UI elements."""
        options_frame = ttk.LabelFrame(parent, text="Netflix Default Naming Options", padding="10")
        options_frame.pack(fill=tk.X, pady=10)

        # Grid layout for naming options
        ttk.Label(options_frame, text="Camera Roll:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(options_frame, textvariable=self.camera_roll_var, width=10).grid(
            row=0, column=1, padx=5, pady=2)

        ttk.Label(options_frame, text="Clip Prefix:").grid(row=0, column=2, sticky=tk.W, pady=2)
        ttk.Entry(options_frame, textvariable=self.clip_prefix_var, width=10).grid(
            row=0, column=3, padx=5, pady=2)

        ttk.Label(options_frame, text="Date (YYMMDD):").grid(row=0, column=4, sticky=tk.W, pady=2)
        ttk.Entry(options_frame, textvariable=self.date_var, width=10).grid(
            row=0, column=5, padx=5, pady=2)
    
    def _create_action_buttons(self, parent: ttk.Frame) -> None:
        """Create the action buttons UI elements."""
        action_frame = ttk.Frame(parent)
        action_frame.pack(fill=tk.X, pady=10)

        preview_btn = ttk.Button(action_frame, text="Preview", command=self.preview_renaming)
        preview_btn.pack(side=tk.LEFT, padx=5)
        
        rename_btn = ttk.Button(action_frame, text="Rename Files", command=self.rename_files)
        rename_btn.pack(side=tk.RIGHT, padx=5)
        
        # Add tooltips
        self._create_tooltip(preview_btn, "Preview how files will be renamed")
        self._create_tooltip(rename_btn, "Apply the renaming to all files")
    
    def _create_preview_table(self, parent: ttk.Frame) -> None:
        """Create the preview table UI elements."""
        preview_frame = ttk.LabelFrame(parent, text="Preview", padding="10")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        columns = ("original", "new")
        self.preview_tree = ttk.Treeview(preview_frame, columns=columns, show="headings", height=10)
        
        # Configure columns
        self.preview_tree.heading("original", text="Original Name")
        self.preview_tree.heading("new", text="New Name")
        self.preview_tree.column("original", width=250, anchor=tk.W)
        self.preview_tree.column("new", width=250, anchor=tk.W)
        
        # Pack with scrollbar
        self.preview_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.preview_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.preview_tree.configure(yscrollcommand=scrollbar.set)
    
    def _create_tooltip(self, widget: ttk.Widget, text: str) -> None:
        """Create a tooltip for a widget."""
        tooltip_window = None
        
        def enter(event) -> None:
            nonlocal tooltip_window
            x, y, _, _ = widget.bbox("insert")
            x += widget.winfo_rootx() + 25
            y += widget.winfo_rooty() + 25
            
            tooltip_window = tk.Toplevel(widget)
            tooltip_window.wm_overrideredirect(True)
            tooltip_window.wm_geometry(f"+{x}+{y}")
            
            label = ttk.Label(tooltip_window, text=text, background="#ffffe0", relief=tk.SOLID, borderwidth=1)
            label.pack(ipadx=5, ipady=2)
        
        def leave(event) -> None:
            nonlocal tooltip_window
            if tooltip_window:
                tooltip_window.destroy()
                tooltip_window = None
        
        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)
    
    def browse_folder(self) -> None:
        """Open a dialog to browse and select a folder."""
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path.set(folder_selected)
            self.load_files()
    
    def load_files(self) -> None:
        """Load files from the selected folder."""
        folder = self.folder_path.get()
        if not folder:
            return

        try:
            # Get all files in the directory (excluding subdirectories)
            self.files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
            messagebox.showinfo("Success", f"Loaded {len(self.files)} files")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load files: {str(e)}")
            self.files = []
    
    def extract_numbers(self, filename: str) -> str:
        """Extract all numbers from a filename and return them as a string.
        
        Args:
            filename: The filename to extract numbers from
        
        Returns:
            A string containing all extracted numbers joined by underscores
        """
        # Extract all numbers from filename using regex
        numbers = re.findall(r'\d+', filename)
        return '_'.join(numbers) if numbers else ""
    
    def generate_new_name(self, filename: str, index: int) -> str:
        """Generate a new filename according to the Netflix naming convention.
        
        Args:
            filename: The original filename
            index: The index of the file in the list (used if no numbers are found)
        
        Returns:
            The new filename in the format [cameraRoll]_[clipName]_[date]
        """
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
    
    def preview_renaming(self) -> None:
        """Generate a preview of how files will be renamed."""
        if not self.files:
            messagebox.showwarning("Warning", "No files loaded. Please select a folder first.")
            return

        # Clear previous preview
        for item in self.preview_tree.get_children():
            self.preview_tree.delete(item)

        self.preview_data = []

        # Generate new names and populate the preview table
        for i, filename in enumerate(self.files, 1):
            new_name = self.generate_new_name(filename, i)
            self.preview_data.append((filename, new_name))
            self.preview_tree.insert("", tk.END, values=(filename, new_name))
    
    def rename_files(self) -> None:
        """Rename files according to the generated preview."""
        if not self.preview_data:
            messagebox.showwarning("Warning", "No preview available. Please generate a preview first.")
            return

        folder = self.folder_path.get()
        if not folder:
            messagebox.showwarning("Warning", "No folder selected. Please select a folder first.")
            return

        success_count = 0
        error_count = 0
        errors: List[str] = []

        # Create a progress window
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Renaming Files")
        progress_window.geometry("300x100")
        progress_window.resizable(False, False)
        
        # Center progress window
        progress_window.update_idletasks()
        width = progress_window.winfo_width()
        height = progress_window.winfo_height()
        x = (progress_window.winfo_screenwidth() // 2) - (width // 2)
        y = (progress_window.winfo_screenheight() // 2) - (height // 2)
        progress_window.geometry(f"{width}x{height}+{x}+{y}")
        
        # Add progress bar
        progress_label = ttk.Label(progress_window, text="Renaming files...")
        progress_label.pack(pady=10)
        
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(progress_window, variable=progress_var, maximum=100)
        progress_bar.pack(padx=20, pady=5, fill=tk.X)
        
        # Make progress window modal
        progress_window.transient(self.root)
        progress_window.grab_set()
        self.root.update_idletasks()

        try:
            # Rename files with progress updates
            total_files = len(self.preview_data)
            for i, (original, new_name) in enumerate(self.preview_data):
                original_path = os.path.join(folder, original)
                new_path = os.path.join(folder, new_name)

                try:
                    # Check if new name already exists and make it unique if necessary
                    if os.path.exists(new_path):
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
                
                # Update progress
                progress = (i + 1) / total_files * 100
                progress_var.set(progress)
                progress_label.config(text=f"Renaming file {i + 1} of {total_files}")
                progress_window.update_idletasks()
        finally:
            # Close progress window
            progress_window.destroy()

        # Show results
        result_msg = f"Renaming completed. {success_count} files successfully renamed, {error_count} errors."
        if errors:
            result_msg += "\n\nErrors:\n" + "\n".join(errors)
            messagebox.showerror("Rename Results", result_msg)
        else:
            messagebox.showinfo("Rename Results", result_msg)

        # Refresh file list and preview
        self.load_files()
        self.preview_renaming()

if __name__ == "__main__":
    root = tk.Tk()
    app = FootageRenamer(root)
    root.mainloop()