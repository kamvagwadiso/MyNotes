import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
import fitz  # PyMuPDF
import json
import os
import datetime
from datetime import datetime, timedelta
import calendar as cal_module
from PIL import Image, ImageTk
import webbrowser


class BookNoteTakingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("My Notes - Professional PDF Reader & Note-Taking App")
        self.root.geometry("1400x800")

        # Center the window on screen
        self.center_window()

        # Set application icon (if available)
        try:
            self.root.iconbitmap("assets/icons/notes_icon.ico")
        except:
            pass

        # Style configuration
        self.setup_styles()
        self.dark_mode = False
        self.current_view = "main"

        # Application state
        self.app_state = self.load_app_state()

        # Current book and notes data
        self.current_book_path = self.app_state.get('last_book_path')
        self.current_notes = {}
        self.current_page = self.app_state.get('last_page', 0)
        self.total_pages = 0
        self.book_title = "No Book Loaded"
        self.zoom_level = self.app_state.get('zoom_level', 1.5)

        # Text formatting
        self.current_font_family = "Segoe UI"
        self.current_font_size = 11
        self.current_font_color = "#2c3e50"
        self.current_bg_color = "#ffffff"

        # Notes navigation
        self.bookmarks = {}
        self.highlights = {}

        # Auto-save tracking
        self.notes_modified = False
        self.auto_save_triggered = False

        # Track usage for calendar
        self.usage_data = self.load_usage_data()

        # Create the main interface
        self.create_navbar()
        self.create_main_content()
        self.create_calendar_page()
        self.create_settings_page()
        self.create_about_page()  # New About page

        # Load last book if available
        if self.current_book_path and os.path.exists(self.current_book_path):
            self.load_book(self.current_book_path, restore_state=True)
        else:
            self.show_welcome_screen()
            self.show_main_view()

        # Auto-save setup
        self.auto_save_id = None
        self.setup_auto_save()

    def center_window(self):
        """Center the window on the screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Professional color scheme
        self.light_bg = "#ffffff"
        self.light_fg = "#2c3e50"
        self.light_accent = "#3498db"
        self.light_secondary = "#ecf0f1"
        self.light_border = "#bdc3c7"

        self.dark_bg = "#2c3e50"
        self.dark_fg = "#ecf0f1"
        self.dark_accent = "#3498db"
        self.dark_secondary = "#34495e"
        self.dark_border = "#7f8c8d"

        self.apply_light_theme()

    def apply_light_theme(self):
        self.style.configure(".", background=self.light_bg, foreground=self.light_fg)
        self.style.configure("TFrame", background=self.light_bg)
        self.style.configure("TLabel", background=self.light_bg, foreground=self.light_fg)
        self.style.configure("TButton", background=self.light_secondary, foreground=self.light_fg)
        self.style.configure("TMenubutton", background=self.light_secondary, foreground=self.light_fg)
        self.style.configure("TLabelframe", background=self.light_bg, foreground=self.light_accent)
        self.style.configure("TLabelframe.Label", background=self.light_bg, foreground=self.light_accent)
        self.style.map("TButton", background=[('active', self.light_accent)])

        self.root.configure(bg=self.light_bg)

    def apply_dark_theme(self):
        self.style.configure(".", background=self.dark_bg, foreground=self.dark_fg)
        self.style.configure("TFrame", background=self.dark_bg)
        self.style.configure("TLabel", background=self.dark_bg, foreground=self.dark_fg)
        self.style.configure("TButton", background=self.dark_secondary, foreground=self.dark_fg)
        self.style.configure("TMenubutton", background=self.dark_secondary, foreground=self.dark_fg)
        self.style.configure("TLabelframe", background=self.dark_bg, foreground=self.dark_accent)
        self.style.configure("TLabelframe.Label", background=self.dark_bg, foreground=self.dark_accent)
        self.style.map("TButton", background=[('active', self.dark_accent)])

        self.root.configure(bg=self.dark_bg)

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.apply_dark_theme()
            self.dark_mode_btn.config(text="☀️ Light Mode")
            self.update_text_widget_theme(dark_mode=True)
        else:
            self.apply_light_theme()
            self.dark_mode_btn.config(text="🌙 Dark Mode")
            self.update_text_widget_theme(dark_mode=False)

    def update_text_widget_theme(self, dark_mode):
        if dark_mode:
            self.notes_text.config(bg="#34495e", fg="#ecf0f1", insertbackground="white")
            self.pdf_canvas.config(bg="#2c3e50")
            if hasattr(self, 'bookmarks_list'):
                self.bookmarks_list.config(bg="#2c3e50", fg="#ecf0f1")
                self.highlights_list.config(bg="#2c3e50", fg="#ecf0f1")
        else:
            self.notes_text.config(bg="white", fg="#2c3e50", insertbackground="black")
            self.pdf_canvas.config(bg="white")
            if hasattr(self, 'bookmarks_list'):
                self.bookmarks_list.config(bg="white", fg="#2c3e50")
                self.highlights_list.config(bg="white", fg="#2c3e50")

    def create_navbar(self):
        navbar = ttk.Frame(self.root)
        navbar.pack(side=tk.TOP, fill=tk.X, padx=15, pady=10)

        # App title with professional styling
        title_label = ttk.Label(navbar, text="📚 My Notes - Professional Reader", font=("Segoe UI", 16, "bold"))
        title_label.pack(side=tk.LEFT, padx=10)

        # File menu with improved styling
        file_menu = ttk.Menubutton(navbar, text="📂 File", width=12)
        file_menu.pack(side=tk.LEFT, padx=5)
        file_menu.menu = tk.Menu(file_menu, tearoff=0, font=("Segoe UI", 10))
        file_menu["menu"] = file_menu.menu

        file_menu.menu.add_command(label="📄 Open PDF Book", command=self.new_book, accelerator="Ctrl+O")
        file_menu.menu.add_command(label="📁 Open Notes", command=self.open_notes)
        file_menu.menu.add_command(label="💾 Save Notes As", command=self.save_notes_as, accelerator="Ctrl+S")
        file_menu.menu.add_separator()
        file_menu.menu.add_command(label="ℹ️ About", command=self.show_about_view)
        file_menu.menu.add_separator()
        file_menu.menu.add_command(label="🚪 Exit", command=self.cleanup_and_exit, accelerator="Ctrl+Q")

        # Book title display with status
        self.title_label = ttk.Label(navbar, text="No book loaded", font=("Segoe UI", 10), foreground="#7f8c8d")
        self.title_label.pack(side=tk.LEFT, padx=20)

        self.status_label = ttk.Label(navbar, text="Ready", font=("Segoe UI", 9), foreground="#7f8c8d")
        self.status_label.pack(side=tk.LEFT, padx=5)

        # View buttons with better spacing
        view_frame = ttk.Frame(navbar)
        view_frame.pack(side=tk.RIGHT, padx=5)

        self.about_btn = ttk.Button(view_frame, text="ℹ️ About", command=self.show_about_view, width=10)
        self.about_btn.pack(side=tk.RIGHT, padx=5)

        self.settings_btn = ttk.Button(view_frame, text="⚙️ Settings", command=self.show_settings_view, width=10)
        self.settings_btn.pack(side=tk.RIGHT, padx=5)

        self.calendar_btn = ttk.Button(view_frame, text="📅 Calendar", command=self.show_calendar_view, width=10)
        self.calendar_btn.pack(side=tk.RIGHT, padx=5)

        self.notes_btn = ttk.Button(view_frame, text="📝 Reader", command=self.show_main_view, width=10)
        self.notes_btn.pack(side=tk.RIGHT, padx=5)

        self.dark_mode_btn = ttk.Button(view_frame, text="🌙 Dark Mode", command=self.toggle_dark_mode, width=12)
        self.dark_mode_btn.pack(side=tk.RIGHT, padx=5)

        # Bind keyboard shortcuts
        self.root.bind("<Control-o>", lambda e: self.new_book())
        self.root.bind("<Control-s>", lambda e: self.save_notes_as())
        self.root.bind("<Control-q>", lambda e: self.cleanup_and_exit())

    def show_welcome_screen(self):
        """Show welcome message when no book is loaded"""
        self.title_label.config(text="Welcome to My Notes! Click 'File → Open PDF Book' to get started")

    def create_main_content(self):
        self.main_frame = ttk.Frame(self.root)

        # Professional paned window with sash
        self.paned_window = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # PDF viewer frame with enhanced styling
        pdf_container = ttk.LabelFrame(self.paned_window, text="PDF Viewer")
        self.paned_window.add(pdf_container, weight=2)

        # Enhanced zoom controls
        control_frame = ttk.Frame(pdf_container)
        control_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))

        ttk.Label(control_frame, text="Zoom:", font=("Segoe UI", 10)).pack(side=tk.LEFT)

        zoom_btn_frame = ttk.Frame(control_frame)
        zoom_btn_frame.pack(side=tk.LEFT, padx=10)

        ttk.Button(zoom_btn_frame, text="➖", width=3, command=self.zoom_out).pack(side=tk.LEFT, padx=2)
        self.zoom_label = ttk.Label(zoom_btn_frame, text=f"{int(self.zoom_level * 100)}%",
                                    font=("Segoe UI", 10, "bold"), width=5)
        self.zoom_label.pack(side=tk.LEFT, padx=5)
        ttk.Button(zoom_btn_frame, text="➕", width=3, command=self.zoom_in).pack(side=tk.LEFT, padx=2)
        ttk.Button(zoom_btn_frame, text="Reset", command=self.reset_zoom).pack(side=tk.LEFT, padx=10)

        # Page info in control frame
        self.page_label = ttk.Label(control_frame, text="Page: 0 / 0", font=("Segoe UI", 10))
        self.page_label.pack(side=tk.RIGHT)

        # PDF canvas with professional styling
        canvas_frame = ttk.Frame(pdf_container)
        canvas_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL)
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL)

        self.pdf_canvas = tk.Canvas(canvas_frame, bg="white", relief="sunken", borderwidth=1,
                                    yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        v_scrollbar.config(command=self.pdf_canvas.yview)
        h_scrollbar.config(command=self.pdf_canvas.xview)

        self.pdf_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Notes container with formatting toolbar
        notes_container = ttk.LabelFrame(self.paned_window, text="Notes & Annotations")
        self.paned_window.add(notes_container, weight=1)

        # Create formatting toolbar
        self.create_formatting_toolbar(notes_container)

        # Notes content area with navigation
        notes_content_frame = ttk.Frame(notes_container)
        notes_content_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # Notes navigation sidebar
        self.create_notes_navigation(notes_content_frame)

        # Notes text area
        text_container = ttk.Frame(notes_content_frame)
        text_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Notes header with save status
        notes_header = ttk.Frame(text_container)
        notes_header.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))

        ttk.Label(notes_header, text="Page Notes", font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT)
        self.save_status_label = ttk.Label(notes_header, text="Saved", font=("Segoe UI", 9), foreground="green")
        self.save_status_label.pack(side=tk.RIGHT)

        # Enhanced notes text area
        text_frame = ttk.Frame(text_container)
        text_frame.pack(fill=tk.BOTH, expand=True)

        self.notes_text = tk.Text(text_frame, wrap=tk.WORD, font=(self.current_font_family, self.current_font_size),
                                  undo=True, maxundo=-1, spacing2=3, spacing3=3,
                                  relief="solid", borderwidth=1, padx=10, pady=10,
                                  selectbackground="#3498db")
        notes_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.notes_text.yview)
        self.notes_text.configure(yscrollcommand=notes_scrollbar.set)

        self.notes_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        notes_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Enhanced page navigation
        self.create_page_navigation()

        # Bind events
        self.notes_text.bind("<KeyPress>", self.on_notes_change)
        self.notes_text.bind("<ButtonRelease-1>", self.on_text_select)

        # Configure text tags
        self.apply_formatting()

    def create_formatting_toolbar(self, parent):
        toolbar = ttk.Frame(parent)
        toolbar.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))

        # Font family
        font_families = ["Segoe UI", "Arial", "Times New Roman", "Courier New", "Verdana", "Georgia"]
        self.font_family_var = tk.StringVar(value=self.current_font_family)
        font_combo = ttk.Combobox(toolbar, textvariable=self.font_family_var, values=font_families, width=12)
        font_combo.pack(side=tk.LEFT, padx=2)
        font_combo.bind('<<ComboboxSelected>>', self.change_font_family)

        # Font size
        font_sizes = ["8", "9", "10", "11", "12", "14", "16", "18", "20", "24"]
        self.font_size_var = tk.StringVar(value=str(self.current_font_size))
        size_combo = ttk.Combobox(toolbar, textvariable=self.font_size_var, values=font_sizes, width=5)
        size_combo.pack(side=tk.LEFT, padx=2)
        size_combo.bind('<<ComboboxSelected>>', self.change_font_size)

        # Formatting buttons with tooltips
        ttk.Button(toolbar, text="B", width=3, command=self.toggle_bold).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="I", width=3, command=self.toggle_italic).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="U", width=3, command=self.toggle_underline).pack(side=tk.LEFT, padx=2)

        # Heading styles
        ttk.Button(toolbar, text="H1", width=3, command=lambda: self.apply_heading(1)).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="H2", width=3, command=lambda: self.apply_heading(2)).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="H3", width=3, command=lambda: self.apply_heading(3)).pack(side=tk.LEFT, padx=2)

        # Color buttons
        ttk.Button(toolbar, text="🎨", width=3, command=self.choose_text_color).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🖍️", width=3, command=self.choose_highlight_color).pack(side=tk.LEFT, padx=2)

        # Navigation markers
        ttk.Button(toolbar, text="🔖", width=3, command=self.add_bookmark).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="📌", width=3, command=self.add_highlight).pack(side=tk.LEFT, padx=2)

        # Clear formatting
        ttk.Button(toolbar, text="Clear", width=5, command=self.clear_formatting).pack(side=tk.LEFT, padx=2)

    def create_notes_navigation(self, parent):
        # Notes navigation sidebar
        nav_frame = ttk.LabelFrame(parent, text="Navigation", width=200)
        nav_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        nav_frame.pack_propagate(False)

        # Bookmarks section
        ttk.Label(nav_frame, text="Bookmarks", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(10, 5), padx=10)

        bookmarks_frame = ttk.Frame(nav_frame)
        bookmarks_frame.pack(fill=tk.X, padx=10, pady=5)

        self.bookmarks_list = tk.Listbox(bookmarks_frame, height=6, font=("Segoe UI", 9))
        bookmarks_scrollbar = ttk.Scrollbar(bookmarks_frame, orient=tk.VERTICAL, command=self.bookmarks_list.yview)
        self.bookmarks_list.configure(yscrollcommand=bookmarks_scrollbar.set)
        self.bookmarks_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        bookmarks_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.bookmarks_list.bind("<<ListboxSelect>>", self.on_bookmark_select)

        # Highlights section
        ttk.Label(nav_frame, text="Highlights", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(10, 5), padx=10)

        highlights_frame = ttk.Frame(nav_frame)
        highlights_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.highlights_list = tk.Listbox(highlights_frame, font=("Segoe UI", 9))
        highlights_scrollbar = ttk.Scrollbar(highlights_frame, orient=tk.VERTICAL, command=self.highlights_list.yview)
        self.highlights_list.configure(yscrollcommand=highlights_scrollbar.set)
        self.highlights_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        highlights_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.highlights_list.bind("<<ListboxSelect>>", self.on_highlight_select)

    def create_page_navigation(self):
        nav_frame = ttk.Frame(self.main_frame, relief="solid", borderwidth=1)
        nav_frame.pack(fill=tk.X, padx=15, pady=10)

        # Navigation buttons with better styling
        nav_btn_frame = ttk.Frame(nav_frame)
        nav_btn_frame.pack(side=tk.LEFT, padx=10, pady=5)

        ttk.Button(nav_btn_frame, text="◀ Previous", command=self.prev_page, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(nav_btn_frame, text="Next ▶", command=self.next_page, width=10).pack(side=tk.LEFT, padx=5)

        # Page info with progress
        info_frame = ttk.Frame(nav_frame)
        info_frame.pack(side=tk.LEFT, padx=20)

        self.page_info_label = ttk.Label(info_frame, text="Page 0 of 0", font=("Segoe UI", 10, "bold"))
        self.page_info_label.pack(side=tk.TOP)

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(info_frame, variable=self.progress_var, maximum=100, length=150)
        self.progress_bar.pack(side=tk.TOP, pady=2)

        # Page jump controls
        jump_frame = ttk.Frame(nav_frame)
        jump_frame.pack(side=tk.RIGHT, padx=10, pady=5)

        ttk.Label(jump_frame, text="Go to page:").pack(side=tk.LEFT)
        self.page_entry = ttk.Entry(jump_frame, width=5, font=("Segoe UI", 10))
        self.page_entry.pack(side=tk.LEFT, padx=5)
        self.page_entry.bind("<Return>", self.go_to_page)
        ttk.Button(jump_frame, text="Go", command=self.go_to_page).pack(side=tk.LEFT, padx=2)

        # Keyboard shortcuts
        self.root.bind("<Left>", lambda e: self.prev_page())
        self.root.bind("<Right>", lambda e: self.next_page())
        self.root.bind("<Prior>", lambda e: self.prev_page())
        self.root.bind("<Next>", lambda e: self.next_page())
        self.root.bind("<Control-s>", lambda e: self.save_notes())
        self.root.bind("<Control-b>", lambda e: self.toggle_bold())
        self.root.bind("<Control-i>", lambda e: self.toggle_italic())

    def create_calendar_page(self):
        self.calendar_frame = ttk.Frame(self.root)

        # Enhanced calendar header
        cal_header = ttk.Frame(self.calendar_frame)
        cal_header.pack(fill=tk.X, padx=20, pady=15)

        ttk.Label(cal_header, text="📅 Reading Calendar", font=("Segoe UI", 20, "bold")).pack(side=tk.LEFT)

        # Professional stats display
        stats_frame = ttk.LabelFrame(cal_header, text="Reading Statistics")
        stats_frame.pack(side=tk.RIGHT)

        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack()

        self.days_used_label = ttk.Label(stats_grid, text="Days used: 0", font=("Segoe UI", 10))
        self.days_used_label.grid(row=0, column=0, sticky="w", padx=5, pady=2)

        self.current_streak_label = ttk.Label(stats_grid, text="Current streak: 0 days", font=("Segoe UI", 10))
        self.current_streak_label.grid(row=1, column=0, sticky="w", padx=5, pady=2)

        self.total_notes_label = ttk.Label(stats_grid, text="Total notes: 0", font=("Segoe UI", 10))
        self.total_notes_label.grid(row=0, column=1, sticky="w", padx=15, pady=2)

        self.avg_pages_label = ttk.Label(stats_grid, text="Avg pages/session: 0", font=("Segoe UI", 10))
        self.avg_pages_label.grid(row=1, column=1, sticky="w", padx=15, pady=2)

        # Calendar navigation
        nav_frame = ttk.Frame(self.calendar_frame)
        nav_frame.pack(fill=tk.X, padx=20, pady=10)

        ttk.Button(nav_frame, text="◀ Previous Month", command=self.prev_calendar_month).pack(side=tk.LEFT)

        self.month_year_label = ttk.Label(nav_frame, text="", font=("Segoe UI", 14, "bold"))
        self.month_year_label.pack(side=tk.LEFT, expand=True)

        ttk.Button(nav_frame, text="Next Month ▶", command=self.next_calendar_month).pack(side=tk.RIGHT)
        ttk.Button(nav_frame, text="Today", command=self.show_current_month).pack(side=tk.RIGHT, padx=10)

        # Calendar container
        cal_container = ttk.Frame(self.calendar_frame)
        cal_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.calendar_grid = tk.Frame(cal_container, bg=self.light_bg)
        self.calendar_grid.pack(fill=tk.BOTH, expand=True)

        self.current_calendar_date = datetime.now()

    def create_settings_page(self):
        self.settings_frame = ttk.Frame(self.root)

        # Settings header
        settings_header = ttk.Frame(self.settings_frame)
        settings_header.pack(fill=tk.X, padx=20, pady=15)

        ttk.Label(settings_header, text="⚙️ Settings", font=("Segoe UI", 20, "bold")).pack(side=tk.LEFT)

        # Settings content
        settings_content = ttk.Frame(self.settings_frame)
        settings_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Appearance settings
        appearance_frame = ttk.LabelFrame(settings_content, text="Appearance")
        appearance_frame.pack(fill=tk.X, pady=10)

        # Theme selection
        theme_frame = ttk.Frame(appearance_frame)
        theme_frame.pack(fill=tk.X, pady=5)
        ttk.Label(theme_frame, text="Theme:", font=("Segoe UI", 11)).pack(side=tk.LEFT)
        self.theme_var = tk.StringVar(value="Light" if not self.dark_mode else "Dark")
        ttk.Radiobutton(theme_frame, text="Light", variable=self.theme_var, value="Light",
                        command=self.apply_theme).pack(side=tk.LEFT, padx=20)
        ttk.Radiobutton(theme_frame, text="Dark", variable=self.theme_var, value="Dark",
                        command=self.apply_theme).pack(side=tk.LEFT, padx=20)

        # Font settings
        font_frame = ttk.Frame(appearance_frame)
        font_frame.pack(fill=tk.X, pady=5)
        ttk.Label(font_frame, text="Default Font:", font=("Segoe UI", 11)).pack(side=tk.LEFT)
        self.settings_font_family = ttk.Combobox(font_frame,
                                                 values=["Segoe UI", "Arial", "Times New Roman", "Courier New"],
                                                 width=15)
        self.settings_font_family.set(self.current_font_family)
        self.settings_font_family.pack(side=tk.LEFT, padx=10)
        self.settings_font_family.bind('<<ComboboxSelected>>', self.change_default_font)

        # Auto-save settings
        auto_save_frame = ttk.LabelFrame(settings_content, text="Auto-save")
        auto_save_frame.pack(fill=tk.X, pady=10)

        self.auto_save_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(auto_save_frame, text="Enable auto-save", variable=self.auto_save_var,
                        command=self.toggle_auto_save).pack(anchor="w")

        ttk.Label(auto_save_frame, text="Auto-save delay (seconds):", font=("Segoe UI", 10)).pack(anchor="w",
                                                                                                  pady=(10, 5))
        self.auto_save_delay_var = tk.StringVar(value="2")
        ttk.Entry(auto_save_frame, textvariable=self.auto_save_delay_var, width=10).pack(anchor="w")

        # Notes settings
        notes_frame = ttk.LabelFrame(settings_content, text="Notes")
        notes_frame.pack(fill=tk.X, pady=10)

        self.show_navigation_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(notes_frame, text="Show navigation sidebar", variable=self.show_navigation_var,
                        command=self.toggle_navigation).pack(anchor="w")

        # Reset settings
        reset_frame = ttk.Frame(settings_content)
        reset_frame.pack(fill=tk.X, pady=20)
        ttk.Button(reset_frame, text="Reset to Defaults", command=self.reset_settings).pack(side=tk.LEFT)
        ttk.Button(reset_frame, text="Save Settings", command=self.save_settings).pack(side=tk.RIGHT, padx=10)

    def create_about_page(self):
        """Create the About page with developer information"""
        self.about_frame = ttk.Frame(self.root)

        # About header
        about_header = ttk.Frame(self.about_frame)
        about_header.pack(fill=tk.X, padx=20, pady=20)

        ttk.Label(about_header, text="ℹ️ About My Notes", font=("Segoe UI", 24, "bold")).pack(side=tk.LEFT)

        # Main content area
        about_content = ttk.Frame(self.about_frame)
        about_content.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)

        # App info section
        app_info_frame = ttk.LabelFrame(about_content, text="Application Information", padding=20)
        app_info_frame.pack(fill=tk.X, pady=(0, 20))

        # App description
        desc_text = """My Notes is a professional PDF reader and note-taking application designed for students, researchers, and book lovers. 

Key Features:
• PDF viewing with smooth zoom controls
• Per-page note taking with auto-save
• Rich text formatting and highlighting
• Reading calendar with usage statistics
• Dark/Light mode for comfortable reading
• Bookmarks and highlights navigation
• Automatic state persistence"""

        desc_label = ttk.Label(app_info_frame, text=desc_text, font=("Segoe UI", 11), justify=tk.LEFT)
        desc_label.pack(anchor="w")

        # Developer section
        dev_frame = ttk.LabelFrame(about_content, text="Developer Information", padding=20)
        dev_frame.pack(fill=tk.X, pady=(0, 20))

        # Developer info with better formatting
        dev_info = """
👨‍💻 Developer: Kamva Gwadiso
🎂 Age: 22 years old
💻 Profession: Software Developer
📧 Contact: Available upon request

This application was developed with love and dedication to create 
the perfect reading companion. Every feature was carefully designed 
to enhance your reading experience and make note-taking effortless.

Development Date: October 1, 2025

Special Note:
This version of My Notes was specially created as a gift, 
embodying the perfect blend of functionality and elegance."""

        dev_label = ttk.Label(dev_frame, text=dev_info, font=("Segoe UI", 11), justify=tk.LEFT)
        dev_label.pack(anchor="w")

        # Technical info
        tech_frame = ttk.LabelFrame(about_content, text="Technical Information", padding=20)
        tech_frame.pack(fill=tk.X)

        tech_info = """
Built with: Python 3, Tkinter, PyMuPDF, Pillow
Version: 1.0.0
License: Personal Use

The application automatically saves your progress and maintains 
your reading statistics. All data is stored locally on your computer."""

        tech_label = ttk.Label(tech_frame, text=tech_info, font=("Segoe UI", 10), justify=tk.LEFT)
        tech_label.pack(anchor="w")

        # Close button
        button_frame = ttk.Frame(about_content)
        button_frame.pack(fill=tk.X, pady=20)

        ttk.Button(button_frame, text="Close", command=self.show_main_view, width=15).pack(side=tk.RIGHT)

    # Text formatting methods
    def change_font_family(self, event=None):
        self.current_font_family = self.font_family_var.get()
        self.apply_formatting()

    def change_font_size(self, event=None):
        try:
            self.current_font_size = int(self.font_size_var.get())
            self.apply_formatting()
        except ValueError:
            pass

    def change_default_font(self, event=None):
        self.current_font_family = self.settings_font_family.get()
        self.notes_text.config(font=(self.current_font_family, self.current_font_size))

    def toggle_bold(self):
        try:
            current_tags = self.notes_text.tag_names("sel.first")
            if "bold" in current_tags:
                self.notes_text.tag_remove("bold", "sel.first", "sel.last")
            else:
                self.notes_text.tag_add("bold", "sel.first", "sel.last")
        except tk.TclError:
            pass

    def toggle_italic(self):
        try:
            current_tags = self.notes_text.tag_names("sel.first")
            if "italic" in current_tags:
                self.notes_text.tag_remove("italic", "sel.first", "sel.last")
            else:
                self.notes_text.tag_add("italic", "sel.first", "sel.last")
        except tk.TclError:
            pass

    def toggle_underline(self):
        try:
            current_tags = self.notes_text.tag_names("sel.first")
            if "underline" in current_tags:
                self.notes_text.tag_remove("underline", "sel.first", "sel.last")
            else:
                self.notes_text.tag_add("underline", "sel.first", "sel.last")
        except tk.TclError:
            pass

    def apply_heading(self, level):
        try:
            # Remove existing heading tags
            for i in range(1, 4):
                self.notes_text.tag_remove(f"heading{i}", "sel.first", "sel.last")

            # Apply new heading
            self.notes_text.tag_add(f"heading{level}", "sel.first", "sel.last")
        except tk.TclError:
            pass

    def choose_text_color(self):
        color = colorchooser.askcolor(title="Choose text color", initialcolor=self.current_font_color)
        if color and color[1]:
            self.current_font_color = color[1]
            try:
                self.notes_text.tag_add("color", "sel.first", "sel.last")
            except tk.TclError:
                pass

    def choose_highlight_color(self):
        color = colorchooser.askcolor(title="Choose highlight color", initialcolor="#ffff00")
        if color and color[1]:
            try:
                self.notes_text.tag_add("highlight", "sel.first", "sel.last")
                self.notes_text.tag_config("highlight", background=color[1])
            except tk.TclError:
                pass

    def clear_formatting(self):
        try:
            for tag in ["bold", "italic", "underline", "heading1", "heading2", "heading3", "color", "highlight"]:
                self.notes_text.tag_remove(tag, "sel.first", "sel.last")
        except tk.TclError:
            pass

    def apply_formatting(self):
        # Configure text tags
        self.notes_text.tag_config("bold", font=(self.current_font_family, self.current_font_size, "bold"))
        self.notes_text.tag_config("italic", font=(self.current_font_family, self.current_font_size, "italic"))
        self.notes_text.tag_config("underline", font=(self.current_font_family, self.current_font_size, "underline"))
        self.notes_text.tag_config("heading1", font=("Segoe UI", 18, "bold"), foreground="#2c3e50")
        self.notes_text.tag_config("heading2", font=("Segoe UI", 16, "bold"), foreground="#34495e")
        self.notes_text.tag_config("heading3", font=("Segoe UI", 14, "bold"), foreground="#7f8c8d")
        self.notes_text.tag_config("color", foreground=self.current_font_color)
        self.notes_text.tag_config("highlight", background="#ffff00")

    def add_bookmark(self):
        try:
            text = self.notes_text.get("sel.first", "sel.last")
            if text.strip():
                bookmark_id = f"bookmark_{len(self.bookmarks)}"
                self.bookmarks[bookmark_id] = {
                    "text": text[:50] + "..." if len(text) > 50 else text,
                    "position": self.notes_text.index("sel.first")
                }
                self.update_bookmarks_list()
        except tk.TclError:
            messagebox.showinfo("Bookmark", "Please select text to bookmark")

    def add_highlight(self):
        try:
            text = self.notes_text.get("sel.first", "sel.last")
            if text.strip():
                highlight_id = f"highlight_{len(self.highlights)}"
                self.highlights[highlight_id] = {
                    "text": text[:50] + "..." if len(text) > 50 else text,
                    "position": self.notes_text.index("sel.first")
                }
                self.update_highlights_list()
        except tk.TclError:
            messagebox.showinfo("Highlight", "Please select text to highlight")

    def update_bookmarks_list(self):
        self.bookmarks_list.delete(0, tk.END)
        for bookmark_id, bookmark in self.bookmarks.items():
            self.bookmarks_list.insert(tk.END, f"📖 {bookmark['text']}")

    def update_highlights_list(self):
        self.highlights_list.delete(0, tk.END)
        for highlight_id, highlight in self.highlights.items():
            self.highlights_list.insert(tk.END, f"🖍️ {highlight['text']}")

    def on_bookmark_select(self, event):
        selection = self.bookmarks_list.curselection()
        if selection:
            bookmark_id = list(self.bookmarks.keys())[selection[0]]
            position = self.bookmarks[bookmark_id]["position"]
            self.notes_text.see(position)
            self.notes_text.focus_set()

    def on_highlight_select(self, event):
        selection = self.highlights_list.curselection()
        if selection:
            highlight_id = list(self.highlights.keys())[selection[0]]
            position = self.highlights[highlight_id]["position"]
            self.notes_text.see(position)
            self.notes_text.focus_set()

    def on_text_select(self, event):
        # Update formatting buttons based on current selection
        pass

    # Settings methods
    def apply_theme(self):
        if self.theme_var.get() == "Dark":
            self.dark_mode = True
        else:
            self.dark_mode = False
        self.toggle_dark_mode()

    def toggle_auto_save(self):
        if self.auto_save_var.get():
            self.setup_auto_save()
        else:
            if self.auto_save_id:
                self.root.after_cancel(self.auto_save_id)

    def toggle_navigation(self):
        # This would show/hide the navigation sidebar
        pass

    def reset_settings(self):
        self.theme_var.set("Light")
        self.auto_save_var.set(True)
        self.show_navigation_var.set(True)
        self.auto_save_delay_var.set("2")
        self.settings_font_family.set("Segoe UI")
        self.apply_theme()
        self.change_default_font()

    def save_settings(self):
        self.update_status("Settings saved", "green")

    # View management methods
    def show_main_view(self):
        self.current_view = "main"
        self.hide_all_views()
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.update_button_states()

    def show_calendar_view(self):
        self.current_view = "calendar"
        self.hide_all_views()
        self.calendar_frame.pack(fill=tk.BOTH, expand=True)
        self.update_calendar()
        self.update_stats()
        self.update_button_states()

    def show_settings_view(self):
        self.current_view = "settings"
        self.hide_all_views()
        self.settings_frame.pack(fill=tk.BOTH, expand=True)
        self.update_button_states()

    def show_about_view(self):
        self.current_view = "about"
        self.hide_all_views()
        self.about_frame.pack(fill=tk.BOTH, expand=True)
        self.update_button_states()

    def hide_all_views(self):
        self.main_frame.pack_forget()
        self.calendar_frame.pack_forget()
        self.settings_frame.pack_forget()
        self.about_frame.pack_forget()

    def update_button_states(self):
        self.notes_btn.config(state="normal")
        self.calendar_btn.config(state="normal")
        self.settings_btn.config(state="normal")
        self.about_btn.config(state="normal")

        if self.current_view == "main":
            self.notes_btn.config(state="disabled")
        elif self.current_view == "calendar":
            self.calendar_btn.config(state="disabled")
        elif self.current_view == "settings":
            self.settings_btn.config(state="disabled")
        elif self.current_view == "about":
            self.about_btn.config(state="disabled")

    # Calendar methods
    def show_current_month(self):
        self.current_calendar_date = datetime.now()
        self.update_calendar()

    def prev_calendar_month(self):
        self.current_calendar_date = self.current_calendar_date.replace(day=1) - timedelta(days=1)
        self.current_calendar_date = self.current_calendar_date.replace(day=1)
        self.update_calendar()

    def next_calendar_month(self):
        next_month = self.current_calendar_date.month + 1
        next_year = self.current_calendar_date.year
        if next_month > 12:
            next_month = 1
            next_year += 1
        self.current_calendar_date = self.current_calendar_date.replace(year=next_year, month=next_month, day=1)
        self.update_calendar()

    def update_calendar(self):
        for widget in self.calendar_grid.winfo_children():
            widget.destroy()

        self.month_year_label.config(text=self.current_calendar_date.strftime("%B %Y"))

        cal = cal_module.monthcalendar(self.current_calendar_date.year, self.current_calendar_date.month)

        # Enhanced day headers
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for i, day in enumerate(days):
            label = ttk.Label(self.calendar_grid, text=day[:3], font=("Segoe UI", 10, "bold"),
                              anchor="center", relief="solid", borderwidth=1)
            label.grid(row=0, column=i, sticky="nsew", padx=1, pady=1)

        # Enhanced day cells
        for week_num, week in enumerate(cal):
            for day_num, day in enumerate(week):
                if day == 0:
                    continue

                bg_color = self.light_secondary if not self.dark_mode else self.dark_secondary
                day_frame = tk.Frame(self.calendar_grid, relief="solid", borderwidth=1, bg=bg_color)
                day_frame.grid(row=week_num + 1, column=day_num, sticky="nsew", padx=1, pady=1)

                day_label = tk.Label(day_frame, text=str(day), font=("Segoe UI", 10, "bold"),
                                     bg=bg_color, fg=self.light_fg if not self.dark_mode else self.dark_fg)
                day_label.pack(anchor="nw", padx=5, pady=5)

                date_str = f"{self.current_calendar_date.year}-{self.current_calendar_date.month:02d}-{day:02d}"
                if date_str in self.usage_data:
                    usage_count = self.usage_data[date_str]
                    usage_text = "✓" if usage_count == 1 else f"{usage_count}✓"
                    usage_indicator = tk.Label(day_frame, text=usage_text, font=("Segoe UI", 9),
                                               fg="green", bg=bg_color)
                    usage_indicator.pack(anchor="ne", padx=5, pady=5)

                    highlight_color = "#d4edda" if not self.dark_mode else "#155724"
                    day_frame.config(bg=highlight_color)
                    day_label.config(bg=highlight_color)
                    usage_indicator.config(bg=highlight_color)

        for i in range(7):
            self.calendar_grid.columnconfigure(i, weight=1)
        for i in range(len(cal) + 1):
            self.calendar_grid.rowconfigure(i, weight=1)

    def update_stats(self):
        days_used = len(self.usage_data)
        self.days_used_label.config(text=f"Days used: {days_used}")

        # Calculate streak
        today = datetime.now()
        streak = 0
        current_date = today
        while True:
            date_str = current_date.strftime("%Y-%m-%d")
            if date_str in self.usage_data:
                streak += 1
                current_date -= timedelta(days=1)
            else:
                break
        self.current_streak_label.config(text=f"Current streak: {streak} days")

        # Additional stats
        total_notes = sum(1 for note in self.current_notes.values() if note.strip())
        self.total_notes_label.config(text=f"Total notes: {total_notes}")

        # Calculate average pages per session (simplified)
        if days_used > 0 and hasattr(self, 'doc'):
            avg_pages = self.total_pages // days_used
            self.avg_pages_label.config(text=f"Avg pages/session: {avg_pages}")

    def update_status(self, message, color="black"):
        self.status_label.config(text=message, foreground=color)
        self.root.after(3000, lambda: self.status_label.config(text="Ready", foreground="#7f8c8d"))

    def update_save_status(self, saved=True):
        if saved:
            self.save_status_label.config(text="✓ Saved", foreground="green")
        else:
            self.save_status_label.config(text="● Unsaved", foreground="orange")

    # PDF and notes methods
    def zoom_in(self):
        if self.zoom_level < 3.0:
            self.zoom_level = min(3.0, self.zoom_level + 0.1)
            self.update_zoom_display()
            if hasattr(self, 'doc'):
                self.show_page(self.current_page)

    def zoom_out(self):
        if self.zoom_level > 0.5:
            self.zoom_level = max(0.5, self.zoom_level - 0.1)
            self.update_zoom_display()
            if hasattr(self, 'doc'):
                self.show_page(self.current_page)

    def reset_zoom(self):
        self.zoom_level = 1.5
        self.update_zoom_display()
        if hasattr(self, 'doc'):
            self.show_page(self.current_page)

    def update_zoom_display(self):
        self.zoom_label.config(text=f"{int(self.zoom_level * 100)}%")

    def new_book(self):
        file_path = filedialog.askopenfilename(
            title="Select PDF Book",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if file_path:
            self.load_book(file_path)

    def open_notes(self):
        file_path = filedialog.askopenfilename(
            title="Open Notes File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            self.load_notes_file(file_path)

    def load_notes_file(self, file_path):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

            book_path = data.get('book_path')
            notes = data.get('notes', {})
            last_page = data.get('last_page', 0)

            if book_path and os.path.exists(book_path):
                self.load_book(book_path, restore_state=True)
                self.current_notes = notes
                self.show_page(last_page)
                self.update_status("Notes loaded successfully", "green")
            else:
                messagebox.showerror("Error", "The associated PDF file was not found.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load notes: {str(e)}")

    def load_book(self, file_path, restore_state=False):
        try:
            if hasattr(self, 'doc'):
                self.doc.close()

            self.current_book_path = file_path
            self.doc = fitz.open(file_path)
            self.total_pages = len(self.doc)
            self.book_title = os.path.splitext(os.path.basename(file_path))[0]
            self.title_label.config(text=self.book_title)

            # Initialize or load notes
            if not restore_state:
                self.current_notes = {str(i): "" for i in range(self.total_pages)}
                self.current_page = 0
            else:
                # Keep existing notes, fill missing pages
                for i in range(self.total_pages):
                    if str(i) not in self.current_notes:
                        self.current_notes[str(i)] = ""

            # Show the appropriate page
            page_to_show = self.current_page if restore_state else 0
            if page_to_show >= self.total_pages:
                page_to_show = self.total_pages - 1

            self.show_page(page_to_show)
            self.record_usage()
            self.update_status(f"Loaded: {self.book_title}", "green")

            # Save app state
            self.save_app_state()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load PDF: {str(e)}")

    def show_page(self, page_num):
        if not hasattr(self, 'doc') or page_num < 0 or page_num >= self.total_pages:
            return

        self.current_page = page_num

        # Update UI elements
        self.page_label.config(text=f"Page: {page_num + 1} / {self.total_pages}")
        self.page_info_label.config(text=f"Page {page_num + 1} of {self.total_pages}")
        self.progress_var.set(((page_num + 1) / self.total_pages) * 100)

        # Display PDF page
        page = self.doc[page_num]
        zoom_matrix = fitz.Matrix(self.zoom_level, self.zoom_level)
        pix = page.get_pixmap(matrix=zoom_matrix)

        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        self.page_image = ImageTk.PhotoImage(img)

        self.pdf_canvas.delete("all")
        self.pdf_canvas.create_image(0, 0, anchor=tk.NW, image=self.page_image)
        self.pdf_canvas.config(scrollregion=(0, 0, pix.width, pix.height))

        # Load notes for this page
        self.notes_text.delete(1.0, tk.END)
        notes = self.current_notes.get(str(page_num), "")
        self.notes_text.insert(1.0, notes)
        self.update_save_status(True)
        self.notes_modified = False

        # Clear navigation lists when changing pages
        self.bookmarks.clear()
        self.highlights.clear()
        self.update_bookmarks_list()
        self.update_highlights_list()

        # Save app state
        self.save_app_state()

    def prev_page(self):
        if self.current_page > 0:
            self.save_current_notes()
            self.show_page(self.current_page - 1)

    def next_page(self):
        if self.current_page < self.total_pages - 1:
            self.save_current_notes()
            self.show_page(self.current_page + 1)

    def go_to_page(self, event=None):
        try:
            page_num = int(self.page_entry.get()) - 1
            if 0 <= page_num < self.total_pages:
                self.save_current_notes()
                self.show_page(page_num)
            else:
                messagebox.showerror("Error", f"Page number must be between 1 and {self.total_pages}")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid page number")

    def on_notes_change(self, event=None):
        if not hasattr(self, 'doc'):
            return

        self.notes_modified = True
        self.update_save_status(False)
        self.record_usage()

        # Cancel previous auto-save
        if self.auto_save_id:
            self.root.after_cancel(self.auto_save_id)

        # Schedule auto-save after 2 seconds of inactivity
        self.auto_save_id = self.root.after(2000, self.auto_save_notes)

    def auto_save_notes(self):
        if self.notes_modified and hasattr(self, 'doc'):
            self.save_current_notes(silent=True)

    def save_current_notes(self, silent=False):
        if not hasattr(self, 'doc') or not self.notes_modified:
            return

        current_notes = self.notes_text.get(1.0, tk.END).strip()
        self.current_notes[str(self.current_page)] = current_notes

        self.notes_modified = False
        self.update_save_status(True)

        if not silent:
            self.update_status("Notes auto-saved", "green")

        # Save to file if we have a path
        if hasattr(self, 'notes_file_path'):
            self.save_notes(silent=True)

    def save_notes_as(self):
        if not hasattr(self, 'doc'):
            messagebox.showwarning("Warning", "No book is currently loaded.")
            return

        self.save_current_notes()

        file_path = filedialog.asksaveasfilename(
            title="Save Notes As",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if file_path:
            self.notes_file_path = file_path
            self.save_notes()

    def save_notes(self, silent=False):
        if not hasattr(self, 'doc'):
            return

        data = {
            'title': self.book_title,
            'book_path': self.current_book_path,
            'notes': self.current_notes,
            'last_page': self.current_page,
            'last_saved': datetime.now().isoformat(),
            'zoom_level': self.zoom_level
        }

        try:
            with open(self.notes_file_path, 'w') as f:
                json.dump(data, f, indent=2)

            if not silent:
                messagebox.showinfo("Success", "Notes saved successfully!")
                self.update_status("Notes saved", "green")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save notes: {str(e)}")

    def setup_auto_save(self):
        # Periodic backup save every 60 seconds
        self.root.after(60000, self.periodic_auto_save)

    def periodic_auto_save(self):
        if hasattr(self, 'doc') and self.notes_modified:
            self.save_current_notes(silent=True)
        self.root.after(60000, self.periodic_auto_save)

    def record_usage(self):
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in self.usage_data:
            self.usage_data[today] = 0
        self.usage_data[today] += 1
        self.save_usage_data()

        if self.current_view == "calendar":
            self.update_stats()

    def load_usage_data(self):
        try:
            data_dir = "data"
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
            usage_file = os.path.join(data_dir, "usage_data.json")
            if os.path.exists(usage_file):
                with open(usage_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {}

    def save_usage_data(self):
        try:
            data_dir = "data"
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
            usage_file = os.path.join(data_dir, "usage_data.json")
            with open(usage_file, 'w') as f:
                json.dump(self.usage_data, f, indent=2)
        except:
            pass

    def load_app_state(self):
        try:
            data_dir = "data"
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
            state_file = os.path.join(data_dir, "app_state.json")
            if os.path.exists(state_file):
                with open(state_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {}

    def save_app_state(self):
        try:
            data_dir = "data"
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
            state_file = os.path.join(data_dir, "app_state.json")
            state = {
                'last_book_path': self.current_book_path,
                'last_page': self.current_page,
                'zoom_level': self.zoom_level,
                'dark_mode': self.dark_mode,
                'last_saved': datetime.now().isoformat()
            }
            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except:
            pass

    def cleanup_and_exit(self):
        # Save everything before exiting
        if hasattr(self, 'doc'):
            self.save_current_notes(silent=True)
            self.save_app_state()
            self.doc.close()
        self.root.quit()

    def __del__(self):
        if hasattr(self, 'doc'):
            self.doc.close()


def main():
    root = tk.Tk()
    app = BookNoteTakingApp(root)

    # Handle window close event properly
    root.protocol("WM_DELETE_WINDOW", app.cleanup_and_exit)

    root.mainloop()


if __name__ == "__main__":
    main()