import os
import tkinter as tk
from tkinter import ttk, messagebox
import sys
from typing import List, Dict, Tuple
import threading
from datetime import datetime
import time
import re
import shutil

class SmartStorageOptimizer:
    def __init__(self):
        # Initialize root window
        self.root = tk.Tk()
        self.root.title("Smart Storage Optimizer")
        self.root.geometry("1200x800")
        
        # Enhanced dark emerald theme
        self.bg_color = "#0A1F0A"  # Dark emerald background
        self.fg_color = "#E0E0E0"  # Light gray text
        self.accent_color = "#1A2F1A"  # Lighter emerald
        self.highlight_color = "#2D4F2D"  # Emerald highlight
        self.border_color = "#FFFFFF"  # White borders
        self.button_bg = "#234223"  # Button background
        self.button_fg = "#FFFFFF"  # Button text
        self.delete_button_bg = "#4F1F1F"  # Dark red for delete
        
        # Configure root
        self.root.configure(bg=self.bg_color)
        
        # Initialize variables
        self.recommendations = []
        self.current_batch_index = 0
        self.batch_size = 5
        self.workstation_active = False
        self.overlay = None
        self.recommendation_windows = []
        
        # File patterns for smart detection
        self.pattern_rules = {
            "temp_files": r".*\.(tmp|temp)$",
            "logs": r".*\.log$",
            "downloads": r".*downloads.*",
            "old_files": r".*\.(old|bak)$",
            "large_media": r".*\.(mp4|mkv|avi|mov)$",
            "duplicate_pattern": r".*\(\d+\).*"
        }
        
        # Create UI
        self.create_ui()

    def create_ui(self):
        # Main container
        self.main_frame = tk.Frame(self.root, bg=self.bg_color)
        self.main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Drive selection frame
        self.create_drive_frame()
        
        # Status and recommendations frame
        self.create_status_frame()
        
        # Workstation button frame
        self.create_workstation_frame()

    def create_drive_frame(self):
        drive_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        drive_frame.pack(fill='x', pady=10)
        
        # Drive selection
        drives = self.get_drives()
        self.drive_var = tk.StringVar(value=drives[0] if drives else "")
        
        tk.Label(
            drive_frame,
            text="Select Drive:",
            bg=self.bg_color,
            fg=self.fg_color,
            font=('Arial', 12, 'bold')
        ).pack(side='left', padx=5)
        
        drive_menu = tk.OptionMenu(drive_frame, self.drive_var, *drives)
        drive_menu.config(
            bg=self.button_bg,
            fg=self.fg_color,
            activebackground=self.highlight_color,
            activeforeground=self.fg_color
        )
        drive_menu.pack(side='left', padx=5)
        
        # Scan button
        self.scan_button = tk.Button(
            drive_frame,
            text="Start Smart Scan",
            command=self.start_smart_scan,
            bg=self.button_bg,
            fg=self.fg_color,
            activebackground=self.highlight_color,
            font=('Arial', 12, 'bold'),
            padx=20,
            pady=5
        )
        self.scan_button.pack(side='left', padx=20)

    def create_status_frame(self):
        """Enhanced status frame with dual-panel display"""
        self.status_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        self.status_frame.pack(fill='both', expand=True, pady=10)
        
        # Status label at top
        self.status_label = tk.Label(
            self.status_frame,
            text="Ready to scan...",
            bg=self.accent_color,
            fg=self.fg_color,
            font=('Arial', 11),
            wraplength=800,
            padx=10,
            pady=10
        )
        self.status_label.pack(fill='x', pady=5)
        
        # Create split panel frame
        panel_frame = tk.Frame(self.status_frame, bg=self.bg_color)
        panel_frame.pack(fill='both', expand=True, pady=5)
        
        # Left panel: Smart Recommendations Bank
        self.create_recommendation_bank(panel_frame)
        
        # Right panel: Itemized List
        self.create_itemized_list(panel_frame)

    def create_recommendation_bank(self, parent):
        """Creates the smart recommendation bank panel"""
        bank_frame = tk.Frame(parent, bg=self.bg_color)
        bank_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        # Header
        tk.Label(
            bank_frame,
            text="Smart Recommendations",
            bg=self.bg_color,
            fg="#90EE90",  # Light green text
            font=('Arial', 12, 'bold')
        ).pack(fill='x', pady=5)
        
        # Create category frames with dark emerald styling
        categories = [
            ("unused_files", "Unused Files (180+ days)"),
            ("large_files", "Large Files (1GB+)"),
            ("old_files", "Old Downloads & Temp Files")
        ]
        
        for cat_id, cat_name in categories:
            frame = tk.Frame(bank_frame, bg=self.bg_color)
            frame.pack(fill='x', pady=5, padx=5)
            
            # Category header
            tk.Label(
                frame,
                text=cat_name,
                bg=self.accent_color,
                fg="#90EE90",  # Light green text
                font=('Arial', 10, 'bold'),
                padx=5,
                pady=2
            ).pack(fill='x')
            
            # Listbox for files
            listbox = tk.Listbox(
                frame,
                bg="#0A1F0A",  # Very dark green
                fg=self.fg_color,
                selectbackground="#234223",  # Darker emerald for selection
                selectforeground=self.fg_color,
                height=6,
                font=('Arial', 9),
                relief='solid',
                borderwidth=1
            )
            listbox.pack(fill='both', expand=True, pady=2)
            
            # Store listbox reference
            setattr(self, f'{cat_id}_listbox', listbox)

    def create_itemized_list(self, parent):
        """Creates an organized itemized list with auto-scroll control"""
        list_frame = tk.Frame(parent, bg='white')
        list_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        # Create Treeview with updated styling
        self.file_tree = ttk.Treeview(
            list_frame,
            columns=("size", "name", "last_used", "age", "reason"),
            show="headings",
            height=10,
            selectmode="browse"
        )
        
        # Configure style
        style = ttk.Style()
        
        # Configure Treeview style
        style.configure(
            "Treeview",
            background="white",
            foreground="black",
            fieldbackground="white",
            rowheight=25
        )
        
        # Configure heading style with dark green background
        style.configure(
            "Treeview.Heading",
            background="#0A2F0A",  # Dark green
            foreground="white",
            font=('Arial', 10, 'bold')
        )
        
        # Force the header background to stay dark green
        style.map("Treeview.Heading",
            background=[('active', '#0A2F0A'), ('pressed', '#0A2F0A')]
        )
        
        # Configure columns
        columns = [
            ("size", "Size (MB)", 80),
            ("name", "File Name", 300),
            ("last_used", "Last Used", 120),
            ("age", "Age (Days)", 100),
            ("reason", "Recommendation", 200)
        ]
        
        for col_id, heading, width in columns:
            self.file_tree.column(col_id, width=width, minwidth=width)
            self.file_tree.heading(col_id, text=heading)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=self.custom_scrollbar_set)
        
        # Bind selection events
        self.file_tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.file_tree.bind("<Button-1>", self.on_click)
        self.file_tree.bind("<Button-3>", self.show_context_menu)
        
        # Pack elements
        self.file_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Initialize scroll control variables
        self.auto_scroll_enabled = True
        self.last_selected_item = None

    def custom_scrollbar_set(self, first, last):
        """Custom scrollbar control that respects selection"""
        if self.auto_scroll_enabled:
            self.file_tree.yview_moveto(float(first))

    def on_tree_select(self, event):
        """Handles tree selection to control scrolling"""
        selection = self.file_tree.selection()
        if selection:
            self.auto_scroll_enabled = False
            self.last_selected_item = selection[0]
            
            # Ensure selected item is visible
            self.file_tree.see(selection[0])

    def on_click(self, event):
        """Handles mouse clicks on the tree"""
        region = self.file_tree.identify_region(event.x, event.y)
        if region == "nothing":
            # Click in empty space
            self.file_tree.selection_remove(self.file_tree.selection())
            self.auto_scroll_enabled = True
            self.last_selected_item = None

    def update_tree_item(self, file_path: str, size_mb: float, reason: str):
        """Updates tree while respecting scroll position"""
        try:
            # Get file stats
            file_stat = os.stat(file_path)
            last_used = datetime.fromtimestamp(file_stat.st_atime)
            age_days = (time.time() - file_stat.st_atime) / (24 * 3600)
            
            # Insert new item
            new_item = self.file_tree.insert(
                "",
                0,
                values=(
                    f"{size_mb:.2f}",
                    file_path,
                    last_used.strftime("%Y-%m-%d"),
                    f"{age_days:.0f}",
                    reason
                ),
                tags=('default',)
            )
            
            # Configure tag
            self.file_tree.tag_configure('default', background='white', foreground='black')
            
            # Maintain selection if exists
            if self.last_selected_item and not self.auto_scroll_enabled:
                self.file_tree.see(self.last_selected_item)
                self.file_tree.selection_set(self.last_selected_item)
            
        except Exception as e:
            print(f"Error updating tree for {file_path}: {e}")

    def create_workstation_frame(self):
        self.workstation_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        self.workstation_frame.pack(fill='x', pady=10)
        
        self.workstation_button = tk.Button(
            self.workstation_frame,
            text="Enter Workstation Mode",
            command=self.toggle_workstation_mode,
            bg=self.highlight_color,
            fg=self.fg_color,
            font=('Arial', 12, 'bold'),
            state='disabled',
            padx=20,
            pady=10
        )
        self.workstation_button.pack(side='right')

    def start_smart_scan(self):
        """Initiates the smart scan process"""
        self.scan_button.config(state='disabled')
        self.status_label.config(text="Scanning in progress...")
        self.recommendations = []
        
        # Start scan in background thread
        scan_thread = threading.Thread(target=self.perform_scan)
        scan_thread.daemon = True
        scan_thread.start()

    def perform_scan(self):
        """Enhanced scanning process"""
        drive = self.drive_var.get()
        files_scanned = 0
        total_size = 0
        
        for root, _, files in os.walk(drive):
            for file in files:
                try:
                    file_path = os.path.join(root, file)
                    files_scanned += 1
                    
                    # Get file info
                    file_stat = os.stat(file_path)
                    size_mb = file_stat.st_size / (1024 * 1024)
                    age_days = (time.time() - file_stat.st_mtime) / (24 * 3600)
                    
                    # Check if file should be recommended
                    reason = self.get_recommendation_reason(file_path, size_mb, age_days)
                    if reason:
                        self.recommendations.append((file_path, size_mb, reason))
                        total_size += size_mb
                        self.update_recommendations(files_scanned, total_size)
                
                except (PermissionError, OSError):
                    continue
        
        # Scan complete
        self.root.after(0, lambda: self.scan_complete(files_scanned, total_size))

    def get_recommendation_reason(self, file_path: str, size_mb: float, age_days: float) -> str:
        """Enhanced smart file detection"""
        try:
            # Skip system directories and files
            if any(sys_dir in file_path.lower() for sys_dir in [
                'windows', 'program files', 'appdata', '$recycle.bin', 'system32'
            ]):
                return ""
            
            file_name = os.path.basename(file_path).lower()
            
            # Skip system files and temporary files
            if file_name.startswith(('.', '$')) or file_name in ['desktop.ini', 'thumbs.db']:
                return ""
            
            if size_mb >= 1000:  # Files larger than 1GB
                return f"Very large file ({size_mb:.1f}MB)"
            elif age_days > 180:  # Files not accessed in 6 months
                return f"Old file, not accessed in {age_days:.0f} days"
            elif size_mb >= 100:  # Files larger than 100MB
                if any(ext in file_name for ext in ['.mp4', '.mov', '.avi', '.mkv']):
                    return f"Large media file ({size_mb:.1f}MB)"
                return f"Large file ({size_mb:.1f}MB)"
            
            return ""
        except:
            return ""

    def update_status(self, message: str):
        """Updates the status label"""
        self.root.after(0, lambda: self.status_label.config(text=message))

    def update_recommendations(self, files_scanned: int, total_size: float):
        """Real-time updates with better organization"""
        def update_ui():
            # Update scan status
            self.status_label.config(text=f"Scanned {files_scanned:,} files...")
            
            # Update tree and recommendation bank
            if self.recommendations:
                latest = self.recommendations[-1]
                file_path, size_mb, reason = latest
                
                # Update tree with better formatting
                self.update_tree_item(file_path, size_mb, reason)
                
                # Update recommendation banks
                file_name = os.path.basename(file_path)
                age_days = (time.time() - os.path.getmtime(file_path)) / (24 * 3600)
                entry = f"{file_name} ({size_mb:.1f}MB) - {age_days:.0f} days old"
                
                if age_days > 180:
                    self.unused_files_listbox.insert(0, entry)
                elif size_mb > 1000:
                    self.large_files_listbox.insert(0, entry)
                elif 'download' in file_path.lower() or file_path.endswith(('.tmp', '.temp')):
                    self.old_files_listbox.insert(0, entry)
                
                # Enable workstation button if we have enough recommendations
                if len(self.recommendations) >= 5:
                    self.workstation_button.config(state='normal')
        
        # Update frequently but not too often to prevent GUI lag
        if files_scanned % 10 == 0 or files_scanned == 1:
            self.root.after(1, update_ui)

    def scan_complete(self, files_scanned: int, total_size: float):
        """Handles scan completion"""
        self.root.after(0, lambda: [
            self.scan_button.config(state='normal'),
            self.workstation_button.config(state='normal'),
            self.status_label.config(
                text=f"Scan Complete!\n"
                     f"Files Scanned: {files_scanned:,}\n"
                     f"Potential Space Savings: {total_size:.1f}MB\n"
                     f"Click 'Enter Workstation Mode' to review {len(self.recommendations)} recommendations"
            ),
            messagebox.showinfo("Scan Complete", 
                              f"Found {len(self.recommendations)} items to review")
        ])

    def toggle_workstation_mode(self):
        """Toggles workstation mode with proper exit handling"""
        if not self.workstation_active and self.recommendations:
            self.workstation_active = True
            self.current_batch_index = 0
            self.recommendation_windows = []
            
            # Create overlay and recommendations
            self.create_overlay()
            self.root.after(100, self.show_recommendation_batch)
        else:
            self.exit_workstation_mode()

    def show_recommendation_batch(self):
        """Shows the current batch of 5 recommendations"""
        if not self.recommendations:
            messagebox.showinfo("Complete", "No recommendations to review!")
            self.exit_workstation_mode()
            return
        
        # Clear any existing windows
        for win in self.recommendation_windows:
            if win and win.winfo_exists():
                win.destroy()
        self.recommendation_windows.clear()
        
        # Calculate window positions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        win_width = 400
        win_height = 300
        
        # Define fixed positions for 5 windows
        positions = [
            (screen_width//4 - win_width//2, screen_height//3),           # Top left
            (screen_width//2 - win_width//2, screen_height//3),           # Top center
            (3*screen_width//4 - win_width//2, screen_height//3),         # Top right
            (screen_width//3 - win_width//2, 2*screen_height//3),         # Bottom left
            (2*screen_width//3 - win_width//2, 2*screen_height//3)        # Bottom right
        ]
        
        # Create windows for current batch
        start_idx = self.current_batch_index
        for i in range(5):
            if start_idx + i >= len(self.recommendations):
                break
            
            rec = self.recommendations[start_idx + i]
            file_path, size_mb, reason = rec
            
            # Create window
            win = tk.Toplevel(self.root)
            win.configure(bg=self.accent_color)
            win.geometry(f"{win_width}x{win_height}+{positions[i][0]}+{positions[i][1]}")
            win.resizable(False, False)
            win.attributes('-topmost', True)
            win.overrideredirect(True)
            
            # Title
            tk.Label(
                win,
                text=f"Recommendation {i + 1}",
                bg=self.accent_color,
                fg='#90EE90',
                font=('Arial', 14, 'bold')
            ).pack(pady=10)
            
            # File details
            age_days = (time.time() - os.path.getmtime(file_path)) / (24 * 3600)
            details = (
                f"Size: {size_mb:.1f} MB\n"
                f"Age: {age_days:.0f} days\n"
                f"Reason: {reason}\n\n"
                f"Path: {file_path}"
            )
            
            tk.Label(
                win,
                text=details,
                bg=self.accent_color,
                fg=self.fg_color,
                wraplength=350,
                justify='left'
            ).pack(pady=10, padx=20)
            
            # Buttons
            button_frame = tk.Frame(win, bg=self.accent_color)
            button_frame.pack(side='bottom', pady=20)
            
            for btn_text, btn_bg, action in [
                ("Delete", '#8B0000', 'delete'),
                ("Move", '#1B4D3E', 'move'),
                ("Copy", '#1B4D3E', 'copy'),
                ("Skip", '#1B4D3E', 'skip')
            ]:
                tk.Button(
                    button_frame,
                    text=btn_text,
                    command=lambda f=file_path, w=win, a=action: self.process_action(a, f, w),
                    bg=btn_bg,
                    fg='white',
                    width=8,
                    font=('Arial', 10, 'bold'),
                    relief='solid',
                    borderwidth=1
                ).pack(side='left', padx=5)
            
            self.recommendation_windows.append(win)
        
        # Update batch counter
        total = len(self.recommendations)
        self.batch_label.config(
            text=f"Reviewing recommendations {start_idx + 1}-{min(start_idx + 5, total)} of {total}"
        )

    def create_overlay(self):
        """Creates overlay with proper exit binding"""
        self.overlay = tk.Toplevel(self.root)
        self.overlay.configure(bg='#0A2F0A')
        self.overlay.attributes('-alpha', 0.9, '-topmost', True)
        self.overlay.state('zoomed')
        
        # Bind click on overlay to exit
        self.overlay.bind("<Button-1>", lambda e: self.exit_workstation_mode())
        
        # Bind window close event
        self.overlay.protocol("WM_DELETE_WINDOW", self.exit_workstation_mode)
        
        # Fixed position header
        header_frame = tk.Frame(self.overlay, bg='#0A2F0A')
        header_frame.place(relx=0.5, rely=0.05, anchor='n')
        
        # Batch counter with fixed position
        self.batch_label = tk.Label(
            header_frame,
            text=f"Reviewing recommendations 1-5 of {len(self.recommendations)}",
            bg='#0A2F0A',
            fg='#90EE90',
            font=('Arial', 14, 'bold')
        )
        self.batch_label.pack(pady=10)

    def exit_workstation_mode(self):
        """Properly exits workstation mode and closes all windows"""
        self.workstation_active = False
        
        # Close all recommendation windows
        if hasattr(self, 'recommendation_windows'):
            for win in self.recommendation_windows:
                if win and win.winfo_exists():
                    win.destroy()
            self.recommendation_windows.clear()
        
        # Close the overlay
        if hasattr(self, 'overlay') and self.overlay:
            self.overlay.destroy()
            self.overlay = None
        
        # Reset batch index
        self.current_batch_index = 0

    def get_drives(self) -> List[str]:
        """Gets available drives"""
        if sys.platform == "win32":
            return [f"{d}:\\" for d in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" 
                    if os.path.exists(f"{d}:")]
        return ["/"]

    def run(self):
        """Starts the application"""
        self.root.mainloop()

    def move_file(self, file_path: str, window: tk.Toplevel):
        """Handle moving files"""
        from tkinter import filedialog
        try:
            dest_dir = filedialog.askdirectory(title="Select Destination Directory")
            if dest_dir:
                new_path = os.path.join(dest_dir, os.path.basename(file_path))
                shutil.move(file_path, new_path)
                window.destroy()
                self.recommendations = [r for r in self.recommendations if r[0] != file_path]
                self.check_batch_complete()
        except Exception as e:
            messagebox.showerror("Error", f"Could not move file: {str(e)}")

    def copy_file(self, file_path: str, window: tk.Toplevel):
        """Handle copying files"""
        from tkinter import filedialog
        try:
            dest_dir = filedialog.askdirectory(title="Select Destination Directory")
            if dest_dir:
                new_path = os.path.join(dest_dir, os.path.basename(file_path))
                shutil.copy2(file_path, new_path)
                window.destroy()
                self.recommendations = [r for r in self.recommendations if r[0] != file_path]
                self.check_batch_complete()
        except Exception as e:
            messagebox.showerror("Error", f"Could not copy file: {str(e)}")

    def enter_workstation_mode(self):
        """Initiates workstation mode"""
        if len(self.recommendations) == 0:
            messagebox.showinfo("No Recommendations", "No files to review!")
            return
        
        self.workstation_active = True
        self.current_batch_index = 0
        
        # Create overlay first
        self.create_overlay()
        
        # Create and show initial recommendations
        self.create_recommendation_windows()
        
        # Force windows to top
        self.root.after(100, self.maintain_window_positions)

    def maintain_window_positions(self):
        """Ensures windows stay on top and visible"""
        if self.workstation_active:
            for win in self.recommendation_windows:
                if win.winfo_exists():
                    win.lift()
                    win.attributes('-topmost', True)
            self.root.after(100, self.maintain_window_positions)

    def process_action(self, action, file_path, window):
        """Processes action and shows next recommendation"""
        try:
            # Handle the action
            if action == 'delete':
                if not messagebox.askyesno("Confirm Delete", f"Delete {file_path}?"):
                    return
                os.remove(file_path)
            elif action == 'move':
                self.move_file(file_path)
            elif action == 'copy':
                self.copy_file(file_path)
            
            # Find current recommendation index
            current_index = next(i for i, r in enumerate(self.recommendations) 
                               if r[0] == file_path)
            
            # Get the next recommendation (5 positions ahead)
            next_index = self.current_batch_index + 5
            
            # Remove the current recommendation
            self.recommendations.pop(current_index)
            
            # If there's a next recommendation available, show it
            if next_index < len(self.recommendations):
                next_rec = self.recommendations[next_index]
                window_index = self.recommendation_windows.index(window)
                
                # Clear current window content
                for widget in window.winfo_children():
                    widget.destroy()
                    
                # Display next recommendation in same window
                self.display_recommendation(
                    window,
                    next_rec[0],  # file_path
                    next_rec[1],  # size_mb
                    next_rec[2],  # reason
                    window_index + 1  # position
                )
            else:
                # If no more recommendations, check if batch is complete
                window.destroy()
                if not any(win.winfo_exists() for win in self.recommendation_windows):
                    self.check_batch_complete()
            
            # Update batch counter
            total = len(self.recommendations)
            self.batch_label.config(
                text=f"Reviewing recommendations {self.current_batch_index + 1}-{min(self.current_batch_index + 5, total)} of {total}"
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Error processing file: {str(e)}")

    def display_recommendation(self, window, file_path, size_mb, reason, position):
        """Displays recommendation content in window"""
        # Title
        tk.Label(
            window,
            text=f"Recommendation {position}",
            bg=self.accent_color,
            fg='#90EE90',
            font=('Arial', 14, 'bold')
        ).pack(pady=10)
        
        # File details
        age_days = (time.time() - os.path.getmtime(file_path)) / (24 * 3600)
        details = (
            f"Size: {size_mb:.1f} MB\n"
            f"Age: {age_days:.0f} days\n"
            f"Reason: {reason}\n\n"
            f"Path: {file_path}"
        )
        
        tk.Label(
            window,
            text=details,
            bg=self.accent_color,
            fg=self.fg_color,
            wraplength=350,
            justify='left'
        ).pack(pady=10, padx=20)
        
        # Action buttons
        button_frame = tk.Frame(window, bg=self.accent_color)
        button_frame.pack(side='bottom', pady=20)
        
        buttons = [
            ("Delete", '#8B0000', lambda: self.process_action('delete', file_path, window)),
            ("Move", '#1B4D3E', lambda: self.process_action('move', file_path, window)),
            ("Copy", '#1B4D3E', lambda: self.process_action('copy', file_path, window)),
            ("Skip", '#1B4D3E', lambda: self.process_action('skip', file_path, window))
        ]
        
        for text, bg, cmd in buttons:
            tk.Button(
                button_frame,
                text=text,
                command=cmd,
                bg=bg,
                fg='white',
                width=8,
                font=('Arial', 10, 'bold'),
                relief='solid',
                borderwidth=1
            ).pack(side='left', padx=5)

    def show_context_menu(self, event):
        """Shows context menu on right-click"""
        try:
            # Select row under mouse
            item = self.file_tree.identify_row(event.y)
            if item:
                self.file_tree.selection_set(item)
                self.context_menu.post(event.x_root, event.y_root)
        except Exception as e:
            print(f"Error showing context menu: {e}")

    def context_delete_file(self):
        """Handles delete from context menu"""
        selected = self.file_tree.selection()
        if selected:
            item = selected[0]
            values = self.file_tree.item(item)['values']
            file_path = values[1]  # File name column
            
            if messagebox.askyesno("Confirm Delete", f"Delete {file_path}?"):
                try:
                    os.remove(file_path)
                    self.file_tree.delete(item)
                except Exception as e:
                    messagebox.showerror("Error", f"Could not delete file: {str(e)}")

    def context_move_file(self):
        """Handles move from context menu"""
        selected = self.file_tree.selection()
        if selected:
            item = selected[0]
            values = self.file_tree.item(item)['values']
            file_path = values[1]
            self.move_file(file_path)

    def context_copy_file(self):
        """Handles copy from context menu"""
        selected = self.file_tree.selection()
        if selected:
            item = selected[0]
            values = self.file_tree.item(item)['values']
            file_path = values[1]
            self.copy_file(file_path)

    def on_select(self, event):
        """Handles tree view selection"""
        # Selection event handler - can be used to add additional functionality
        pass

if __name__ == "__main__":
    app = SmartStorageOptimizer()
    app.run()