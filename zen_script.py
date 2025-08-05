import tkinter as tk
from tkinter import font, messagebox, filedialog, ttk
import platform
import os
import re
import json
import sys

def get_application_path():
    """Returns the base path for the application, whether running as a script or frozen."""
    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle, the PyInstaller bootloader
        # sets `sys.frozen=True`. For a one-file bundle, the path to the temp
        # folder where assets are extracted is stored in `sys._MEIPASS`.
        return getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    else:
        # Running as a normal Python script
        return os.path.dirname(os.path.abspath(__file__))

class ZenScriptEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("zen.script")
        self.current_file_path = None  # Track file path for save state fix
        self.application_path = get_application_path()
        self.settings_file = os.path.join(self.application_path, ".zenscript_settings.json")
        self.available_fonts = None  # Cache for system fonts
        self.setup_methods()
        self.setup_ui()
        self.apply_catppuccin_mocha_theme()
        self.configure_ttk_styles()  # Configure ttk styles after theme setup
        self.load_settings()  # Load saved settings after applying default theme
        self.set_monospace_font()
        self.setup_keybindings()
    
    def setup_methods(self):
        """Initialize all methods that will be called by UI elements"""
        self.new_file = lambda: self._new_file()
        self.open_file = lambda: self._open_file()
        self.save_file = lambda e=None: self._save_file(e)
        self.cut_text = lambda: self._cut_text()
        self.copy_text = lambda: self._copy_text()
        self.paste_text = lambda: self._paste_text()
        self.select_all = lambda e=None: self._select_all(e)
        self.custom_theme_dialog = lambda: self._custom_theme_dialog()
        self.font_options_dialog = lambda: self._font_options_dialog()

    def configure_ttk_styles(self):
        """Configure ttk widget styles to match the Catppuccin Mocha theme"""
        style = ttk.Style()
        
        # Configure Combobox style
        style.theme_use('clam')  # Use clam theme as base for better customization
        
        style.configure('Themed.TCombobox',
                       fieldbackground=self.menu_colors["menu_surface"],
                       background=self.menu_colors["menu_surface"],
                       foreground=self.menu_colors["menu_text"],
                       bordercolor=self.menu_colors["menu_surface"],
                       arrowcolor=self.menu_colors["menu_text"],
                       insertcolor=self.menu_colors["menu_text"],
                       selectbackground=self.menu_colors["menu_blue"],
                       selectforeground="#ffffff")
        
        style.map('Themed.TCombobox',
                 fieldbackground=[('active', self.menu_colors["menu_surface"]),
                                ('focus', self.menu_colors["menu_surface"])],
                 background=[('active', self.menu_colors["menu_surface"]),
                            ('focus', self.menu_colors["menu_surface"])],
                 bordercolor=[('active', self.menu_colors["menu_blue"]),
                             ('focus', self.menu_colors["menu_blue"])],
                 arrowcolor=[('active', self.menu_colors["menu_blue"]),
                            ('focus', self.menu_colors["menu_blue"])])
        
        # Configure the dropdown listbox
        self.root.option_add('*TCombobox*Listbox.Background', self.menu_colors["menu_surface"])
        self.root.option_add('*TCombobox*Listbox.Foreground', self.menu_colors["menu_text"])
        self.root.option_add('*TCombobox*Listbox.selectBackground', self.menu_colors["menu_blue"])
        self.root.option_add('*TCombobox*Listbox.selectForeground', "#ffffff")

    def setup_ui(self):
        """Setup the user interface"""
        self.text = tk.Text(self.root, wrap="word", undo=True, borderwidth=0)
        self.text.pack(expand=True, fill="both", padx=5, pady=5)
        self.bottom_frame = tk.Frame(self.root, bg="#181825")
        self.bottom_frame.pack(side="bottom", fill="x")
        self.status = tk.Label(self.bottom_frame, text="", anchor="w", bg="#181825", fg="#a6adc8")
        self.status.pack(side="left", fill="x", padx=5, pady=(0, 2), expand=True)
        self.create_custom_menu_bar(self.bottom_frame)
        made_with = tk.Label(self.bottom_frame, text="wabi-sabi (侘び寂び) | made with ♡", 
                             anchor="e", fg="#6c7086", bg="#181825")
        made_with.pack(side="right", padx=5, pady=(0, 2))

    def create_custom_menu_bar(self, parent=None):
        """Create a custom menu bar that follows app theme"""
        if parent is None:
            parent = self.root
        self.menu_frame = tk.Frame(parent, bg="#181825", height=25)
        self.menu_frame.pack(side="left", padx=(0, 10))
        # File menu
        file_btn = tk.Menubutton(self.menu_frame, text="File", bg="#181825", fg="#cdd6f4",
                                 activebackground="#313244", activeforeground="#89b4fa",
                                 relief=tk.FLAT)
        file_btn.pack(side="left", padx=(5,0))
        file_menu = tk.Menu(file_btn, tearoff=0, bg="#181825", fg="#cdd6f4",
                            activebackground="#313244", activeforeground="#89b4fa",
                            relief=tk.FLAT, bd=0)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Exit", command=self.root.quit, accelerator="Alt+F4")
        file_btn.config(menu=file_menu)
        # Edit menu
        edit_btn = tk.Menubutton(self.menu_frame, text="Edit", bg="#181825", fg="#cdd6f4",
                                 activebackground="#313244", activeforeground="#89b4fa",
                                 relief=tk.FLAT)
        edit_btn.pack(side="left")
        edit_menu = tk.Menu(edit_btn, tearoff=0, bg="#181825", fg="#cdd6f4",
                            activebackground="#313244", activeforeground="#89b4fa",
                            relief=tk.FLAT, bd=0)
        edit_menu.add_command(label="Undo", command=self.text.edit_undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.text.edit_redo, accelerator="Ctrl+Y")
        edit_menu.add_command(label="Cut", command=self.cut_text, accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=self.copy_text, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=self.paste_text, accelerator="Ctrl+V")
        edit_menu.add_command(label="Select All", command=self.select_all, accelerator="Ctrl+A")
        edit_btn.config(menu=edit_menu)
        # Options menu (removed "Customize All Colors" option)
        options_btn = tk.Menubutton(self.menu_frame, text="Options", bg="#181825", fg="#cdd6f4",
                                    activebackground="#313244", activeforeground="#89b4fa",
                                    relief=tk.FLAT)
        options_btn.pack(side="left")
        options_menu = tk.Menu(options_btn, tearoff=0, bg="#181825", fg="#cdd6f4",
                               activebackground="#313244", activeforeground="#89b4fa",
                               relief=tk.FLAT, bd=0)
        options_menu.add_command(label="Catppuccin Mocha", command=self.apply_catppuccin_mocha_theme)
        options_menu.add_command(label="Custom Theme", command=self.custom_theme_dialog)
        options_menu.add_command(label="Font & Text Options", command=self.font_options_dialog)
        options_btn.config(menu=options_menu)

    def setup_keybindings(self):
        """Configure keyboard shortcuts"""
        # File operations
        self.root.bind('<Control-s>', lambda e: self._save_file(e))
        self.root.bind('<Control-n>', lambda e: self._new_file())
        self.root.bind('<Control-o>', lambda e: self._open_file())
        
        # Edit operations
        self.root.bind('<Control-a>', lambda e: self._select_all(e))
        self.root.bind('<Control-z>', lambda e: self.text.edit_undo())
        self.root.bind('<Control-y>', lambda e: self.text.edit_redo())
        self.root.bind('<Control-x>', lambda e: self._cut_text())
        self.root.bind('<Control-c>', lambda e: self._copy_text())
        
        # Mac-specific bindings
        if platform.system() == "Darwin":
            self.root.bind('<Command-s>', lambda e: self._save_file(e))
            self.root.bind('<Command-n>', lambda e: self._new_file())
            self.root.bind('<Command-o>', lambda e: self._open_file())
            self.root.bind('<Command-a>', lambda e: self._select_all(e))
            self.root.bind('<Command-z>', lambda e: self.text.edit_undo())
            self.root.bind('<Command-y>', lambda e: self.text.edit_redo())
            self.root.bind('<Command-x>', lambda e: self._cut_text())
            self.root.bind('<Command-c>', lambda e: self._copy_text())

    def _new_file(self):
        self.text.delete(1.0, tk.END)
        self.current_file_path = None  # Reset file path
        self.status.config(text="New file")
        self.root.title("zen.script - Untitled")

    def _open_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    self.text.delete(1.0, tk.END)
                    self.text.insert(tk.END, file.read())
                self.current_file_path = file_path  # FIX: Store file path for save state
                self.status.config(text=f"Opened: {file_path}")
                self.root.title(f"zen.script - {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Open Error", f"Could not open file:\n{e}")

    def _save_file(self, event=None):
        content = self.text.get(1.0, tk.END)
        
        # FIX: If file was opened from disk, save to same location
        if self.current_file_path:
            file_path = self.current_file_path
        else:
            # Only ask for save location if it's a new file
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
            )
        
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(content)
                self.current_file_path = file_path  # Update current file path
                self.status.config(text=f"Saved: {file_path}")
                self.root.title(f"zen.script - {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Save Error", f"Could not save file:\n{e}")
        return "break"

    def _cut_text(self):
        # FIX: Use tkinter's native clipboard operations to prevent duplication
        try:
            if self.text.selection_get():
                self.text.event_generate("<<Cut>>")
        except tk.TclError:
            pass  # No selection

    def _copy_text(self):
        # FIX: Use tkinter's native clipboard operations to prevent duplication
        try:
            if self.text.selection_get():
                self.text.event_generate("<<Copy>>")
        except tk.TclError:
            pass  # No selection

    def _paste_text(self):
        # Use tkinter's native paste operation to prevent duplication
        try:
            self.text.event_generate("<<Paste>>")
        except tk.TclError:
            pass  # Handle any paste errors gracefully
        return "break"  # Prevent default paste behavior

    def _select_all(self, event=None):
        self.text.tag_add(tk.SEL, "1.0", tk.END)
        self.text.mark_set(tk.INSERT, "1.0")
        self.text.see(tk.INSERT)
        return "break"

    def _custom_theme_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Custom Theme")
        dialog.geometry("380x280")
        dialog.resizable(True, True)
        center_window(dialog)
        dialog.configure(bg=self.menu_colors["menu_bg"])
        
        # Title
        title = tk.Label(dialog, text="Custom Theme", 
                        bg=self.menu_colors["menu_bg"], fg=self.menu_colors["menu_blue"],
                        font=("Arial", 12, "bold"))
        title.pack(pady=(15, 5))
        
        # Subtitle
        subtitle = tk.Label(dialog, text="(Only affects editor text, not UI)", 
                           bg=self.menu_colors["menu_bg"], fg="#6c7086", 
                           font=("Arial", 9, "italic"))
        subtitle.pack(pady=(0, 15))
        
        # Main frame for inputs
        main_frame = tk.Frame(dialog, bg=self.menu_colors["menu_bg"])
        main_frame.pack(expand=True, fill="both", padx=20, pady=10)
        
        # Background color section
        bg_frame = tk.Frame(main_frame, bg=self.menu_colors["menu_bg"])
        bg_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(bg_frame, text="Editor Background:", 
                bg=self.menu_colors["menu_bg"], fg=self.menu_colors["menu_text"]).pack(anchor="w")
        bg_entry = tk.Entry(bg_frame, bg=self.menu_colors["menu_surface"], fg=self.menu_colors["menu_text"], 
                           borderwidth=1, font=("Consolas", 10))
        bg_entry.pack(fill="x", pady=(3, 0))
        bg_entry.insert(0, self.colors["base"])
        
        # Text color section  
        text_frame = tk.Frame(main_frame, bg=self.menu_colors["menu_bg"])
        text_frame.pack(fill="x", pady=(0, 15))
        
        tk.Label(text_frame, text="Typing Text Color:", 
                bg=self.menu_colors["menu_bg"], fg=self.menu_colors["menu_text"]).pack(anchor="w")
        text_entry = tk.Entry(text_frame, bg=self.menu_colors["menu_surface"], fg=self.menu_colors["menu_text"], 
                             borderwidth=1, font=("Consolas", 10))
        text_entry.pack(fill="x", pady=(3, 0))
        text_entry.insert(0, self.colors["text"])
        
        def save_theme():
            if not self._is_valid_color(bg_entry.get()) or not self._is_valid_color(text_entry.get()):
                messagebox.showerror("Invalid Color", "Please enter valid hex color codes (e.g. #1e1e2e).")
                return
            # Only change editor colors, keep UI colors unchanged
            self.colors["base"] = bg_entry.get()
            self.colors["text"] = text_entry.get()
            self.apply_current_theme()
            self.save_settings()
            messagebox.showinfo("Settings Saved", "Custom theme saved successfully!")
            dialog.destroy()
        
        # Save button (centered)
        save_btn = tk.Button(dialog, text="Save Theme", command=save_theme, 
                            bg=self.menu_colors["menu_blue"], fg="#ffffff",
                            borderwidth=0, relief=tk.FLAT, font=("Arial", 10, "bold"),
                            padx=20, pady=8)
        save_btn.pack(pady=(0, 15))

    def _font_options_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Font & Text Options")
        dialog.geometry("450x380")
        dialog.resizable(True, True)
        center_window(dialog)
        dialog.configure(bg=self.menu_colors["menu_bg"])
        
        # Title
        title = tk.Label(dialog, text="Font & Text Options", 
                        bg=self.menu_colors["menu_bg"], fg=self.menu_colors["menu_blue"],
                        font=("Arial", 12, "bold"))
        title.pack(pady=(15, 20))
        
        # Main frame
        main_frame = tk.Frame(dialog, bg=self.menu_colors["menu_bg"])
        main_frame.pack(expand=True, fill="both", padx=20, pady=10)
        
        # Font family section with searchable combobox
        font_frame = tk.Frame(main_frame, bg=self.menu_colors["menu_bg"])
        font_frame.pack(fill="x", pady=(0, 15))
        
        tk.Label(font_frame, text="Font Family:", 
                bg=self.menu_colors["menu_bg"], fg=self.menu_colors["menu_text"],
                font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 3))
        
        # Get available fonts (cached for speed)
        if self.available_fonts is None:
            self.available_fonts = sorted(list(font.families()))
        
        # Create searchable combobox for fonts with themed style
        font_var = tk.StringVar(value=self.custom_font.actual("family"))
        font_combo = ttk.Combobox(font_frame, textvariable=font_var, values=self.available_fonts, 
                                 state="normal", font=("Consolas", 10), style='Themed.TCombobox')
        font_combo.pack(fill="x", pady=(0, 5))
        
        # Font size section
        size_frame = tk.Frame(main_frame, bg=self.menu_colors["menu_bg"])
        size_frame.pack(fill="x", pady=(0, 15))
        
        tk.Label(size_frame, text="Font Size:", 
                bg=self.menu_colors["menu_bg"], fg=self.menu_colors["menu_text"],
                font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 3))
        size_var = tk.StringVar(value=str(self.custom_font.actual("size")))
        size_entry = tk.Entry(size_frame, textvariable=size_var, 
                             bg=self.menu_colors["menu_surface"], fg=self.menu_colors["menu_text"], 
                             borderwidth=1, font=("Consolas", 10))
        size_entry.pack(fill="x")
        
        # Text wrap section
        wrap_frame = tk.Frame(main_frame, bg=self.menu_colors["menu_bg"])
        wrap_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(wrap_frame, text="Text Wrap:", 
                bg=self.menu_colors["menu_bg"], fg=self.menu_colors["menu_text"],
                font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 3))
        wrap_var = tk.StringVar(value=self.text.cget("wrap"))
        wrap_combo = ttk.Combobox(wrap_frame, textvariable=wrap_var, 
                                 values=["word", "char", "none"], state="readonly",
                                 font=("Consolas", 10), style='Themed.TCombobox')
        wrap_combo.pack(fill="x")
        
        def apply_font():
            try:
                new_family = font_var.get()
                new_size = int(size_var.get())
                
                # Validate font size
                if new_size < 6 or new_size > 72:
                    messagebox.showerror("Invalid Size", "Font size must be between 6 and 72.")
                    return
                    
                self.custom_font.config(family=new_family, size=new_size)
                self.text.configure(font=self.custom_font)
                self.status.configure(font=(new_family, 10))
                
                wrap_value = wrap_var.get()
                if wrap_value in ["word", "char", "none"]:
                    self.text.config(wrap=wrap_value)
                
                self.save_settings()  # Save settings after applying
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Invalid Size", "Please enter a valid number for font size.")
            except Exception as e:
                messagebox.showerror("Font Error", f"Could not apply font settings:\n{e}")
        
        # Apply button
        apply_btn = tk.Button(dialog, text="Apply & Save", command=apply_font,
                             bg=self.menu_colors["menu_surface"], fg=self.menu_colors["menu_text"],
                             borderwidth=1, relief=tk.FLAT, font=("Arial", 10, "bold"),
                             padx=20, pady=8)
        apply_btn.pack(pady=10)

    def save_settings(self):
        """Save current theme and font settings to file"""
        try:
            settings = {
                "theme": {
                    "base": self.colors["base"],
                    "text": self.colors["text"]
                },
                "font": {
                    "family": self.custom_font.actual("family"),
                    "size": self.custom_font.actual("size")
                },
                "text_wrap": self.text.cget("wrap")
            }
            
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            # Silently fail if we can't save settings
            pass

    def load_settings(self):
        """Load saved theme and font settings from file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                
                # Load theme settings
                if "theme" in settings:
                    theme = settings["theme"]
                    if "base" in theme and self._is_valid_color(theme["base"]):
                        self.colors["base"] = theme["base"]
                    if "text" in theme and self._is_valid_color(theme["text"]):
                        self.colors["text"] = theme["text"]
                
                # Load font settings
                if "font" in settings:
                    font_settings = settings["font"]
                    family = font_settings.get("family", "Consolas")
                    size = font_settings.get("size", 12)
                    try:
                        self.custom_font.config(family=family, size=size)
                        self.text.configure(font=self.custom_font)
                        self.status.configure(font=(family, 10))
                    except Exception:
                        pass  # Keep default font if loading fails
                
                # Load text wrap setting
                if "text_wrap" in settings:
                    wrap_value = settings["text_wrap"]
                    if wrap_value in ["word", "char", "none"]:
                        self.text.config(wrap=wrap_value)
                
                # Apply the loaded theme
                self.apply_current_theme()
                # Reconfigure ttk styles after loading settings
                self.configure_ttk_styles()
                
        except Exception as e:
            # Silently fail if we can't load settings
            pass

    def _is_valid_color(self, value):
        # Accepts #RGB, #RRGGBB, #AARRGGBB
        return bool(re.fullmatch(r'#([A-Fa-f0-9]{3}|[A-Fa-f0-9]{6}|[A-Fa-f0-9]{8})', value))

    def set_monospace_font(self):
        system = platform.system()
        font_family = "Courier New"
        font_size = 12
        if system == "Darwin":
            try:
                test_font = font.Font(family="SF Mono", size=font_size)
                font_family = "SF Mono" if test_font.actual()["family"] == "SF Mono" else "Menlo"
            except Exception:
                font_family = "Menlo"
        elif system == "Windows":
            font_family = "Consolas"
        else:
            font_family = "DejaVu Sans Mono"
        self.custom_font = font.Font(family=font_family, size=font_size)
        self.text.configure(font=self.custom_font)
        self.status.configure(font=(font_family, 10))

    def apply_catppuccin_mocha_theme(self):
        # Always reset to default Catppuccin Mocha colors
        self.colors = {
            "base": "#1e1e2e",
            "mantle": "#181825",
            "text": "#cdd6f4",
            "surface0": "#313244",
            "blue": "#89b4fa",
            "subtext0": "#a6adc8",
            "overlay0": "#6c7086"
        }
        # Separate menu colors that won't change with custom themes
        self.menu_colors = {
            "menu_text": "#cdd6f4",
            "menu_bg": "#181825",
            "menu_surface": "#313244",
            "menu_blue": "#89b4fa"
        }
        self.apply_current_theme()
        self.configure_ttk_styles()  # Reconfigure styles after theme change
        self.save_settings()  # Save when switching to default theme

    def apply_current_theme(self):
        self.root.configure(bg=self.colors["base"])
        self.text.configure(
            bg=self.colors["base"],
            fg=self.colors["text"],
            insertbackground=self.colors.get("blue", "#89b4fa"),
            selectbackground=self.colors.get("surface0", "#313244"),
            selectforeground=self.colors["text"],
            inactiveselectbackground=self.colors.get("surface0", "#313244"),
            highlightthickness=0,
            relief=tk.FLAT
        )
        # Keep UI elements with original colors
        self.status.configure(
            bg=self.menu_colors.get("menu_bg", "#181825"),
            fg=self.colors.get("subtext0", "#a6adc8")
        )
        self.bottom_frame.configure(bg=self.menu_colors.get("menu_bg", "#181825"))
        
        if hasattr(self, 'menu_frame'):
            self.menu_frame.configure(bg=self.menu_colors.get("menu_bg", "#181825"))
            for child in self.menu_frame.winfo_children():
                if isinstance(child, tk.Menubutton):
                    child.configure(
                        bg=self.menu_colors.get("menu_bg", "#181825"),
                        fg=self.menu_colors.get("menu_text", "#cdd6f4"),
                        activebackground=self.menu_colors.get("menu_surface", "#313244"),
                        activeforeground=self.menu_colors.get("menu_blue", "#89b4fa")
                    )

def center_window(window, width=None, height=None):
    """Centers a tkinter window. If width/height are provided, it sets the size."""
    window.update_idletasks()
    
    # If width and height are not provided, use the window's current size
    if width is None:
        width = window.winfo_width()
    if height is None:
        height = window.winfo_height()

    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry(f'{width}x{height}+{x}+{y}')

if __name__ == "__main__":
    root = tk.Tk()
    center_window(root, 800, 600)
    # Windows-specific theming fixes
    if platform.system() == "Windows":
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass  # Ignore DPI errors
    
    # Set window icon from the application's directory to make it portable
    application_path = get_application_path()
    icon_path = os.path.join(application_path, "logo_zen_dot.ico")
    png_icon_path = os.path.join(application_path, "logo_zen_dot.png")
    try:
        if platform.system() == "Windows":
            if os.path.exists(icon_path):
                root.iconbitmap(default=icon_path)
        else:
            if os.path.exists(png_icon_path):
                img = tk.PhotoImage(file=png_icon_path)
                root.iconphoto(True, img)
    except Exception:
        # Silently fail if the icon can't be loaded.
        pass
    
    editor = ZenScriptEditor(root)
    root.mainloop()