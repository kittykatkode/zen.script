import tkinter as tk
from tkinter import font, messagebox, filedialog
import platform
import os
import re

class ZenScriptEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("zen.script")
        self.setup_methods()
        self.setup_ui()
        self.apply_catppuccin_mocha_theme()
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
        self.advanced_theme_dialog = lambda: self._advanced_theme_dialog()  # <-- add this line

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
                            activebackground="#313244", activeforeground="#89b4fa")
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit, accelerator="Alt+F4")
        file_btn.config(menu=file_menu)
        # Edit menu
        edit_btn = tk.Menubutton(self.menu_frame, text="Edit", bg="#181825", fg="#cdd6f4",
                                 activebackground="#313244", activeforeground="#89b4fa",
                                 relief=tk.FLAT)
        edit_btn.pack(side="left")
        edit_menu = tk.Menu(edit_btn, tearoff=0, bg="#181825", fg="#cdd6f4",
                            activebackground="#313244", activeforeground="#89b4fa")
        edit_menu.add_command(label="Undo", command=self.text.edit_undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.text.edit_redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=self.cut_text, accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=self.copy_text, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=self.paste_text, accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="Select All", command=self.select_all, accelerator="Ctrl+A")
        edit_btn.config(menu=edit_menu)
        # Options menu (was Theme)
        options_btn = tk.Menubutton(self.menu_frame, text="Options", bg="#181825", fg="#cdd6f4",
                                    activebackground="#313244", activeforeground="#89b4fa",
                                    relief=tk.FLAT)
        options_btn.pack(side="left")
        options_menu = tk.Menu(options_btn, tearoff=0, bg="#181825", fg="#cdd6f4",
                               activebackground="#313244", activeforeground="#89b4fa")
        options_menu.add_command(label="Catppuccin Mocha", command=self.apply_catppuccin_mocha_theme)
        options_menu.add_command(label="Custom Theme", command=self.custom_theme_dialog)
        options_menu.add_command(label="Customize All Colors", command=self.advanced_theme_dialog)  # <-- use the lambda
        options_menu.add_separator()
        options_menu.add_command(label="Font & Text Options", command=self.font_options_dialog)
        options_btn.config(menu=options_menu)

    def setup_keybindings(self):
        """Configure keyboard shortcuts"""
        self.root.bind('<Control-s>', self.save_file)
        if platform.system() == "Darwin":
            self.root.bind('<Command-s>', self.save_file)
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-a>', lambda e: self.select_all())
        self.root.bind_all('<Control-z>', lambda e: self.text.edit_undo())
        self.root.bind_all('<Control-y>', lambda e: self.text.edit_redo())
        self.root.bind_all('<Control-x>', lambda e: self.cut_text())
        self.root.bind_all('<Control-c>', lambda e: self.copy_text())
        self.root.bind_all('<Control-v>', lambda e: self.paste_text())

    def _new_file(self):
        self.text.delete(1.0, tk.END)
        self.status.config(text="New file")

    def _open_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    self.text.delete(1.0, tk.END)
                    self.text.insert(tk.END, file.read())
                self.status.config(text=f"Opened: {file_path}")
            except Exception as e:
                messagebox.showerror("Open Error", f"Could not open file:\n{e}")

    def _save_file(self, event=None):
        content = self.text.get(1.0, tk.END)
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(content)
                self.status.config(text=f"Saved: {file_path}")
            except Exception as e:
                messagebox.showerror("Save Error", f"Could not save file:\n{e}")
        return "break"

    def _cut_text(self):
        self.text.event_generate("<<Cut>>")

    def _copy_text(self):
        self.text.event_generate("<<Copy>>")

    def _paste_text(self):
        self.text.event_generate("<<Paste>>")

    def _select_all(self, event=None):
        self.text.tag_add(tk.SEL, "1.0", tk.END)
        self.text.mark_set(tk.INSERT, "1.0")
        self.text.see(tk.INSERT)
        return "break"

    def _custom_theme_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Custom Theme")
        dialog.geometry("320x220")
        dialog.resizable(True, True)
        dialog.configure(bg=self.colors["mantle"])
        tk.Label(dialog, text="Custom Theme", 
                 bg=self.colors["mantle"], fg=self.colors["blue"]).pack(pady=10)
        tk.Label(dialog, text="Background:", bg=self.colors["mantle"], fg=self.colors["text"]).pack()
        bg_entry = tk.Entry(dialog, bg=self.colors["surface0"], fg=self.colors["text"], borderwidth=1)
        bg_entry.pack(pady=2)
        bg_entry.insert(0, self.colors["base"])
        tk.Label(dialog, text="Text Color:", bg=self.colors["mantle"], fg=self.colors["text"]).pack()
        text_entry = tk.Entry(dialog, bg=self.colors["surface0"], fg=self.colors["text"], borderwidth=1)
        text_entry.pack(pady=2)
        text_entry.insert(0, self.colors["text"])
        def apply_theme():
            if not self._is_valid_color(bg_entry.get()) or not self._is_valid_color(text_entry.get()):
                messagebox.showerror("Invalid Color", "Please enter valid hex color codes (e.g. #1e1e2e).")
                return
            self.colors["base"] = bg_entry.get()
            self.colors["text"] = text_entry.get()
            self.apply_current_theme()
            dialog.destroy()
        tk.Button(dialog, text="Apply", command=apply_theme, 
                  bg=self.colors["surface0"], fg=self.colors["text"],
                  borderwidth=0, relief=tk.FLAT).pack(pady=10)

    def _advanced_theme_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Customize All Colors")
        dialog.geometry("400x500")
        dialog.resizable(True, True)
        dialog.configure(bg=self.colors["mantle"])
        entries = {}
        tk.Label(dialog, text="Customize All Theme Colors", 
                 bg=self.colors["mantle"], fg=self.colors["blue"]).pack(pady=10)
        for key in self.colors:
            tk.Label(dialog, text=f"{key}:", bg=self.colors["mantle"], fg=self.colors["text"]).pack()
            entry = tk.Entry(dialog, bg=self.colors["surface0"], fg=self.colors["text"], borderwidth=1)
            entry.pack(pady=2)
            entry.insert(0, self.colors[key])
            entries[key] = entry
        def apply_all():
            for key in self.colors:
                val = entries[key].get()
                if not self._is_valid_color(val):
                    messagebox.showerror("Invalid Color", f"Color for '{key}' is not valid hex (e.g. #1e1e2e).")
                    return
                self.colors[key] = val
            self.apply_current_theme()
            dialog.destroy()
        tk.Button(dialog, text="Apply All", command=apply_all, 
                  bg=self.colors["surface0"], fg=self.colors["text"],
                  borderwidth=0, relief=tk.FLAT).pack(pady=10)

    def _font_options_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Font & Text Options")
        dialog.geometry("350x250")
        dialog.resizable(True, True)
        dialog.configure(bg=self.colors["mantle"])
        tk.Label(dialog, text="Font & Text Options", bg=self.colors["mantle"], fg=self.colors["blue"]).pack(pady=10)
        # Font family
        tk.Label(dialog, text="Font Family:", bg=self.colors["mantle"], fg=self.colors["text"]).pack()
        available_fonts = list(font.families())
        available_fonts.sort()
        font_var = tk.StringVar(value=self.custom_font.actual("family"))
        font_dropdown = tk.OptionMenu(dialog, font_var, *available_fonts)
        font_dropdown.config(bg=self.colors["surface0"], fg=self.colors["text"])
        font_dropdown.pack(pady=2)
        # Font size
        tk.Label(dialog, text="Font Size:", bg=self.colors["mantle"], fg=self.colors["text"]).pack()
        size_var = tk.StringVar(value=str(self.custom_font.actual("size")))
        size_entry = tk.Entry(dialog, textvariable=size_var, bg=self.colors["surface0"], fg=self.colors["text"], borderwidth=1)
        size_entry.pack(pady=2)
        # Text wrap
        tk.Label(dialog, text="Text Wrap:", bg=self.colors["mantle"], fg=self.colors["text"]).pack()
        wrap_var = tk.StringVar(value=self.text.cget("wrap"))
        wrap_menu = tk.OptionMenu(dialog, wrap_var, "word", "char", "none")
        wrap_menu.config(bg=self.colors["surface0"], fg=self.colors["text"])
        wrap_menu.pack(pady=2)
        def apply_font():
            try:
                new_family = font_var.get()
                new_size = int(size_var.get())
                self.custom_font.config(family=new_family, size=new_size)
                self.text.configure(font=self.custom_font)
                self.status.configure(font=(new_family, 10))
                self.text.config(wrap=wrap_var.get())
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Font Error", f"Could not apply font settings:\n{e}")
        tk.Button(dialog, text="Apply", command=apply_font,
                  bg=self.colors["surface0"], fg=self.colors["text"],
                  borderwidth=0, relief=tk.FLAT).pack(pady=10)

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
        self.apply_current_theme()

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
        self.status.configure(
            bg=self.colors.get("mantle", "#181825"),
            fg=self.colors.get("subtext0", "#a6adc8")
        )
        if hasattr(self, 'menu_frame'):
            self.menu_frame.configure(bg=self.colors.get("mantle", "#181825"))
            for child in self.menu_frame.winfo_children():
                if isinstance(child, tk.Menubutton):
                    child.configure(
                        bg=self.colors.get("mantle", "#181825"),
                        fg=self.colors.get("text", "#cdd6f4"),
                        activebackground=self.colors.get("surface0", "#313244"),
                        activeforeground=self.colors.get("blue", "#89b4fa")
                    )

def center_window(window, width=800, height=600):
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")

if __name__ == "__main__":
    root = tk.Tk()
    center_window(root, 800, 600)  # <-- replaces root.geometry("800x600")
    # Windows-specific theming fixes
    if platform.system() == "Windows":
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            messagebox.showerror("DPI Error", "Could not set DPI awareness for Windows.")
    # Set window icon cross-platform
    icon_path = os.path.expanduser(r"~\dev\zen.script\logo_zen_dot.ico")
    png_icon_path = os.path.expanduser(r"~\dev\zen.script\logo_zen_dot.png")
    try:
        if platform.system() == "Windows":
            if os.path.exists(icon_path):
                root.iconbitmap(default=icon_path)
            else:
                messagebox.showwarning("Icon Warning", "No ICO icon found for Windows platform.")
        else:
            if os.path.exists(png_icon_path):
                img = tk.PhotoImage(file=png_icon_path)
                root.iconphoto(True, img)
            else:
                messagebox.showwarning("Icon Warning", "No PNG icon found for non-Windows platform.")
    except Exception as e:
        messagebox.showerror("Icon Error", f"Icon error: {e}")
    editor = ZenScriptEditor(root)
    root.mainloop()