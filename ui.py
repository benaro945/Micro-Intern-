import csv
import json
import os
import sqlite3
import shutil
import uuid
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from datetime import datetime
from pathlib import Path

import database as db
from security import verify_password
from matching import calculate_match
from button_style import RoundedButton, RoundedMenubutton


APP_TITLE = "MicroIntern"
BG = "#f4f7fc"
PANEL = "#e7eefb"
CARD = "#ffffff"
TEXT = "#17243b"
MUTED = "#65748b"
ACCENT = "#3563e9"
SUCCESS = ACCENT
DANGER = "#d64545"
WARN = "#d99014"
BORDER = "#e0e7f2"
NAVY = "#18336b"

TRANSLATIONS = {
    "en": {
        "language": "Language", "brand_line": "MICRO PROJECTS. REAL EXPERIENCE.",
        "welcome_title": "Build your next opportunity.",
        "welcome_body": "Connect with growing businesses, take on meaningful projects, and turn your skills into real experience.",
        "step_learn": "LEARN", "step_build": "BUILD", "step_grow": "GROW",
        "step_learn_desc": "Find work that fits your skills.",
        "step_build_desc": "Work on real business projects.",
        "step_grow_desc": "Build your portfolio and earnings.",
        "sign_in": "Sign in", "register": "Register", "email": "Email",
        "password": "Password", "sign_in_button": "Sign in",
        "new_here": "New to MicroIntern?", "create_account": "Create an account",
        "browse_public": "Browse public tasks", "load_demo": "Load demo data",
        "demo_hint": "Try the demo accounts after loading demo data.",
        "student_dashboard": "Student Dashboard", "business_dashboard": "Business Dashboard",
        "logout": "Log out", "dashboard": "Dashboard", "browse_tasks": "Browse Tasks",
        "applications": "Applications", "profile": "Profile", "post_task": "Post Task",
        "my_tasks": "My Tasks", "rating": "Rating", "jobs_completed": "Jobs Completed",
        "total_earnings": "Total Earnings", "recommended_tasks": "Recommended Open Tasks",
        "tasks_posted": "Tasks Posted", "completed": "Completed", "total_paid": "Total Paid",
        "platform_revenue": "Platform Revenue", "recent_tasks": "Recent Tasks",
        "login_failed": "Invalid email or password.", "back": "Back",
        "create_account_title": "Create Account", "role": "Role",
        "name_business": "Name / Business Name", "create_account_button": "Create Account",
        "setup_title": "Tell us about you",
        "setup_subtitle": "This becomes your MicroInterns profile. Employers see it when you apply.",
        "headline": "Headline", "university": "University", "course": "Course",
        "graduation_year": "Graduation year", "location": "Location", "skills": "Skills",
        "skills_hint": "Comma-separated. These help match you to briefs.", "about": "About you",
        "portfolio": "Portfolio / website", "linkedin": "LinkedIn",
        "finish_setup": "Finish setup", "invalid_year": "Enter a valid graduation year or leave it blank.",
        "profile_saved": "Your profile is ready.",
    },
    "km": {
        "language": "ភាសា", "brand_line": "គម្រោងតូចៗ។ បទពិសោធន៍ពិត។",
        "welcome_title": "បង្កើតឱកាសបន្ទាប់របស់អ្នក។",
        "welcome_body": "ភ្ជាប់ទំនាក់ទំនងជាមួយអាជីវកម្មដែលកំពុងរីកចម្រើន ធ្វើគម្រោងមានន័យ និងបង្កើតបទពិសោធន៍ពិតពីជំនាញរបស់អ្នក។",
        "step_learn": "រៀន", "step_build": "អភិវឌ្ឍ", "step_grow": "រីកចម្រើន",
        "step_learn_desc": "ស្វែងរកការងារដែលត្រូវនឹងជំនាញ។",
        "step_build_desc": "ធ្វើការលើគម្រោងអាជីវកម្មពិត។",
        "step_grow_desc": "បង្កើតស្នាដៃ និងប្រាក់ចំណូល។",
        "sign_in": "ចូលគណនី", "register": "ចុះឈ្មោះ", "email": "អ៊ីមែល",
        "password": "ពាក្យសម្ងាត់", "sign_in_button": "ចូលគណនី",
        "new_here": "ថ្មីនៅ MicroIntern មែនទេ?", "create_account": "បង្កើតគណនី",
        "browse_public": "មើលការងារសាធារណៈ", "load_demo": "ផ្ទុកទិន្នន័យសាកល្បង",
        "demo_hint": "ផ្ទុកទិន្នន័យសាកល្បង ដើម្បីប្រើគណនីសាកល្បង។",
        "student_dashboard": "ផ្ទាំងគ្រប់គ្រងសិស្ស", "business_dashboard": "ផ្ទាំងគ្រប់គ្រងអាជីវកម្ម",
        "logout": "ចាកចេញ", "dashboard": "ផ្ទាំងគ្រប់គ្រង", "browse_tasks": "ស្វែងរកការងារ",
        "applications": "ពាក្យដាក់ស្នើ", "profile": "ប្រវត្តិរូប", "post_task": "បង្ហោះការងារ",
        "my_tasks": "ការងាររបស់ខ្ញុំ", "rating": "ការវាយតម្លៃ", "jobs_completed": "ការងារបានបញ្ចប់",
        "total_earnings": "ប្រាក់ចំណូលសរុប", "recommended_tasks": "ការងារបើកដែលណែនាំ",
        "tasks_posted": "ការងារបានបង្ហោះ", "completed": "បានបញ្ចប់", "total_paid": "បានបង់សរុប",
        "platform_revenue": "ចំណូលវេទិកា", "recent_tasks": "ការងារថ្មីៗ",
        "login_failed": "អ៊ីមែល ឬពាក្យសម្ងាត់មិនត្រឹមត្រូវទេ។", "back": "ត្រឡប់ក្រោយ",
        "create_account_title": "បង្កើតគណនី", "role": "តួនាទី",
        "name_business": "ឈ្មោះ / ឈ្មោះអាជីវកម្ម", "create_account_button": "បង្កើតគណនី",
        "setup_title": "ប្រាប់យើងអំពីអ្នក",
        "setup_subtitle": "នេះជាប្រវត្តិរូប MicroInterns របស់អ្នក។ និយោជកនឹងឃើញវានៅពេលអ្នកដាក់ពាក្យ។",
        "headline": "ចំណងជើង", "university": "សាកលវិទ្យាល័យ", "course": "មុខវិជ្ជា",
        "graduation_year": "ឆ្នាំបញ្ចប់ការសិក្សា", "location": "ទីតាំង", "skills": "ជំនាញ",
        "skills_hint": "បំបែកដោយសញ្ញាក្បៀស ដើម្បីជួយផ្គូផ្គងអ្នកនឹងការងារ។", "about": "អំពីអ្នក",
        "portfolio": "ស្នាដៃ / គេហទំព័រ", "linkedin": "LinkedIn",
        "finish_setup": "បញ្ចប់ការរៀបចំ", "invalid_year": "បញ្ចូលឆ្នាំបញ្ចប់ការសិក្សាត្រឹមត្រូវ ឬទុកឱ្យទទេ។",
        "profile_saved": "ប្រវត្តិរូបរបស់អ្នករួចរាល់ហើយ។",
    },
}


def money(value):
    return f"${float(value):,.2f}"


class MicroInternApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1280x820")
        self.minsize(1000, 680)
        self.configure(bg=BG)
        self.current_user = None
        self.language = "en"
        self._active_screen = "welcome"
        self.style = ttk.Style(self)
        self._fade_after_id = None
        self._motion_jobs = {}
        self._configure_style()
        db.init_db()
        self.show_welcome()

    def _configure_style(self):
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass
        self.style.configure("Treeview", background=CARD, foreground=TEXT,
                             rowheight=46, fieldbackground=CARD,
                             borderwidth=0, font=("Segoe UI", 10))
        self.style.map("Treeview", background=[("selected", "#dce8ff")],
                       foreground=[("selected", NAVY)])
        self.style.configure("Treeview.Heading", background=PANEL, foreground=NAVY,
                             font=("Segoe UI", 11, "bold"), padding=(12, 14), relief="flat")
        self.style.map("Treeview.Heading", background=[("active", "#d8e4fa")])
        self.style.configure("TCombobox", padding=8, fieldbackground=CARD, foreground=TEXT)
        self.style.configure("Vertical.TScrollbar", background="#cbd8ee", troughcolor=BG,
                             borderwidth=0, arrowsize=12)
        self.style.configure("TProgressbar", background=ACCENT, troughcolor="#e7efff", borderwidth=0)

    def t(self, key):
        return TRANSLATIONS[self.language].get(key, key)

    def _font(self, size=10, bold=False):
        family = "Khmer UI" if self.language == "km" else "Segoe UI"
        return (family, size, "bold") if bold else (family, size)

    def _language_picker(self, parent):
        picker = ttk.Combobox(parent, values=["English", "ខ្មែរ"],
                              state="readonly", width=11)
        picker.set("English" if self.language == "en" else "ខ្មែរ")
        picker.bind("<<ComboboxSelected>>", lambda _event: self.change_language(picker.get()))
        return picker

    def brand_logo(self, parent, background=BG, compact=False):
        width, height = (178, 42) if compact else (238, 56)
        scale = height / 56
        logo = tk.Canvas(parent, width=width, height=height, bg=background,
                         highlightthickness=0)

        def points(coords):
            return [coordinate * scale for coordinate in coords]

        left_mark = [4, 10, 11, 2, 27, 16, 27, 48, 18, 48, 18, 26, 10, 20, 10, 48, 4, 48]
        right_mark = [27, 16, 43, 2, 50, 10, 50, 48, 42, 48, 42, 18, 34, 26, 27, 21]
        logo.create_polygon(*points(left_mark), fill="#4140c9", outline="")
        logo.create_polygon(*points(right_mark), fill="#00b99a", outline="")
        logo.create_polygon(*points([27, 21, 34, 26, 39, 21, 39, 29, 33, 34]),
                            fill=background, outline="")
        text_x = 61 * scale
        logo.create_text(text_x, height * 0.52, text="MicroIntern",
                         anchor="w", fill=NAVY,
                         font=("Segoe UI", 16 if compact else 20, "bold"))
        return logo

    def change_language(self, selected):
        self.language = "km" if selected == "ខ្មែរ" else "en"
        if self._active_screen == "welcome":
            self.show_welcome()
        elif self._active_screen in ("login", "register"):
            if self._active_screen == "register":
                self.show_register()
            else:
                self.show_login()
        elif self._active_screen == "onboarding":
            self._setup_values = self._read_setup_values()
            self.show_student_setup()
        elif self.current_user and self.current_user["role"] == "student" and self._active_screen in ("tasks", "applications", "profile", "projects", "messages"):
            {"tasks": self.show_student_tasks, "applications": self.show_student_applications,
             "profile": self.show_student_profile, "projects": self.show_student_projects,
             "messages": self.show_messages}[self._active_screen]()
        elif self.current_user and self.current_user['role'] == 'business' and self._active_screen.startswith('business_'):
            routes = {'business_dashboard': self.show_business_dashboard, 'business_tasks': self.show_business_tasks,
                      'business_post': self.show_post_task, 'business_applicants': self.show_business_inbox,
                      'business_payments': self.show_business_invoices, 'business_messages': self.show_messages,
                      'business_profile': self.show_business_profile}
            routes[self._active_screen]()
        elif self._active_screen == "dashboard" and self.current_user:
            if self.current_user["role"] == "student":
                self.show_student_dashboard()
            else:
                self.show_business_dashboard()

    def clear(self):
        for job in getattr(self, '_motion_jobs', {}).values():
            self.after_cancel(job)
        self._motion_jobs = {}
        if getattr(self, '_messages_after_id', None):
            self.after_cancel(self._messages_after_id)
            self._messages_after_id = None
        if self._fade_after_id is not None:
            self.after_cancel(self._fade_after_id)
            self._fade_after_id = None
        for child in self.winfo_children():
            child.destroy()
        self._fade_in()

    def _fade_in(self):
        try:
            self.attributes("-alpha", 0.97)
        except tk.TclError:
            return

        steps = 12

        def reveal(step=1):
            try:
                self.attributes("-alpha", 0.97 + 0.03 * (1 - (1 - step / steps) ** 3))
            except tk.TclError:
                self._fade_after_id = None
                return
            if step < steps:
                self._fade_after_id = self.after(18, reveal, step + 1)
            else:
                self._fade_after_id = None

        self._fade_after_id = self.after(18, reveal)

    def _animate_color(self, widget, option, target, duration=160):
        key = (str(widget), option)
        previous = self._motion_jobs.pop(key, None)
        if previous:
            self.after_cancel(previous)
        start = self.winfo_rgb(widget.cget(option))
        end = self.winfo_rgb(target)
        steps = max(1, duration // 16)
        def tick(step=1):
            if not widget.winfo_exists():
                self._motion_jobs.pop(key, None)
                return
            progress = 1 - (1 - step / steps) ** 3
            color = '#' + ''.join(f'{round((a + (b-a)*progress)/257):02x}' for a,b in zip(start,end))
            widget.configure(**{option: color})
            if step < steps:
                self._motion_jobs[key] = self.after(16, tick, step + 1)
            else:
                self._motion_jobs.pop(key, None)
        tick()

    def _page_intro(self, parent, title, description):
        intro = tk.Frame(parent, bg=BG)
        intro.pack(fill='x', pady=(0, 18))
        tk.Label(intro, text=title, bg=BG, fg=NAVY, font=self._font(23, True)).pack(anchor='w')
        subtitle = tk.Label(intro, text=description, bg=BG, fg=MUTED,
                            font=self._font(10), justify='left', anchor='w')
        subtitle.pack(fill='x', pady=(6, 0))
        intro.bind('<Configure>', lambda event: subtitle.configure(wraplength=max(200,event.width)))

    def topbar(self, title, subtitle=""):
        bar = tk.Frame(self, bg=BG)
        bar.pack(fill="x", padx=28, pady=(16, 10))
        self.brand_logo(bar, background=BG, compact=True).pack(side="left", padx=(0, 15))
        title_group = tk.Frame(bar, bg=BG)
        title_group.pack(side="left", anchor="center")
        tk.Label(title_group, text=title, font=self._font(17, True),
                 fg=TEXT, bg=BG).pack(anchor="w")
        if subtitle:
            tk.Label(title_group, text=subtitle, font=self._font(9),
                     fg=MUTED, bg=BG).pack(anchor="w", pady=(2, 0))
        if self.current_user:
            self._profile_dropdown(bar).pack(side="right")
        if self._active_screen in ("dashboard", "register"):
            self._language_picker(bar).pack(side="right", padx=(0, 14))

    def button(self, parent, text, command, bg=ACCENT, width=18):
        return RoundedButton(parent, text=text, command=command, width=width,
                             font=self._font(10, True))

    def entry(self, parent, show=None):
        e = tk.Entry(parent, font=self._font(11), bg="#fbfcff", fg=TEXT,
                     relief="flat", show=show)
        e.configure(highlightthickness=1, highlightbackground=BORDER,
                    highlightcolor=ACCENT)
        return e

    def card(self, parent):
        card = tk.Frame(parent, bg=CARD, padx=24, pady=22,
                        highlightthickness=1, highlightbackground=BORDER)
        card.bind('<Enter>', lambda event: self._animate_color(card, 'highlightbackground', '#adc4ff'))
        card.bind('<Leave>', lambda event: self._animate_color(card, 'highlightbackground', BORDER))
        return card

    def show_welcome(self):
        self._auth_screen(welcome=True)

    def _auth_screen(self, welcome=False):
        self.clear()
        self._active_screen = "welcome" if welcome else "login"
        if welcome:
            self.current_user = None

        header = tk.Frame(self, bg=CARD, height=70)
        header.pack(fill="x")
        header.pack_propagate(False)
        brand = tk.Frame(header, bg=CARD)
        brand.pack(side="left", padx=28)
        self.brand_logo(brand, background=CARD, compact=True).pack(side="left")

        actions = tk.Frame(header, bg=CARD)
        actions.pack(side="right", padx=34)
        self._language_picker(actions).pack(side="left", padx=(0, 16))
        RoundedButton(actions, text=self.t("sign_in"), command=self.show_login,
                  bg=CARD, fg=ACCENT, activeforeground=NAVY, relief="flat",
                  cursor="hand2", font=self._font(10, True), padx=12).pack(side="left")
        self.button(actions, self.t("register"), self.show_register, width=10).pack(side="left", padx=(6, 0))

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=46, pady=34)
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=2, minsize=350)
        body.rowconfigure(0, weight=1)

        intro = tk.Frame(body, bg=BG)
        intro.grid(row=0, column=0, sticky="nsew", padx=(0, 46))
        tk.Label(intro, text=self.t("brand_line"), bg=BG, fg=ACCENT,
                 font=self._font(10, True)).pack(anchor="w", pady=(18, 14))
        tk.Label(intro, text=self.t("welcome_title"), bg=BG, fg=NAVY,
                 font=self._font(32, True), wraplength=550,
                 justify="left").pack(anchor="w")
        tk.Label(intro, text=self.t("welcome_body"), bg=BG, fg=MUTED,
                 font=self._font(12), wraplength=540, justify="left"
                 ).pack(anchor="w", pady=(15, 22))

        steps = tk.Frame(intro, bg=BG)
        steps.pack(fill="x", pady=(12, 24))
        for index, (title, description, tint) in enumerate((
                ("step_learn", "step_learn_desc", "#e7efff"),
                ("step_build", "step_build_desc", "#e4f5f2"),
                ("step_grow", "step_grow_desc", "#fff2df"))):
            tile = tk.Frame(steps, bg=CARD, padx=14, pady=13,
                            highlightthickness=1, highlightbackground=BORDER)
            tile.pack(side="left", fill="both", expand=True, padx=(0 if index == 0 else 10, 0))
            tk.Label(tile, text=f"0{index + 1}", bg=tint, fg=NAVY,
                     font=self._font(10, True), padx=8, pady=4).pack(anchor="w")
            tk.Label(tile, text=self.t(title), bg=CARD, fg=NAVY,
                     font=self._font(11, True)).pack(anchor="w", pady=(11, 4))
            tk.Label(tile, text=self.t(description), bg=CARD, fg=MUTED,
                     font=self._font(9), wraplength=150, justify="left"
                     ).pack(anchor="w")

        tk.Label(intro, text=self.t("demo_hint"), bg=BG, fg=MUTED,
                 font=self._font(9)).pack(anchor="w", pady=(4, 8))
        links = tk.Frame(intro, bg=BG)
        links.pack(anchor="w")
        RoundedButton(links, text=self.t("browse_public"), command=self.show_public_tasks,
                  bg=BG, fg=ACCENT, activeforeground=NAVY, relief="flat",
                  cursor="hand2", font=self._font(10, True)).pack(side="left", padx=(0, 14))
        RoundedButton(links, text=self.t("load_demo"), command=self.load_demo,
                  bg=BG, fg=MUTED, activeforeground=NAVY, relief="flat",
                  cursor="hand2", font=self._font(10)).pack(side="left")

        form = self.card(body)
        form.grid(row=0, column=1, sticky="nsew", padx=(0, 3), pady=20)
        form.configure(padx=28, pady=30)
        tk.Label(form, text=self.t("sign_in"), bg=CARD, fg=NAVY,
                 font=self._font(22, True)).pack(anchor="w", pady=(0, 7))
        tk.Label(form, text=self.t("email"), fg=TEXT, bg=CARD,
                 font=self._font(10, True)).pack(anchor="w", pady=(0, 6))
        email = self.entry(form)
        email.pack(fill="x", ipady=9)
        tk.Label(form, text=self.t("password"), fg=TEXT, bg=CARD,
                 font=self._font(10, True)).pack(anchor="w", pady=(16, 6))
        pwd = self.entry(form, show="*")
        pwd.pack(fill="x", ipady=9)

        def do_login():
            user = db.get_user_by_email(email.get())
            if not user or not verify_password(pwd.get(), user["password_hash"]):
                messagebox.showerror(self.t("sign_in"), self.t("login_failed"))
                return
            self.current_user = user
            if user["role"] == "student":
                self.show_student_dashboard()
            else:
                self.show_business_dashboard()

        self.button(form, self.t("sign_in_button"), do_login, width=24).pack(fill="x", pady=(24, 15))
        register_line = tk.Frame(form, bg=CARD)
        register_line.pack(anchor="center")
        tk.Label(register_line, text=self.t("new_here"), bg=CARD, fg=MUTED,
                 font=self._font(9)).pack(side="left")
        RoundedButton(register_line, text=self.t("create_account"), command=self.show_register,
                  bg=CARD, fg=ACCENT, activeforeground=NAVY, relief="flat",
                  cursor="hand2", font=self._font(9, True)).pack(side="left", padx=3)

    def load_demo(self):
        try:
            created = db.seed_demo_data()
            if created:
                messagebox.showinfo("Demo Data", "Demo accounts and tasks were created.")
            else:
                messagebox.showinfo("Demo Data", "Demo data already exists.")
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def show_login(self):
        self._auth_screen()

    def show_register(self):
        self.clear()
        self._active_screen = "register"
        self.topbar(self.t("create_account_title"))
        box = self.card(self)
        box.pack(pady=38)

        labels = [self.t("role"), self.t("name_business"), self.t("email"), self.t("password")]
        for i, label in enumerate(labels):
            tk.Label(box, text=label, fg=TEXT, bg=CARD).grid(row=i*2, column=0, sticky="w", pady=(9,4))

        role = ttk.Combobox(box, values=["student", "business"], state="readonly")
        role.set("student")
        role.grid(row=1, column=0, sticky="ew", ipady=5)

        name = self.entry(box); name.grid(row=3, column=0, ipadx=130, ipady=7)
        email = self.entry(box); email.grid(row=5, column=0, ipadx=130, ipady=7)
        pwd = self.entry(box, show="*"); pwd.grid(row=7, column=0, ipadx=130, ipady=7)

        def register():
            if not name.get().strip() or "@" not in email.get() or len(pwd.get()) < 6:
                messagebox.showerror("Invalid Input",
                                     "Enter a name, valid email, and password of at least 6 characters.")
                return
            try:
                uid = db.create_user(role.get(), name.get(), email.get(), pwd.get())
            except sqlite3.IntegrityError:
                messagebox.showerror("Email Used", "An account with this email already exists.")
                return
            user = db.get_user(uid)
            self.current_user = user
            if user["role"] == "student":
                self._setup_values = {}
                self.show_student_setup()
            else:
                messagebox.showinfo("Welcome", "Account created successfully.")
                self.show_business_profile()

        self.button(box, self.t("create_account_button"), register, bg=ACCENT, width=24).grid(row=8, column=0, pady=20)
        self.button(box, self.t("back"), self.show_welcome, bg=NAVY, width=24).grid(row=9, column=0)

    def show_public_tasks(self):
        self.clear()
        self.topbar("Open Micro-Projects", "Public view")
        frame = tk.Frame(self, bg=BG)
        frame.pack(fill="both", expand=True, padx=28, pady=10)

        cols = ("id","title","business","category","budget","deadline")
        tree = ttk.Treeview(frame, columns=cols, show="headings")
        widths = [60,280,180,150,100,120]
        for c,w in zip(cols,widths):
            tree.heading(c, text=c.title())
            tree.column(c, width=w, anchor="w")
        for t in db.list_open_tasks():
            tree.insert("", "end", values=(t["id"],t["title"],t["business_name"],
                                           t["category"],money(t["budget"]),t["deadline"]))
        tree.pack(fill="both", expand=True)
        self.button(self, self.t("back"), self.show_welcome, bg=NAVY).pack(pady=15)

    def _avatar_image(self, path, size):
        image = tk.PhotoImage(master=self, file=path)
        factor = max(1, (max(image.width(), image.height()) + size - 1) // size)
        return image.subsample(factor, factor)

    def _profile_dropdown(self, parent):
        user = self.current_user
        student = db.get_student(user["id"]) if user["role"] == "student" else None
        command = self.show_student_profile if student else self.show_business_profile
        button = RoundedMenubutton(parent, text=f"{user['name']}  ?", compound="left",
                               bg="#edf3ff", fg=TEXT, relief="flat", padx=10, pady=7,
                               font=self._font(10, True), cursor="hand2")
        image = None
        if student and student.get("avatar_path"):
            try:
                image = self._avatar_image(student["avatar_path"], 32)
            except (tk.TclError, OSError):
                pass
        if image is None:
            image = tk.PhotoImage(master=self, width=32, height=32)
            image.put(ACCENT, to=(0, 0, 32, 32))
            image.put("#ffffff", to=(12, 6, 20, 14))
            image.put("#ffffff", to=(8, 18, 24, 27))
        button.configure(image=image)
        button.image = image
        menu = tk.Menu(button, tearoff=False, bg=CARD, fg=TEXT)
        menu.add_command(label=user['email'], state="disabled")
        menu.add_separator()
        menu.add_command(label="User information", command=command)
        if student:
            menu.add_command(label="Portfolio / CV / Skills", command=command)
        menu.add_separator()
        menu.add_command(label=self.t("logout"), command=self.logout)
        button.configure(menu=menu)
        return button

    def _student_shell(self, active, title=""):
        self._active_screen = active
        header = tk.Frame(self, bg=CARD, padx=24, pady=16,
                          highlightthickness=1, highlightbackground=BORDER)
        header.pack(fill="x")
        self.brand_logo(header, CARD, compact=True).pack(side="left")
        self._profile_dropdown(header).pack(side="right", padx=(14, 0))
        self._language_picker(header).pack(side="right")
        shell = tk.Frame(self, bg=BG)
        shell.pack(fill="both", expand=True)
        sidebar = tk.Frame(shell, bg="#303e4e", width=210)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        tk.Label(sidebar, text="STUDENT WORKSPACE", bg="#303e4e", fg="#a5b2bf",
                 font=self._font(8, True)).pack(anchor="w", padx=18, pady=(24, 15))
        items = [("dashboard", "dashboard", self.show_student_dashboard),
                 ("tasks", "browse_tasks", self.show_student_tasks),
                 ("applications", "applications", self.show_student_applications),
                 ("projects", "My Projects", self.show_student_projects),
                 ("messages", "Messages", self.show_messages),
                 ("profile", "profile", self.show_student_profile)]
        symbols = {'dashboard': '01', 'tasks': '02', 'applications': '03', 'projects': '04', 'messages': '05', 'profile': '06'}
        for key, label, command in items:
            color = ACCENT if key == active else "#303e4e"
            button = RoundedButton(sidebar, text=f"{symbols[key]}   {self.t(label)}", command=command,
                               anchor="w", bg=color, fg="white", relief="flat",
                               padx=18, pady=14, font=self._font(10, key == active), cursor="hand2")
            button.set_selected(key == active)
            button.pack(fill="x", padx=10, pady=4)
        footer = tk.Frame(sidebar, bg="#303e4e", padx=18, pady=20)
        footer.pack(side='bottom', fill='x')
        tk.Label(footer, text='MICRO PROJECTS. REAL EXPERIENCE.', bg="#303e4e", fg='#bac9dd',
                 font=self._font(8, True), wraplength=170, justify='left').pack(anchor='w')
        tk.Label(footer, text='Build skills. Deliver work. Grow.', bg="#303e4e", fg='#93a9c4',
                 font=self._font(8), wraplength=170, justify='left').pack(anchor='w', pady=(6,0))
        main = tk.Frame(shell, bg=BG, padx=24, pady=22)
        main.pack(side="left", fill="both", expand=True)
        if title:
            descriptions = {
                'tasks': 'Find meaningful work from growing businesses. Explore opportunities tailored to your skills.',
                'applications': 'Track your applications and take your next step toward real project experience.',
                'projects': 'Your delivery hub: manage milestones, submit work, and collaborate with your client.',
                'messages': 'Keep project questions, decisions, and feedback together in one place.',
                'profile': 'Show businesses what you can do with your skills, experience, and selected work.'}
            self._page_intro(main, title, descriptions.get(active, 'Your next opportunity starts here.'))
        return main

    def _business_shell(self, active, title='', subtitle=''):
        self._active_screen = 'business_' + active
        business = db.get_business(self.current_user['id'])
        shell = tk.Frame(self, bg=BG)
        shell.pack(fill='both', expand=True)
        sidebar = tk.Frame(shell, bg='#1e202b', width=204)
        sidebar.pack(side='left', fill='y')
        sidebar.pack_propagate(False)
        tk.Label(sidebar, text='MICROINTERN', bg='#1e202b', fg='white',
                 font=self._font(13, True), pady=21).pack(anchor='w', padx=17)
        tk.Label(sidebar, text='BUSINESS WORKSPACE', bg='#1e202b', fg='#8d97a5',
                 font=self._font(8, True)).pack(anchor='w', padx=17, pady=(4, 12))
        items = [('dashboard', 'Dashboard', self.show_business_dashboard),
                 ('tasks', 'Products / Tasks', self.show_business_tasks),
                 ('post', 'Store / Post Task', self.show_post_task),
                 ('messages', 'Messages', self.show_messages),
                 ('applicants', 'Applicants', self.show_business_inbox),
                 ('payments', 'Invoices / Payments', self.show_business_invoices),
                 ('profile', 'Settings / Profile', self.show_business_profile)]
        self._business_nav_buttons = {}
        for key, label, command in items:
            selected = key == active
            color = ACCENT if selected else '#1e202b'
            button = RoundedButton(sidebar, text='   ' + label, command=command,
                               anchor='w', relief='flat', cursor='hand2', bg=color,
                               fg='white' if selected else '#b3bdc8',
                               font=self._font(10, selected), padx=8, pady=12)
            button.set_selected(selected)
            button.pack(fill='x', padx=10, pady=4)
            self._business_nav_buttons[key] = button
        footer = tk.Frame(sidebar, bg='#1e202b', padx=17, pady=20)
        footer.pack(side='bottom', fill='x')
        tk.Label(footer, text=business['name'], bg='#1e202b', fg='white',
                 font=self._font(10, True), wraplength=165).pack(anchor='w')
        tk.Label(footer, text='Business account', bg='#1e202b', fg='#8d97a5',
                 font=self._font(8)).pack(anchor='w', pady=(4,0))
        main = tk.Frame(shell, bg=BG)
        main.pack(side='left', fill='both', expand=True)
        header = tk.Frame(main, bg=CARD, padx=22, pady=14,
                          highlightthickness=1, highlightbackground=BORDER)
        header.pack(fill='x')
        greeting = tk.Frame(header, bg=CARD)
        greeting.pack(side='left')
        tk.Label(greeting, text='MICROINTERN BUSINESS', bg=CARD, fg=MUTED,
                 font=self._font(8, True)).pack(anchor='w')
        tk.Label(greeting, text=f"Welcome back, {business['name']}", bg=CARD, fg=TEXT,
                 font=self._font(15, True)).pack(anchor='w', pady=(3,0))
        actions = tk.Frame(header, bg=CARD)
        actions.pack(side='right')
        self._profile_dropdown(actions).pack(side='right', padx=(12,0))
        self._language_picker(actions).pack(side='right', padx=(8,0))
        RoundedButton(actions, text='Messages', command=self.show_messages, bg=CARD,
                  fg=MUTED, relief='flat', cursor='hand2', font=self._font(9, True)).pack(side='right')
        content = tk.Frame(main, bg=BG, padx=20, pady=16)
        content.pack(fill='both', expand=True)
        if title:
            self._page_intro(content, title, subtitle)
        return content, actions

    def show_student_dashboard(self):
        self.clear()
        self._active_screen = "dashboard"
        s = db.get_student(self.current_user["id"])
        fin = db.student_financials(s["id"])
        applications = db.list_student_applications(s["id"])
        main = self._student_shell("dashboard")
        background = BG
        tk.Label(main, text=f"Welcome back, {s['name']}", bg=background, fg=TEXT,
                 font=self._font(26, True)).pack(anchor="w")
        tk.Label(main, text="Your projects, progress, and next opportunity.", bg=background,
                 fg=MUTED, font=self._font(10)).pack(anchor="w", pady=(3, 16))
        row = tk.Frame(main, bg=background)
        row.pack(fill="x")
        stats = [
            (self.t("total_earnings"), money(fin["earnings"]), "#4169e1", "Project earnings"),
            (self.t("jobs_completed"), str(s["jobs_completed"]), "#577ce6", "Completed projects"),
            (self.t("applications"), str(len(applications)), "#398cda", "Submitted applications"),
            (self.t("rating"), f"{s['rating']:.1f}/5" if s["rating"] else "New", "#79a4ed", "Your reputation"),
        ]
        for index, (title, value, color, caption) in enumerate(stats):
            c = tk.Frame(row, bg=color, padx=16, pady=16)
            c.grid(row=0, column=index, sticky="nsew", padx=(0, 12 if index < 3 else 0))
            row.columnconfigure(index, weight=1, uniform="metrics")
            tk.Label(c, text=value, fg="white", bg=color, font=self._font(21, True)).pack(anchor="w")
            tk.Label(c, text=title.upper(), fg="white", bg=color, font=self._font(9, True)).pack(anchor="w", pady=(3, 10))
            tk.Label(c, text=caption, fg="white", bg=color, font=self._font(8)).pack(anchor="w")
        charts = tk.Frame(main, bg=background)
        charts.pack(fill="x", pady=18)
        earnings = self.card(charts)
        earnings.pack(side="left", fill="both", expand=True, padx=(0, 16))
        tk.Label(earnings, text="Earnings Overview · Last 6 Months", bg=CARD, fg=TEXT,
                 font=self._font(11, True)).pack(anchor="w")
        chart = tk.Canvas(earnings, bg=CARD, height=150, highlightthickness=0)
        chart.pack(fill="x", pady=(8, 0))
        with db.connect() as conn:
            payments = conn.execute("""SELECT substr(tr.created_at,1,7) month,
                SUM(tr.student_earnings) amount FROM transactions tr JOIN tasks t ON t.id=tr.task_id
                WHERE t.assigned_student_id=? GROUP BY month""", (s['id'],)).fetchall()
        totals = {p['month']: p['amount'] for p in payments}
        current = datetime.now()
        months = []
        for offset in range(5, -1, -1):
            ordinal = current.year * 12 + current.month - 1 - offset
            months.append(datetime(ordinal // 12, ordinal % 12 + 1, 1))
        chart_motion = {'progress': 0.0}
        def draw_earnings(event=None):
            chart.delete("all")
            width = chart.winfo_width() if event is None else event.width
            values = [totals.get(month.strftime('%Y-%m'), 0) for month in months]
            maximum = max(max(values), 1)
            for index, (month, value) in enumerate(zip(months, values)):
                x = 40 + index * (width - 70) / 6
                bar_width = max(10, (width - 70) / 9)
                y = 110 - value / maximum * 75 * chart_motion["progress"]
                chart.create_rectangle(x, y, x + bar_width, 111, fill="#4169e1", outline="")
                chart.create_text(x + bar_width / 2, y - 10, text=money(value), fill=MUTED, font=self._font(8))
                chart.create_text(x + bar_width / 2, 130, text=month.strftime('%b'), fill=MUTED, font=self._font(8))
        chart.bind("<Configure>", draw_earnings)
        def animate_chart(step=0):
            if not chart.winfo_exists():
                return
            chart_motion['progress'] = 1 - (1 - step / 24) ** 3
            draw_earnings()
            if step < 24:
                self._motion_jobs[(str(chart), 'entrance')] = self.after(16, animate_chart, step + 1)
            else:
                self._motion_jobs.pop((str(chart), 'entrance'), None)
        self._motion_jobs[(str(chart), 'entrance')] = self.after(40, animate_chart)
        status_card = self.card(charts)
        status_card.pack(side="right", fill="both")
        tk.Label(status_card, text="Application Status", bg=CARD, fg=TEXT,
                 font=self._font(11, True)).pack(anchor="w")
        donut = tk.Canvas(status_card, bg=CARD, width=230, height=158, highlightthickness=0)
        donut.pack()
        start = 90
        for status, color in [("Pending", "#398cda"), ("Accepted", "#4169e1"), ("Rejected", "#79a4ed")]:
            count = sum(a['status'] == status for a in applications)
            extent = 360 * count / max(len(applications), 1)
            if extent:
                donut.create_arc(12, 15, 140, 143, start=start, extent=extent, fill=color, outline=CARD)
            start += extent
            y = 40 + ["Pending", "Accepted", "Rejected"].index(status) * 30
            donut.create_text(150, y, text=f"{status}: {count}", anchor="w", fill=color, font=self._font(8))
        if not applications:
            donut.create_oval(12, 15, 140, 143, fill=BORDER, outline="")
        donut.create_oval(38, 41, 114, 117, fill=CARD, outline="")
        donut.create_text(76, 79, text=str(len(applications)), fill=TEXT, font=self._font(20, True))
        tasks_panel = tk.Frame(main, bg=CARD, padx=14, pady=12)
        tasks_panel.pack(fill="both", expand=True)
        tk.Label(tasks_panel, text=self.t("recommended_tasks"), fg=TEXT, bg=CARD,
                 font=self._font(15, True)).pack(anchor="w", pady=(0, 10))
        self._student_task_table(recommended=True, parent=tasks_panel)

    def _student_task_table(self, recommended=False, parent=None):
        s = db.get_student(self.current_user["id"])
        tasks = db.list_open_tasks()
        scored = [(calculate_match(s,t)["total"], t) for t in tasks]
        scored.sort(key=lambda x: x[0], reverse=True)

        frame = tk.Frame(parent or self, bg=CARD if parent else BG)
        frame.pack(fill="both", expand=True, padx=0 if parent else 28, pady=5)
        cols = ("id","title","business","category","budget","match")
        tree = ttk.Treeview(frame, columns=cols, show="headings", height=5 if recommended else 11)
        widths = [40,230,130,120,80,70] if parent else [55,300,180,150,90,90]
        for c,w in zip(cols,widths):
            tree.heading(c, text=c.title())
            tree.column(c, width=w, anchor="w")
        data = scored[:8] if recommended else scored
        for score,t in data:
            tree.insert("", "end", values=(t["id"],t["title"],t["business_name"],
                                           t["category"],money(t["budget"]),f"{score:.1f}%"))
        tree.pack(fill="both", expand=True)
        scrollbar = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        scrollbar.pack(fill="x")
        tree.configure(xscrollcommand=scrollbar.set)
        if not data:
            tk.Label(frame, text="No open tasks yet. Check back soon.", bg=CARD if parent else BG,
                     fg=MUTED, font=self._font(10)).pack(pady=8)

        def open_selected():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Select Task", "Select a task first.")
                return
            task_id = int(tree.item(sel[0], "values")[0])
            self.show_task_detail(task_id)

        tree.bind("<Double-1>", lambda _event: open_selected())
        self.button(frame, "View Task", open_selected, bg="#398cda").pack(pady=10)

    def _scroll_page(self, parent):
        canvas = tk.Canvas(parent, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.configure(yscrollcommand=scrollbar.set)
        content = tk.Frame(canvas, bg=BG)
        window = canvas.create_window((0, 0), window=content, anchor="nw")
        content.bind("<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda event: canvas.itemconfigure(window, width=event.width))
        def wheel(event):
            canvas.yview_scroll(-int(event.delta / 120), "units")
        def route_wheel(event):
            if canvas.winfo_exists() and str(event.widget).startswith(str(content)):
                wheel(event)
        binding = self.bind("<MouseWheel>", route_wheel, add="+")
        canvas.bind("<Destroy>", lambda event: self.unbind("<MouseWheel>", binding) if event.widget == canvas else None)
        return content

    def show_student_tasks(self):
        self.clear()
        main = self._student_shell("tasks", "Discover your next project")
        student = db.get_student(self.current_user["id"])
        tasks = db.list_open_tasks()
        tasks.sort(key=lambda task: calculate_match(student, task)["total"], reverse=True)
        controls = tk.Frame(main, bg=BG)
        controls.pack(fill="x", pady=(0, 12))
        query = tk.StringVar()
        search = self.entry(controls)
        search.configure(textvariable=query)
        search.pack(side="left", fill="x", expand=True, ipady=7, padx=(0, 10))
        category = tk.StringVar(value="All categories")
        categories = ["All categories"] + sorted({task['category'] for task in tasks})
        picker = ttk.Combobox(controls, textvariable=category, values=categories, state="readonly", width=22)
        picker.pack(side="right")
        content = self._scroll_page(main)
        tk.Label(content, text="Getting started", bg=BG, fg=NAVY,
                 font=self._font(14, True)).pack(anchor="w", pady=(0, 10))
        banners = tk.Frame(content, bg=BG)
        banners.pack(fill="x", pady=(0, 20))
        for index, (title, subtitle, command) in enumerate([
            ("Find your best match", "Explore projects ranked for your skills", lambda: reset_filters()),
            ("Build a standout profile", "Add skills, a CV, and your best work", self.show_student_profile),
        ]):
            banner = RoundedButton(banners, text=title + "\n\n" + subtitle, command=command,
                               bg=ACCENT if index == 0 else NAVY, fg="white", relief="flat",
                               anchor="w", justify="left", padx=20, pady=22,
                               font=self._font(11, True), cursor="hand2", wraplength=320)
            banner.grid(row=0, column=index, sticky="nsew", padx=(0, 12 if index == 0 else 0))
            banners.columnconfigure(index, weight=1, uniform="banners")
        heading = tk.Label(content, text="Open opportunities", bg=BG, fg=NAVY, font=self._font(14, True))
        heading.pack(anchor="w", pady=(0, 10))
        grid = tk.Frame(content, bg=BG)
        grid.pack(fill="x")
        cards = []
        state = {"columns": 0}

        def open_card(event, task_id):
            self.show_task_detail(task_id)

        def make_card(task):
            card = tk.Frame(grid, bg=CARD, highlightthickness=1, highlightbackground=BORDER,
                            cursor="hand2")
            card.task_id = task['id']
            visual = tk.Canvas(card, height=105, bg="#e1ebff", highlightthickness=0)
            visual.pack(fill="x")
            visual.create_oval(180, -50, 340, 110, fill="#bdd1ff", outline="")
            visual.create_oval(230, 35, 345, 150, fill="#93b5ff", outline="")
            visual.create_text(18, 34, text=task['category'].upper(), anchor="w", fill=NAVY, font=self._font(10, True))
            visual.create_text(18, 75, text=money(task['budget']) + " / project", anchor="w", fill=ACCENT, font=self._font(17, True))
            body = tk.Frame(card, bg=CARD, padx=14, pady=14)
            body.pack(fill="both", expand=True)
            company = tk.Frame(body, bg=CARD)
            company.pack(fill="x", pady=(0, 10))
            initials = ''.join(part[0] for part in task['business_name'].split()[:2]).upper()
            tk.Label(company, text=initials, bg=ACCENT, fg="white", width=3, pady=7,
                     font=self._font(10, True)).pack(side="left", padx=(0, 8))
            tk.Label(company, text=task['business_name'], bg=CARD, fg=TEXT,
                     font=self._font(10, True), wraplength=170, anchor="w").pack(anchor="w")
            tk.Label(company, text="? Unverified", bg=CARD, fg=MUTED, font=self._font(8)).pack(anchor="w")
            title = tk.Label(body, text=task['title'], bg=CARD, fg=TEXT, font=self._font(12, True),
                            justify="left", anchor="nw", height=3)
            title.pack(fill="x")
            summary = ' '.join(task['description'].split())
            summary = summary[:135] + ('?' if len(summary) > 135 else '')
            description = tk.Label(body, text=summary, bg=CARD, fg=MUTED, justify="left", anchor="nw",
                                   height=4, font=self._font(9))
            description.pack(fill="x", pady=(3, 8))
            tk.Label(body, text=f"{task['applicants_count']} applicants  ?  ? No reviews yet", bg=CARD,
                     fg=MUTED, anchor="w", font=self._font(8)).pack(fill="x")
            tk.Label(body, text=f"Posted {task['created_at'][:10]}", bg=CARD, fg=MUTED,
                     anchor="w", font=self._font(8)).pack(fill="x", pady=(5, 8))
            tk.Label(body, text=f"{calculate_match(student, task)['total']:.0f}% skill & preference match  ?",
                     bg="#edf3ff", fg=ACCENT, pady=7, font=self._font(9, True)).pack(fill="x")
            def bind_click(widget):
                widget.bind("<Button-1>", lambda event, tid=task['id']: open_card(event, tid))
                for child in widget.winfo_children():
                    bind_click(child)
            bind_click(card)
            card.bind("<Enter>", lambda event: card.configure(highlightbackground=ACCENT))
            card.bind("<Leave>", lambda event: card.configure(highlightbackground=BORDER))
            card.configure(takefocus=True)
            card.bind("<Return>", lambda event: self.show_task_detail(task['id']))
            card.bind("<space>", lambda event: self.show_task_detail(task['id']))
            card.bind("<Configure>", lambda event: [label.configure(wraplength=max(140, event.width - 30)) for label in (title, description)])
            return card

        def layout(event=None):
            columns = max(1, min(4, grid.winfo_width() // 270))
            if columns == state['columns'] and event is not None:
                return
            for col in range(4):
                grid.columnconfigure(col, weight=1 if col < columns else 0, uniform="task-cards")
            for index, card in enumerate(cards):
                card.grid(row=index // columns, column=index % columns, sticky="nsew",
                          padx=(0, 12), pady=(0, 14))
            state['columns'] = columns

        def filter_cards(*args):
            for child in grid.winfo_children():
                child.destroy()
            cards.clear()
            term = query.get().strip().casefold()
            selected = [task for task in tasks if (category.get() == 'All categories' or task['category'] == category.get())
                        and term in ' '.join(str(task[key]) for key in ('title', 'description', 'business_name', 'required_skills')).casefold()]
            heading.configure(text=f"Open opportunities ? {len(selected)}")
            for task in selected:
                cards.append(make_card(task))
            if not cards:
                tk.Label(grid, text="No matching tasks. Try another search or category.", bg=BG,
                         fg=MUTED, pady=30, font=self._font(11)).grid(row=0, column=0, columnspan=4)
            layout()

        def reset_filters():
            category.set('All categories')
            query.set('')
            search.focus_set()

        query.trace_add('write', filter_cards)
        category.trace_add('write', filter_cards)
        grid.bind('<Configure>', layout)
        filter_cards()

    def show_task_detail(self, task_id):
        self.clear()
        task = db.get_task(task_id)
        if task is None:
            messagebox.showwarning("Task unavailable", "This task is no longer available.")
            self.show_student_tasks()
            return
        student = db.get_student(self.current_user["id"])
        score = calculate_match(student, task)

        main = self._student_shell("tasks", f"Task #{task_id}")
        detail_content = self._scroll_page(main)
        hero = tk.Frame(detail_content, bg="#e7efff", padx=26, pady=24,
                        highlightthickness=1, highlightbackground=BORDER)
        hero.pack(fill="x", pady=(0, 14))
        tk.Label(hero, text=task["category"].upper(), bg="#e7efff", fg=ACCENT,
                 font=self._font(10, True)).pack(anchor="w", pady=(0, 10))
        project_title = tk.Label(hero, text=task["title"], bg="#e7efff", fg=NAVY,
                                 font=self._font(28, True), justify="left", anchor="w")
        project_title.pack(fill="x")
        tk.Label(hero, text=f"{task['business_name']}  /  {task['experience']} project",
                 bg="#e7efff", fg=MUTED, font=self._font(11)).pack(anchor="w", pady=(10, 0))
        hero.bind("<Configure>", lambda event: project_title.configure(
            wraplength=max(200, event.width - 52)))
        box = self.card(detail_content)
        box.pack(fill="both", expand=True, pady=8)

        left = tk.Frame(box, bg=CARD); left.pack(side="left", fill="both", expand=True, padx=(0,30))
        right = tk.Frame(box, bg="#edf3ff", padx=22, pady=22,
                 highlightthickness=1, highlightbackground=BORDER)
        right.pack(side="right", anchor="n")

        details = [
            ("Business", task["business_name"]),
            ("Category", task["category"]),
            ("Budget", money(task["budget"])),
            ("Deadline", task["deadline"]),
            ("Required skills", task["required_skills"]),
            ("Schedule", task["schedule"] or "Flexible"),
            ("Experience", task["experience"]),
            ("Project brief", task["description"]),
            ("Deliverables", task.get("deliverables") or "Not specified. Confirm the expected files and milestones with the business before starting."),
            ("Business contact", task["business_email"]),
            ("Posted", task["created_at"][:10]),
            ("Applicants", str(task["applicants_count"])),
            ("Budget breakdown", f"Project budget: {money(task['budget'])} | Platform fee (10%): {money(round(task['budget'] * 0.1, 2))} | Your earnings: {money(task['budget'] - round(task['budget'] * 0.1, 2))}"),
        ]
        for k,v in details:
            tk.Label(left, text=k.upper(), fg=NAVY, bg=CARD,
                     font=self._font(15, True)).pack(anchor="w", pady=(18, 7))
            tk.Label(left, text=str(v), fg=TEXT, bg=CARD, wraplength=600,
                     justify="left", font=self._font(11)).pack(anchor="w", pady=(0, 12))
            tk.Frame(left, bg=BORDER, height=1).pack(fill="x")
        left.bind("<Configure>", lambda event: [
            label.configure(wraplength=max(160, event.width - 10))
            for label in left.winfo_children() if isinstance(label, tk.Label)])

        tk.Label(right, text="YOUR MATCH", fg=NAVY, bg="#edf3ff",
                 font=self._font(13, True)).pack()
        tk.Label(right, text=f"{score['total']:.1f}%", fg=ACCENT, bg="#edf3ff",
                 font=("Segoe UI",30,"bold")).pack(pady=8)
        for key in ["skill","budget","availability","experience","rating"]:
            tk.Label(right, text=f"{key.title():12} {score[key]:5.1f}%",
                     fg=TEXT, bg="#edf3ff", font=("Consolas",10)).pack(anchor="w")

        def apply():
            try:
                db.apply_to_task(task_id, student["id"], score["total"])
                messagebox.showinfo("Applied", "Your application was submitted.")
                self.show_student_applications()
            except sqlite3.IntegrityError:
                messagebox.showwarning("Already Applied", "You already applied for this task.")

        already_applied = any(a['task_id'] == task_id for a in db.list_student_applications(student['id']))
        action = self.button(right, "Applied" if already_applied else "Apply Now", apply, bg=ACCENT, width=16)
        action.pack(pady=(25,7))
        if already_applied or task['status'] != 'Open':
            action.configure(state="disabled", text="Applied" if already_applied else "Applications closed")
        self.button(right, 'Message Business', lambda: self.show_messages(task_id, student['id']), width=18).pack(pady=8)
        self.button(right, self.t("back"), self.show_student_tasks, bg=NAVY, width=16).pack()

    def show_student_applications(self):
        self.clear()
        main = self._student_shell("applications", "My Applications")
        frame = tk.Frame(main, bg=BG)
        frame.pack(fill="both", expand=True, padx=28, pady=10)

        cols = ("id","task","business","budget","match","application","task_status")
        tree = ttk.Treeview(frame, columns=cols, show="headings")
        for c,w in zip(cols,[55,260,180,90,90,110,110]):
            tree.heading(c,text=c.replace("_"," ").title()); tree.column(c,width=w,anchor="w")
        applications = db.list_student_applications(self.current_user["id"])
        by_id = {str(a["id"]): a for a in applications}
        for a in applications:
            tree.insert("", "end", values=(a["id"],a["title"],a["business_name"],
                                           money(a["budget"]),f"{a['match_score']:.1f}%",
                                           a["status"],a["task_status"]))
        tree.pack(fill="both", expand=True)


        def open_project():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Select project", "Choose an application to view its project.")
                return
            application = by_id[str(tree.item(selected[0], 'values')[0])]
            if application['status'] == 'Accepted':
                self.show_project_workspace(application['task_id'])
            else:
                self.show_task_detail(application['task_id'])
        tree.bind('<Double-1>', lambda event: open_project())
        self.button(frame, "Open Project / Submit Work", open_project, width=28).pack(pady=12)
        tk.Label(frame, text="Accepted projects: submit your work, read feedback, and track payment.",
                 bg=BG, fg=MUTED, font=self._font(9)).pack()

    def show_student_projects(self):
        self.clear()
        main = self._student_shell('projects', 'My Projects')
        tk.Label(main, text='Manage delivery, collaborate with businesses, and track your earnings.',
                 bg=BG, fg=MUTED, font=self._font(11)).pack(anchor='w', pady=(0, 15))
        content = self._scroll_page(main)
        projects = [a for a in db.list_student_applications(self.current_user['id']) if a['status'] == 'Accepted']
        if not projects:
            tk.Label(content, text='Your accepted projects will appear here.', bg=BG, fg=MUTED,
                     font=self._font(13), pady=30).pack()
            self.button(content, 'Find a Project', self.show_student_tasks).pack()
        for project in projects:
            card = self.card(content)
            card.pack(fill='x', pady=(0, 12))
            tk.Label(card, text=project['title'], bg=CARD, fg=NAVY, font=self._font(18, True),
                     wraplength=600, justify='left').pack(anchor='w')
            tk.Label(card, text=f"{project['business_name']}  |  {project['task_status']}  |  Budget {money(project['budget'])}",
                     bg=CARD, fg=MUTED, font=self._font(11)).pack(anchor='w', pady=10)
            actions = tk.Frame(card, bg=CARD)
            actions.pack(fill='x')
            self.button(actions, 'Open / Submit Work', lambda tid=project['task_id']: self.show_project_workspace(tid),
                        width=23).pack(side='left')
            self.button(actions, 'Message Business', lambda tid=project['task_id']: self.show_messages(tid, self.current_user['id']),
                        width=21).pack(side='left', padx=10)

    def show_messages(self, task_id=None, student_id=None):
        user_id = self.current_user['id']
        student_view = self.current_user['role'] == 'student'
        if task_id is not None:
            student_id = user_id if student_view else student_id
            try:
                db.get_project_messages(task_id, student_id, user_id)
            except ValueError as exc:
                messagebox.showerror('Messages', str(exc))
                return
        self.clear()
        if student_view:
            main = self._student_shell('messages', 'Messages')
        else:
            main, _ = self._business_shell('messages', 'Messages', 'Project conversations inside MicroIntern')
        conversation_panel = tk.Frame(main, bg=CARD, width=240, padx=12, pady=12,
                                      highlightthickness=1, highlightbackground=BORDER)
        conversation_panel.pack(side='left', fill='y', padx=(0, 14))
        conversation_panel.pack_propagate(False)
        tk.Label(conversation_panel, text='Conversations', bg=CARD, fg=NAVY,
                 font=self._font(14, True)).pack(anchor='w', pady=(0, 10))
        conversations = tk.Listbox(conversation_panel, bg=CARD, fg=TEXT, relief='flat',
                                   selectbackground=ACCENT, selectforeground='white',
                                   font=self._font(10), exportselection=False)
        conversations.pack(fill='both', expand=True)
        panel = tk.Frame(main, bg=CARD, padx=16, pady=14,
                         highlightthickness=1, highlightbackground=BORDER)
        panel.pack(side='left', fill='both', expand=True)
        title = tk.Label(panel, text='Select a conversation', bg=CARD, fg=NAVY,
                         font=self._font(17, True), anchor='w', justify='left', wraplength=480)
        title.pack(fill='x', pady=(0, 8))
        tk.Label(panel, text='Discuss requirements, delivery, and feedback here.', bg=CARD,
                 fg=MUTED, font=self._font(10)).pack(anchor='w', pady=(0, 12))
        transcript = tk.Text(panel, bg='#f7f9ff', fg=TEXT, font=self._font(11), wrap='word',
                             relief='flat', padx=14, pady=12, state='disabled', height=12)
        scroll = ttk.Scrollbar(panel, command=transcript.yview)
        scroll.pack(side='right', fill='y')
        transcript.configure(yscrollcommand=scroll.set)
        transcript.pack(fill='both', expand=True)
        transcript.tag_configure('mine', foreground=ACCENT, font=self._font(10, True))
        transcript.tag_configure('other', foreground=NAVY, font=self._font(10, True))
        composer = tk.Text(panel, height=3, bg='#edf3ff', fg=TEXT, wrap='word',
                           font=self._font(11), relief='flat', padx=10, pady=8)
        composer.pack(fill='x', pady=(12, 8))
        state = {'task': task_id, 'student': student_id, 'rows': [], 'signature': None}
        def refresh():
            rows = db.list_conversations(user_id)
            state['rows'] = rows
            conversations.delete(0, 'end')
            for index, row in enumerate(rows):
                name = row['business_name'] if student_view else row['student_name']
                unread = f" ({row['unread']} new)" if row['unread'] else ''
                conversations.insert('end', f"{name} / {row['title']}{unread}")
                if row['task_id'] == state['task'] and row['student_id'] == state['student']:
                    conversations.selection_set(index)
            if state['task'] is not None:
                messages = db.get_project_messages(state['task'], state['student'], user_id)
                task = db.get_task(state['task'])
                counterpart = task['business_name'] if student_view else db.get_user(state['student'])['name']
                title.configure(text=f"{counterpart}\n{task['title']}")
                signature = [(m['id'], m['read_at']) for m in messages]
                if state['signature'] != signature:
                    transcript.configure(state='normal')
                    transcript.delete('1.0', 'end')
                    if not messages:
                        transcript.insert('end', 'Start the conversation. Ask a question about this project.\n')
                    for message in messages:
                        mine = message['sender_id'] == user_id
                        transcript.insert('end', f"{'You' if mine else message['sender_name']}  /  {message['created_at'].replace('T', ' ')}\n", 'mine' if mine else 'other')
                        transcript.insert('end', message['body'] + '\n\n')
                    transcript.configure(state='disabled')
                    transcript.see('end')
                    state['signature'] = signature
                composer.configure(state='normal')
                send.configure(state='normal')
            else:
                composer.configure(state='disabled')
                send.configure(state='disabled')
        def select(event):
            selection = conversations.curselection()
            if selection:
                row = state['rows'][selection[0]]
                state.update(task=row['task_id'], student=row['student_id'], signature=None)
                composer.delete('1.0', 'end')
                refresh()
        conversations.bind('<<ListboxSelect>>', select)
        def send_message():
            try:
                db.send_project_message(state['task'], state['student'], user_id, composer.get('1.0', 'end-1c'))
                composer.delete('1.0', 'end')
                refresh()
            except ValueError as exc:
                messagebox.showerror('Message', str(exc))
        send = self.button(panel, 'Send Message', send_message, width=20)
        send.pack(anchor='e')
        if not db.list_conversations(user_id) and task_id is None:
            title.configure(text='No conversations yet')
            transcript.configure(state='normal')
            transcript.insert('end', 'Students: open a task or My Projects and choose Message Business.\nBusinesses: incoming project conversations appear here.')
            transcript.configure(state='disabled')
        def poll():
            try:
                refresh()
            finally:
                self._messages_after_id = self.after(3000, poll)
        refresh()
        self._messages_after_id = self.after(3000, poll)

    def show_project_workspace(self, task_id):
        task = db.get_task(task_id)
        if not task:
            messagebox.showwarning("Project", "Project not found.")
            return
        student_view = self.current_user['role'] == 'student'
        authorized = task['assigned_student_id'] == self.current_user['id'] if student_view else task['business_id'] == self.current_user['id']
        if not authorized:
            messagebox.showerror("Project", "You do not have access to this project.")
            return
        self.clear()
        if student_view:
            main = self._student_shell('projects', 'Project Workspace')
        else:
            main, _ = self._business_shell('tasks', 'Review Project', 'Review delivery, request changes, or approve completed work.')
        content = self._scroll_page(main)
        toolbar = tk.Frame(content, bg=BG)
        toolbar.pack(fill='x', pady=(0, 12))
        self.button(toolbar, 'Project Messages', lambda: self.show_messages(task_id, task['assigned_student_id']), width=22).pack(side='right')
        tk.Label(toolbar, text='DELIVERY & COLLABORATION', bg=BG, fg=ACCENT,
                 font=self._font(10, True)).pack(side='left')
        brief = self.card(content)
        brief.pack(fill='x', pady=(0, 12))
        tk.Label(brief, text=task['title'], bg=CARD, fg=NAVY, font=self._font(25, True), wraplength=650).pack(anchor='w', pady=(0, 12))
        payment = db.project_payment(task_id)
        earnings = round(task['budget'] - round(task['budget'] * .1, 2), 2)
        for label, value in [('Business', task['business_name']), ('Status', task['status']),
                             ('Deadline', task['deadline']), ('Project brief', task['description']),
                             ('Deliverables', task.get('deliverables') or 'Confirm deliverables with the business.'),
                             
                             ('Payment', f"Recorded earnings: {money(payment['student_earnings'])}" if payment else f"Awaiting approval ? Expected earnings: {money(earnings)}")]:
            tk.Label(brief, text=f"{label}: {value}", bg=CARD, fg=TEXT, justify='left',
                     wraplength=650, font=self._font(10)).pack(anchor='w', pady=4)
        tk.Label(brief, text="Payments are simulated in this app; approval records earnings, with a 10% platform fee.",
                 bg=CARD, fg=MUTED, wraplength=650, font=self._font(9)).pack(anchor='w', pady=6)
        if task['review_feedback']:
            tk.Label(brief, text="Business feedback: " + task['review_feedback'], bg='#edf3ff', fg=ACCENT,
                     wraplength=650, justify='left', padx=10, pady=10).pack(fill='x', pady=8)
        submission = self.card(content)
        submission.pack(fill='x', pady=(0, 12))
        tk.Label(submission, text='Submit your deliverables', bg=CARD, fg=NAVY, font=self._font(19, True)).pack(anchor='w')
        tk.Label(submission, text='Include the final files or a working link, and explain what you delivered. Your client can approve it or request changes.',
                 bg=CARD, fg=MUTED, wraplength=650, justify='left', font=self._font(10)).pack(anchor='w', pady=(8, 12))
        tk.Label(submission, text='Project link (optional when attaching a file)', bg=CARD, fg=MUTED).pack(anchor='w', pady=(10, 4))
        link = self.entry(submission)
        link.pack(fill='x', ipady=6)
        link.insert(0, task['submission_url'] or '')
        tk.Label(submission, text='Delivery notes / what is included', bg=CARD, fg=MUTED).pack(anchor='w', pady=(10, 4))
        notes = tk.Text(submission, height=4, wrap='word', bg='#fbfcff', fg=TEXT, font=self._font(10))
        notes.pack(fill='x')
        notes.insert('1.0', task['submission_notes'] or '')
        attachment = tk.StringVar(value=task['submission_path'] or '')
        tk.Label(submission, textvariable=attachment, bg='#edf3ff', fg=ACCENT, padx=10, pady=10, wraplength=650).pack(anchor='w', pady=8)
        if task['submitted_at']:
            tk.Label(submission, text='Last submitted: ' + task['submitted_at'], bg=CARD, fg=MUTED).pack(anchor='w')
        editable = student_view and task['status'] in ('Assigned', 'In Progress', 'Changes Requested')
        def choose_file():
            path = filedialog.askopenfilename(title='Attach project deliverable', filetypes=[('All files', '*.*')])
            if path:
                attachment.set(path)
        def submit():
            path = attachment.get()
            try:
                if not path and not link.get().strip():
                    raise ValueError('Attach a file or provide a project link.')
                if path and not os.path.isfile(path):
                    raise ValueError('The selected file is missing. Choose it again.')
                if path and path != task['submission_path']:
                    folder = Path(db.DB_PATH).parent / 'project_submissions'
                    folder.mkdir(exist_ok=True)
                    target = folder / f"{task_id}_{uuid.uuid4().hex}_{Path(path).name}"
                    shutil.copy2(path, target)
                    path = str(target)
                db.submit_project(task_id, self.current_user['id'], notes.get('1.0', 'end-1c'), link.get(), path)
                messagebox.showinfo('Submitted', 'Your work was sent to the business for review.')
                self.show_project_workspace(task_id)
            except (ValueError, OSError) as exc:
                messagebox.showerror('Submission', str(exc))
        if editable:
            self.button(submission, 'Attach File', choose_file).pack(anchor='w', pady=8)
            self.button(submission, 'Submit for Review', submit, width=24).pack(anchor='e', pady=8)
        else:
            link.configure(state='readonly')
            notes.configure(state='disabled')
        def open_link():
            import webbrowser
            url = task['submission_url']
            if url and url.lower().startswith(('https://', 'http://')):
                webbrowser.open(url)
        if task['submission_url']:
            self.button(submission, 'Open Project Link', open_link).pack(anchor='w', pady=6)
        if task['submission_path']:
            def save_attachment():
                destination = filedialog.asksaveasfilename(title='Save submitted deliverable', initialfile=Path(task['submission_path']).name)
                if destination:
                    try:
                        shutil.copy2(task['submission_path'], destination)
                    except (OSError, shutil.SameFileError) as exc:
                        messagebox.showerror('Attachment', str(exc))
            self.button(submission, 'Save Attachment', save_attachment).pack(anchor='w', pady=6)
        if not student_view and task['status'] == 'Submitted':
            review = self.card(content)
            review.pack(fill='x', pady=8)
            tk.Label(review, text='Review feedback', bg=CARD, fg=NAVY).pack(anchor='w')
            feedback = tk.Text(review, height=3, wrap='word', font=self._font(10))
            feedback.pack(fill='x', pady=8)
            def decide(approve):
                try:
                    db.review_project(task_id, self.current_user['id'], approve, feedback.get('1.0', 'end-1c'))
                    messagebox.showinfo('Review saved', 'Project approved and earnings recorded.' if approve else 'Changes requested from the student.')
                    self.show_project_workspace(task_id)
                except ValueError as exc:
                    messagebox.showerror('Review', str(exc))
            self.button(review, 'Request Changes', lambda: decide(False), width=22).pack(side='left')
            self.button(review, 'Approve & Record Payment', lambda: decide(True), width=28).pack(side='right')
        self.button(content, 'Back to My Projects' if student_view else 'Back to My Tasks',
                    self.show_student_projects if student_view else self.show_business_tasks, width=24).pack(pady=12)

    def _read_setup_values(self):
        values = {}
        for key, widget in getattr(self, "_setup_entries", {}).items():
            if key == "about":
                values[key] = widget.get("1.0", "end-1c")
            else:
                values[key] = widget.get()
        return values

    def show_student_profile(self):
        self.clear()
        self._active_screen = "profile"
        student = db.get_student(self.current_user["id"])
        main = self._student_shell("profile", "Profile & Portfolio")

        actions = tk.Frame(main, bg=BG, padx=12)
        actions.pack(fill="x", pady=(0, 8))
        tk.Label(actions, text="Dashboard  >  Profile & Portfolio", bg=BG, fg=MUTED,
                 font=self._font(9)).pack(side="left")
        self.button(actions, "Save Changes", lambda: save_profile(), bg=SUCCESS,
                    width=15).pack(side="right")
        self.button(actions, "Cancel", self.show_student_profile, bg=NAVY,
                    width=10).pack(side="right", padx=(0, 7))

        page = tk.Frame(main, bg=BG)
        page.pack(fill="both", expand=True, padx=28, pady=(0, 16))
        canvas = tk.Canvas(page, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(page, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        content = tk.Frame(canvas, bg=BG)
        content_window = canvas.create_window((0, 0), window=content, anchor="nw")
        content.bind("<Configure>", lambda _event: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda event: canvas.itemconfigure(content_window, width=event.width))

        profile_card = self.card(content)
        profile_card.pack(fill="x", pady=(0, 12))
        tk.Label(profile_card, text="Personal information", bg=CARD, fg=NAVY,
                 font=self._font(18, True)).grid(row=0, column=0, columnspan=4,
                                                 sticky="w", pady=(0, 12))
        avatar = RoundedButton(profile_card, text="Add photo", bg="#edf3ff", fg=SUCCESS,
                   activebackground="#dce8ff", relief="flat", bd=0,
                   width=12, height=4, font=self._font(9, True), cursor="hand2")
        avatar.grid(row=1, column=0, rowspan=2, sticky="nw", padx=(0, 14))
        avatar_path = tk.StringVar(value=student.get("avatar_path") or "")
        def preview_avatar(path):
            image = self._avatar_image(path, 90)
            avatar.configure(image=image, text="", width=90, height=90)
            avatar.image = image

        def choose_avatar():
            filename = filedialog.askopenfilename(
                title="Choose profile photo",
                filetypes=[("Profile images", "*.png *.gif *.ppm *.pgm")],
            )
            if not filename:
                return
            try:
                preview_avatar(filename)
            except (tk.TclError, OSError):
                messagebox.showerror("Profile photo", "Choose a valid PNG or GIF image.")
                return
            avatar_path.set(filename)

        avatar.configure(command=choose_avatar)
        if avatar_path.get() and os.path.isfile(avatar_path.get()):
            try:
                preview_avatar(avatar_path.get())
            except (tk.TclError, OSError):
                avatar.configure(text="Edit photo")
        RoundedButton(profile_card, text="Edit photo", command=choose_avatar, bg=CARD,
                  fg=ACCENT, relief="flat", cursor="hand2", font=self._font(9, True)
                  ).grid(row=3, column=0, sticky="w", pady=(5, 0))

        fields = {}
        profile_values = {
            "Full name": student["name"],
            "Headline / role": student["headline"],
            "Location": student["location"],
            "University": student["university"],
            "Course": student["course"],
            "Graduation year": student["graduation_year"],
            "Portfolio website": student["portfolio"],
            "LinkedIn": student["linkedin"],
        }
        field_positions = [
            ("Full name", 1, 1), ("Headline / role", 1, 2),
            ("Location", 2, 1), ("University", 2, 2),
            ("Course", 3, 1), ("Graduation year", 3, 2),
            ("Portfolio website", 4, 1), ("LinkedIn", 4, 2),
        ]
        for label, row_index, column_index in field_positions:
            field = tk.Frame(profile_card, bg=CARD)
            field.grid(row=row_index, column=column_index, sticky="ew",
                       padx=(0, 12), pady=(0, 8))
            tk.Label(field, text=label, bg=CARD, fg=MUTED,
                     font=self._font(8, True)).pack(anchor="w", pady=(0, 3))
            entry = self.entry(field)
            entry.pack(fill="x", ipady=5)
            entry.insert(0, profile_values[label] or "")
            fields[label] = entry
        for column_index in range(1, 4):
            profile_card.columnconfigure(column_index, weight=1)

        about_card = self.card(content)
        about_card.pack(fill="x", pady=(0, 12))
        tk.Label(about_card, text="About me", bg=CARD, fg=NAVY,
                 font=self._font(15, True)).pack(anchor="w", pady=(0, 10))
        about = tk.Text(about_card, height=4, font=self._font(10), bg="#fbfcff",
                        fg=TEXT, relief="flat", wrap="word", highlightthickness=1,
                        highlightbackground=BORDER, highlightcolor=ACCENT)
        about.pack(fill="x")
        about.insert("1.0", student["about"] or "")

        skills_card = self.card(content)
        skills_card.pack(fill="x", pady=(0, 12))
        skill_heading = tk.Frame(skills_card, bg=CARD)
        skill_heading.pack(fill="x")
        tk.Label(skill_heading, text="Skills & Expertise", bg=CARD, fg=NAVY,
                 font=self._font(12, True)).pack(side="left")
        tk.Label(skill_heading, text="Set a level for each skill", bg=CARD, fg=MUTED,
                 font=self._font(8)).pack(side="right")
        skills_input_row = tk.Frame(skills_card, bg=CARD)
        skills_input_row.pack(fill="x", pady=(10, 7))
        skill_input = self.entry(skills_input_row)
        skill_input.pack(side="left", fill="x", expand=True, ipady=5)
        skill_levels = {}
        try:
            skill_levels.update(json.loads(student.get("skill_levels") or "{}"))
        except (TypeError, json.JSONDecodeError):
            pass
        skills = [skill.strip() for skill in (student["skills"] or "").split(",") if skill.strip()]
        skills_rows = tk.Frame(skills_card, bg=CARD)
        skills_rows.pack(fill="x")

        def render_skills():
            for child in skills_rows.winfo_children():
                child.destroy()
            for skill in skills:
                skill_row = tk.Frame(skills_rows, bg="#f7f9fa", padx=8, pady=5)
                skill_row.pack(fill="x", pady=3)
                tk.Label(skill_row, text=skill, bg="#f7f9fa", fg=TEXT,
                         font=self._font(9, True), width=24, anchor="w").pack(side="left")
                level = ttk.Combobox(skill_row,
                                     values=["Beginner", "Intermediate", "Advanced", "Expert"],
                                     state="readonly", width=15)
                level.set(skill_levels.get(skill, "Intermediate"))
                level.pack(side="left", padx=9)
                level.bind("<<ComboboxSelected>>",
                           lambda _event, name=skill, widget=level: skill_levels.update({name: widget.get()}))
                RoundedButton(skill_row, text="Remove", command=lambda name=skill: remove_skill(name),
                          bg="#f7f9fa", fg=DANGER, relief="flat", cursor="hand2",
                          font=self._font(8, True)).pack(side="right")

        def add_skill(_event=None):
            name = skill_input.get().strip().strip(",")
            if name and name.casefold() not in {item.casefold() for item in skills}:
                skills.append(name)
                skill_levels[name] = "Intermediate"
                render_skills()
            skill_input.delete(0, "end")
            return "break"

        def remove_skill(name):
            skills.remove(name)
            skill_levels.pop(name, None)
            render_skills()

        skill_input.bind("<Return>", add_skill)
        add_skill_button = self.button(skills_input_row, "Add skill", add_skill, bg=ACCENT, width=11)
        add_skill_button.pack(side="left", padx=(8, 0))
        render_skills()

        resume_card = self.card(content)
        resume_card.pack(fill="x", pady=(0, 12))
        tk.Label(resume_card, text="Resume", bg=CARD, fg=TEXT,
                 font=self._font(12, True)).pack(anchor="w")
        resume_path = tk.StringVar(value=student.get("resume_path") or "")
        resume_row = tk.Frame(resume_card, bg=CARD)
        resume_row.pack(fill="x", pady=(8, 0))
        tk.Label(resume_row, textvariable=resume_path, bg=CARD, fg=MUTED,
                 font=self._font(9)).pack(side="left", fill="x", expand=True, anchor="w")

        def choose_resume():
            filename = filedialog.askopenfilename(
                title="Choose resume",
                filetypes=[("Resume files", "*.pdf *.doc *.docx"), ("All files", "*.*")],
            )
            if filename:
                resume_path.set(filename)

        self.button(resume_row, "Upload PDF / DOCX", choose_resume, bg=NAVY,
                    width=16).pack(side="right")

        projects_card = self.card(content)
        projects_card.pack(fill="x")
        project_header = tk.Frame(projects_card, bg=CARD)
        project_header.pack(fill="x", pady=(0, 8))
        tk.Label(project_header, text="Portfolio projects", bg=CARD, fg=TEXT,
                 font=self._font(12, True)).pack(side="left")
        self.button(project_header, "Add project", lambda: edit_project(),
                    bg=ACCENT, width=12).pack(side="right")
        project_rows = tk.Frame(projects_card, bg=CARD)
        project_rows.pack(fill="x")

        def render_projects():
            for child in project_rows.winfo_children():
                child.destroy()
            projects = db.list_student_projects(student["id"])
            if not projects:
                tk.Label(project_rows, text="No projects yet. Add a project to showcase your work.",
                         bg=CARD, fg=MUTED, font=self._font(9)).pack(anchor="w", pady=8)
            for index, project in enumerate(projects):
                project_card = tk.Frame(project_rows, bg="#f7f9fa", padx=11, pady=9,
                                        highlightthickness=1, highlightbackground=BORDER)
                project_card.grid(row=index // 2, column=index % 2, sticky="nsew",
                                  padx=(0 if index % 2 == 0 else 6, 6 if index % 2 == 0 else 0),
                                  pady=5)
                project_rows.columnconfigure(index % 2, weight=1, uniform="profile-projects")
                cover_path = project["cover_image"]
                if cover_path and os.path.isfile(cover_path):
                    try:
                        cover = tk.PhotoImage(file=cover_path)
                        factor = max(1, (max(cover.width(), cover.height()) + 159) // 160)
                        cover = cover.subsample(factor, factor)
                        cover_label = tk.Label(project_card, image=cover, bg="#f7f9fa")
                        cover_label.image = cover
                        cover_label.pack(anchor="w", pady=(0, 6))
                    except tk.TclError:
                        tk.Label(project_card, text=f"Cover: {os.path.basename(cover_path)}",
                                 bg="#f7f9fa", fg=MUTED, font=self._font(8)).pack(anchor="w")
                tk.Label(project_card, text=project["title"], bg="#f7f9fa", fg=TEXT,
                         font=self._font(10, True)).pack(anchor="w")
                tk.Label(project_card, text=project["description"] or "No description",
                         bg="#f7f9fa", fg=MUTED, justify="left", anchor="w",
                         wraplength=360, font=self._font(8)).pack(fill="x", pady=(4, 5))
                details = ", ".join(filter(None, (project["tags"], project["live_url"], project["repo_url"])))
                tk.Label(project_card, text=details or "No links or tags", bg="#f7f9fa",
                         fg=ACCENT, justify="left", anchor="w", wraplength=360,
                         font=self._font(8)).pack(fill="x")
                buttons = tk.Frame(project_card, bg="#f7f9fa")
                buttons.pack(anchor="e", pady=(5, 0))
                self.button(buttons, "Edit", lambda item=project: edit_project(item),
                            bg=NAVY, width=7).pack(side="left", padx=3)
                self.button(buttons, "Delete", lambda item_id=project["id"]: delete_project(item_id),
                            bg=DANGER, width=7).pack(side="left", padx=3)

        def edit_project(project=None):
            dialog = tk.Toplevel(self)
            dialog.title("Edit Project" if project else "Add Project")
            dialog.configure(bg=BG)
            dialog.transient(self)
            dialog.grab_set()
            box = self.card(dialog)
            box.pack(fill="both", expand=True, padx=16, pady=16)
            entries = {}
            project_fields = [
                ("Title", "title"), ("Description", "description"),
                ("Skills / tags", "tags"), ("Cover image path", "cover_image"),
                ("Live demo URL", "live_url"), ("Repository URL", "repo_url"),
            ]
            for row_index, (label, key) in enumerate(project_fields):
                tk.Label(box, text=label, bg=CARD, fg=TEXT,
                         font=self._font(9, True)).grid(row=row_index * 2, column=0,
                                                       columnspan=2, sticky="w", pady=(7, 3))
                field = self.entry(box)
                field.grid(row=row_index * 2 + 1, column=0, sticky="ew", ipady=5)
                field.insert(0, project.get(key, "") if project else "")
                entries[key] = field
                if key == "cover_image":
                    def browse_cover(target=field):
                        filename = filedialog.askopenfilename(
                            parent=dialog, title="Choose project cover",
                            filetypes=[("Images", "*.png *.jpg *.jpeg *.gif"), ("All files", "*.*")],
                        )
                        if filename:
                            target.delete(0, "end")
                            target.insert(0, filename)
                    self.button(box, "Browse", browse_cover, bg=NAVY, width=9).grid(
                        row=row_index * 2 + 1, column=1, padx=(7, 0))
            box.columnconfigure(0, weight=1)

            def save_project():
                if not entries["title"].get().strip():
                    messagebox.showerror("Project title", "Enter a project title.", parent=dialog)
                    return
                db.save_student_project(
                    student["id"], entries["title"].get(), entries["description"].get(),
                    entries["tags"].get(), entries["cover_image"].get(),
                    entries["live_url"].get(), entries["repo_url"].get(),
                    project_id=project["id"] if project else None,
                )
                dialog.destroy()
                render_projects()

            buttons = tk.Frame(box, bg=CARD)
            buttons.grid(row=len(project_fields) * 2, column=0, columnspan=2,
                         sticky="e", pady=(12, 0))
            self.button(buttons, "Cancel", dialog.destroy, bg=NAVY, width=9).pack(side="left", padx=4)
            self.button(buttons, "Save Project", save_project, bg=SUCCESS, width=13).pack(side="left", padx=4)
            dialog.geometry("520x520")

        def delete_project(project_id):
            if messagebox.askyesno("Delete project", "Remove this project from your portfolio?"):
                db.delete_student_project(student["id"], project_id)
                render_projects()

        def save_profile():
            name = fields["Full name"].get().strip()
            if not name:
                messagebox.showerror("Full name", "Enter your name before saving.")
                return
            year = fields["Graduation year"].get().strip()
            if year and (not year.isdigit() or not 1900 <= int(year) <= 2200):
                messagebox.showerror("Graduation year", self.t("invalid_year"))
                return
            selected_photo = avatar_path.get()
            if selected_photo and selected_photo != (student.get("avatar_path") or ""):
                try:
                    photo_folder = Path(db.DB_PATH).parent / "profile_photos"
                    photo_folder.mkdir(exist_ok=True)
                    destination = photo_folder / f"{student['id']}_{uuid.uuid4().hex}{Path(selected_photo).suffix.lower()}"
                    shutil.copy2(selected_photo, destination)
                    avatar_path.set(str(destination))
                except OSError:
                    messagebox.showerror("Profile photo", "Could not save the photo. Please select it again.")
                    return
            db.update_student(
                student["id"], name, ", ".join(skills), student["availability"],
                student["minimum_budget"], student["experience"],
                headline=fields["Headline / role"].get(),
                university=fields["University"].get(), course=fields["Course"].get(),
                graduation_year=year, location=fields["Location"].get(),
                about=about.get("1.0", "end-1c"),
                portfolio=fields["Portfolio website"].get(),
                linkedin=fields["LinkedIn"].get(),
                skill_levels=json.dumps(skill_levels),
                resume_path=resume_path.get(), avatar_path=avatar_path.get(),
            )
            self.current_user = db.get_user(student["id"])
            messagebox.showinfo("Profile saved", "Your MicroIntern profile has been updated.")
            self.show_student_profile()

        render_projects()

    def show_student_setup(self):
        self.clear()
        self._active_screen = "onboarding"
        student = db.get_student(self.current_user["id"])
        saved_values = {
            "headline": student["headline"], "university": student["university"],
            "course": student["course"], "graduation_year": student["graduation_year"],
            "location": student["location"], "skills": student["skills"],
            "about": student["about"], "portfolio": student["portfolio"],
            "linkedin": student["linkedin"],
        }
        saved_values.update(getattr(self, "_setup_values", {}))
        self._setup_values = saved_values

        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", pady=(14, 10))
        self.brand_logo(header, background=BG).pack()
        self._language_picker(header).place(relx=0.96, rely=0.5, anchor="e")

        box = tk.Frame(self, bg=CARD, padx=24, pady=20,
                       highlightthickness=1, highlightbackground=BORDER)
        box.pack(fill="both", expand=True, padx=24, pady=(0, 22))
        tk.Label(box, text=self.t("setup_title"), bg=CARD, fg=NAVY,
                 font=self._font(17, True)).grid(row=0, column=0, columnspan=2, sticky="w")
        tk.Label(box, text=self.t("setup_subtitle"), bg=CARD, fg=MUTED,
                 font=self._font(10), wraplength=620, justify="left"
                 ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(4, 16))
        box.columnconfigure(0, weight=1, uniform="profile")
        box.columnconfigure(1, weight=1, uniform="profile")

        self._setup_entries = {}

        def add_entry(key, row, column, span=1):
            tk.Label(box, text=self.t(key), bg=CARD, fg=TEXT,
                     font=self._font(9, True)).grid(row=row, column=column,
                                                    columnspan=span, sticky="w",
                                                    pady=(4, 4), padx=(0 if column == 0 else 12, 0))
            field = self.entry(box)
            field.grid(row=row + 1, column=column, columnspan=span, sticky="ew",
                       ipady=6, padx=(0 if column == 0 else 12, 0), pady=(0, 7))
            field.insert(0, saved_values.get(key, ""))
            self._setup_entries[key] = field
            return field

        add_entry("headline", 2, 0, 2)
        add_entry("university", 4, 0)
        add_entry("course", 4, 1)
        add_entry("graduation_year", 6, 0)
        add_entry("location", 6, 1)
        add_entry("skills", 8, 0, 2)
        tk.Label(box, text=self.t("skills_hint"), bg=CARD, fg=MUTED,
                 font=self._font(8)).grid(row=10, column=0, columnspan=2,
                                          sticky="w", pady=(0, 4))

        tk.Label(box, text=self.t("about"), bg=CARD, fg=TEXT,
                 font=self._font(9, True)).grid(row=11, column=0, columnspan=2,
                                                sticky="w", pady=(4, 4))
        about = tk.Text(box, height=3, font=self._font(10), bg="#fbfcff", fg=TEXT,
                        relief="flat", wrap="word", highlightthickness=1,
                        highlightbackground=BORDER, highlightcolor=ACCENT)
        about.grid(row=12, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        about.insert("1.0", saved_values.get("about", ""))
        self._setup_entries["about"] = about

        add_entry("portfolio", 13, 0)
        add_entry("linkedin", 13, 1)

        def finish_setup():
            values = self._read_setup_values()
            year = values["graduation_year"].strip()
            if year and (not year.isdigit() or not 1900 <= int(year) <= 2200):
                messagebox.showerror(self.t("graduation_year"), self.t("invalid_year"))
                return
            db.update_student(
                student["id"], student["name"], values["skills"],
                student["availability"], student["minimum_budget"], student["experience"],
                headline=values["headline"], university=values["university"],
                course=values["course"], graduation_year=year,
                location=values["location"], about=values["about"],
                portfolio=values["portfolio"], linkedin=values["linkedin"],
            )
            self._setup_values = values
            messagebox.showinfo(self.t("profile"), self.t("profile_saved"))
            self.show_student_dashboard()

        self.button(box, self.t("finish_setup"), finish_setup, width=24).grid(
            row=15, column=0, columnspan=2, sticky="ew", pady=(7, 0)
        )

    def show_business_dashboard(self):
        self.clear()
        self._active_screen = "dashboard"
        b = db.get_business(self.current_user["id"])
        data = db.business_dashboard_data(b["id"])
        content, actions = self._business_shell('dashboard')
        search = self.entry(actions)
        search.configure(width=23)
        search.pack(side='left', ipady=6, padx=(0,9))
        search.insert(0, 'Search payments...')
        heading = tk.Frame(content, bg=BG)
        heading.pack(fill="x", pady=(0, 10))
        tk.Label(heading, text="Sales overview", bg=BG, fg=TEXT,
                 font=self._font(17, True)).pack(side="left")
        tk.Label(heading, text=datetime.now().strftime("%B %d, %Y"), bg=BG, fg=MUTED,
                 font=self._font(9)).pack(side="right", pady=5)

        metric_row = tk.Frame(content, bg=BG)
        metric_row.pack(fill="x")
        metrics = [
            ("Applicants", f"{data['customers'] or 0:,}", "Unique students"),
            ("Revenue", money(data["revenue"]), "Completed project payments"),
            ("Platform fees", money(data["fees"]), "10% service fee"),
            ("Invoices", f"{data['invoices'] or 0:,}", "Paid projects"),
        ]
        for index, (title, value, caption) in enumerate(metrics):
            metric = self.card(metric_row)
            metric.grid(row=0, column=index, sticky="nsew", padx=(0 if index == 0 else 7, 0))
            metric_row.columnconfigure(index, weight=1, uniform="sales-metrics")
            tk.Label(metric, text=title, bg=CARD, fg=MUTED,
                     font=self._font(9, True)).pack(anchor="w")
            tk.Label(metric, text=value, bg=CARD, fg=TEXT,
                     font=self._font(19, True)).pack(anchor="w", pady=(7, 3))
            tk.Label(metric, text=caption, bg=CARD, fg=MUTED,
                     font=self._font(8)).pack(anchor="w")

        analytics = tk.Frame(content, bg=BG)
        analytics.pack(fill="x", pady=12)
        invoice_panel = self.card(analytics)
        invoice_panel.pack(side="left", fill="both", padx=(0, 7))
        sales_panel = self.card(analytics)
        sales_panel.pack(side="left", fill="both", expand=True, padx=(7, 0))
        tk.Label(invoice_panel, text="Project payment status", bg=CARD, fg=TEXT,
                 font=self._font(11, True)).pack(anchor="w")
        donut_area = tk.Frame(invoice_panel, bg=CARD)
        donut_area.pack(fill="both", expand=True, pady=(7, 0))
        donut = tk.Canvas(donut_area, width=160, height=178, bg=CARD, highlightthickness=0)
        donut.pack(side="left")
        self._draw_business_donut(donut, data)
        legend = tk.Frame(donut_area, bg=CARD)
        legend.pack(side="left", fill="y", padx=(4, 0), pady=24)
        for label, amount, color in (
            ("Paid", data["paid"] or 0, SUCCESS),
            ("In progress", data["pending"] or 0, ACCENT),
            ("Open", data["open"] or 0, WARN),
        ):
            item = tk.Frame(legend, bg=CARD)
            item.pack(anchor="w", pady=6)
            tk.Label(item, text="●", bg=CARD, fg=color, font=self._font(9)).pack(side="left")
            tk.Label(item, text=f" {label}", bg=CARD, fg=MUTED,
                     font=self._font(8)).pack(side="left")
            tk.Label(legend, text=str(amount), bg=CARD, fg=TEXT,
                     font=self._font(11, True)).pack(anchor="w", padx=(14, 0))

        chart_heading = tk.Frame(sales_panel, bg=CARD)
        chart_heading.pack(fill="x")
        tk.Label(chart_heading, text="Payment activity", bg=CARD, fg=TEXT,
                 font=self._font(11, True)).pack(side="left")
        tk.Label(chart_heading, text="Monthly · current year", bg=CARD, fg=MUTED,
                 font=self._font(8)).pack(side="right")
        chart = tk.Canvas(sales_panel, height=174, bg=CARD, highlightthickness=0)
        chart.pack(fill="x", expand=True, pady=(5, 0))
        self._draw_business_monthly_chart(chart, data["monthly"])

        table_panel = self.card(content)
        table_panel.pack(fill="both", expand=True)
        table_header = tk.Frame(table_panel, bg=CARD)
        table_header.pack(fill="x", pady=(0, 8))
        tk.Label(table_header, text="Recent project payments", bg=CARD, fg=TEXT,
                 font=self._font(11, True)).pack(side="left")
        controls = tk.Frame(table_header, bg=CARD)
        controls.pack(side="right")
        status_filter = ttk.Combobox(controls, values=["All payments", "Paid"],
                                     state="readonly", width=13)
        status_filter.set("All payments")
        status_filter.pack(side="left", padx=(0, 7))
        export = self.button(controls, "Export CSV", lambda: None, bg=NAVY, width=11)
        export.pack(side="left")
        columns = ("invoice", "student", "project", "date", "status", "amount")
        tree = ttk.Treeview(table_panel, columns=columns, show="headings", height=5)
        for column, width in zip(columns, (100, 145, 250, 135, 95, 100)):
            tree.heading(column, text=column.title())
            tree.column(column, width=width, anchor="w")
        tree.tag_configure("paid", foreground=SUCCESS)
        tree.pack(fill="both", expand=True)

        def refresh_payments(*_args):
            query = search.get().strip().lower()
            if query == "search payments...":
                query = ""
            tree.delete(*tree.get_children())
            for invoice in data["recent"]:
                status = "Paid"
                searchable = f"{invoice['task_id']} {invoice['student_name'] or ''} {invoice['title']} {status}".lower()
                if query and query not in searchable:
                    continue
                if status_filter.get() != "All payments" and status != status_filter.get():
                    continue
                tree.insert("", "end", values=(
                    f"MI-{invoice['task_id']:05d}", invoice["student_name"] or "Student",
                    invoice["title"], invoice["created_at"][:10], status,
                    money(invoice["gross"]),
                ), tags=("paid",))

        def clear_search_hint(_event):
            if search.get() == "Search payments...":
                search.delete(0, "end")

        def restore_search_hint(_event):
            if not search.get().strip():
                search.insert(0, "Search payments...")
                refresh_payments()

        search.bind("<FocusIn>", clear_search_hint)
        search.bind("<FocusOut>", restore_search_hint)

        def export_payments():
            filename = filedialog.asksaveasfilename(
                title="Export project payments", defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")], initialfile="microintern-payments.csv",
            )
            if not filename:
                return
            with open(filename, "w", newline="", encoding="utf-8") as output:
                writer = csv.writer(output)
                writer.writerow(["Invoice", "Student", "Project", "Date", "Status", "Amount"])
                for item in tree.get_children():
                    writer.writerow(tree.item(item, "values"))
            messagebox.showinfo("Export complete", "Project payments were exported.")

        export.configure(command=export_payments)
        search.bind("<KeyRelease>", refresh_payments)
        status_filter.bind("<<ComboboxSelected>>", refresh_payments)
        tree.bind("<Double-1>", lambda _event: self._show_payment_detail(tree))
        refresh_payments()

    def _draw_business_donut(self, canvas, data):
        values = [int(data["paid"] or 0), int(data["pending"] or 0), int(data["open"] or 0)]
        colors = [SUCCESS, ACCENT, WARN]
        total = sum(values)
        bounds = (18, 14, 142, 138)
        canvas.create_oval(*bounds, outline="#edf0f5", width=20)
        if total:
            start = 90
            for value, color in zip(values, colors):
                extent = 360 * value / total
                if extent:
                    canvas.create_arc(*bounds, start=start, extent=-extent, style="arc",
                                      outline=color, width=20)
                start -= extent
        canvas.create_text(80, 70, text=f"{total:,}", fill=TEXT,
                           font=self._font(17, True))
        canvas.create_text(80, 92, text="Projects", fill=MUTED, font=self._font(8))

    def _draw_business_monthly_chart(self, canvas, monthly):
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        values = [float(monthly.get(index, 0) or 0) for index in range(1, 13)]
        canvas.update_idletasks()
        width = max(canvas.winfo_width(), 540)
        height = 174
        left, right, top, bottom = 42, width - 15, 12, height - 28
        maximum = max(max(values), 1)
        for step in range(5):
            y = top + step * (bottom - top) / 4
            amount = maximum * (4 - step) / 4
            canvas.create_line(left, y, right, y, fill="#edf0f2")
            canvas.create_text(left - 8, y, text=f"${amount:,.0f}", anchor="e",
                               fill=MUTED, font=self._font(7))
        points = []
        for index, value in enumerate(values):
            x = left + index * (right - left) / 11
            y = bottom - value / maximum * (bottom - top)
            points.append((x, y))
        area = [left, bottom] + [coordinate for point in points for coordinate in point] + [right, bottom]
        canvas.create_polygon(*area, fill="#edf0ff", outline="")
        canvas.create_line(*[coordinate for point in points for coordinate in point],
                           fill=ACCENT, width=2, smooth=True)
        for index, (x, y) in enumerate(points):
            canvas.create_oval(x - 3, y - 3, x + 3, y + 3,
                               fill=CARD, outline=ACCENT, width=2)
            canvas.create_text(x, bottom + 13, text=months[index], fill=MUTED,
                               font=self._font(7))

        tooltip = canvas.create_text(0, 0, text="", fill=TEXT, anchor="nw",
                                    font=self._font(8, True), state="hidden")
        def show_tooltip(event):
            index = round((event.x - left) / (right - left) * 11)
            if not 0 <= index < len(points):
                canvas.itemconfigure(tooltip, state="hidden")
                return
            canvas.itemconfigure(tooltip, text=f"{months[index]}  {money(values[index])}",
                                 state="normal")
            canvas.coords(tooltip, min(event.x + 9, right - 82), max(top, event.y - 18))
        canvas.bind("<Motion>", show_tooltip)
        canvas.bind("<Leave>", lambda _event: canvas.itemconfigure(tooltip, state="hidden"))

    def _show_payment_detail(self, tree):
        selected = tree.selection()
        if not selected:
            return
        invoice, student, title, date, status, amount = tree.item(selected[0], "values")
        messagebox.showinfo(invoice, f"{title}\nStudent: {student}\nDate: {date}\nStatus: {status}\nAmount: {amount}")

    def show_business_invoices(self):
        self.clear()
        business = db.get_business(self.current_user["id"])
        data = db.business_dashboard_data(business["id"])
        main, _ = self._business_shell('payments', 'Project Payments', 'Review completed project payments and platform fees.')
        frame = self.card(main)
        frame.pack(fill="both", expand=True)
        columns = ("invoice", "student", "project", "date", "status", "gross", "fee")
        tree = ttk.Treeview(frame, columns=columns, show="headings")
        for column, width in zip(columns, (100, 150, 300, 150, 100, 110, 110)):
            tree.heading(column, text=column.title())
            tree.column(column, width=width, anchor="w")
        for invoice in data["recent"]:
            tree.insert("", "end", values=(
                f"MI-{invoice['task_id']:05d}", invoice["student_name"] or "Student",
                invoice["title"], invoice["created_at"][:10], "Paid",
                money(invoice["gross"]), money(invoice["platform_fee"]),
            ))
        tree.pack(fill="both", expand=True)
        tree.bind("<Double-1>", lambda _event: self._show_payment_detail(tree))

    def show_business_inbox(self):
        self.clear()
        main, _ = self._business_shell('applicants', 'Applicant Inbox', 'Review students who applied to your projects.')
        frame = self.card(main)
        frame.pack(fill="both", expand=True)
        columns = ("task_id", "project", "student", "match", "status")
        tree = ttk.Treeview(frame, columns=columns, show="headings")
        for column, width in zip(columns, (70, 300, 180, 100, 120)):
            tree.heading(column, text=column.replace("_", " ").title())
            tree.column(column, width=width, anchor="w")
        for task in db.list_business_tasks(self.current_user["id"]):
            for applicant in db.list_task_applicants(task["id"]):
                tree.insert("", "end", values=(task["id"], task["title"], applicant["name"],
                                                 f"{applicant['match_score']:.1f}%", applicant["status"]))
        tree.pack(fill="both", expand=True)
        def review_selected():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Select Application", "Select an applicant first.")
                return
            self.show_applicants(int(tree.item(selected[0], "values")[0]))
        self.button(frame, "Review Applicants", review_selected, bg=SUCCESS).pack(pady=10)

    def _business_task_table(self, limit=None, parent=None):
        tasks=db.list_business_tasks(self.current_user["id"])
        if limit: tasks=tasks[:limit]
        frame=self.card(parent or self); frame.pack(fill="both",expand=True,pady=5)
        cols=("id","title","category","budget","status","student")
        tree=ttk.Treeview(frame,columns=cols,show="headings")
        for c,w in zip(cols,[55,290,150,90,110,160]):
            tree.heading(c,text=c.title()); tree.column(c,width=w,anchor="w")
        for t in tasks:
            tree.insert("","end",values=(t["id"],t["title"],t["category"],money(t["budget"]),
                                         t["status"],t["student_name"] or "-"))
        tree.pack(fill="both",expand=True)

        def applicants():
            sel=tree.selection()
            if not sel:
                messagebox.showwarning("Select Task","Select a task first."); return
            self.show_applicants(int(tree.item(sel[0],"values")[0]))

        def advance():
            sel=tree.selection()
            if not sel:
                messagebox.showwarning("Select Task","Select a task first."); return
            tid=int(tree.item(sel[0],"values")[0])
            task=db.get_task(tid)
            if task['status'] in ('In Progress', 'Submitted', 'Changes Requested', 'Completed'):
                self.show_project_workspace(tid)
                return
            transitions={"Assigned":"In Progress"}
            nxt=transitions.get(task["status"])
            if not nxt:
                messagebox.showinfo("No Action","This task cannot be advanced from its current status.")
                return
            try:
                db.update_task_status(tid,nxt)
                messagebox.showinfo("Updated",f"Task status changed to {nxt}.")
                self.show_business_tasks()
            except Exception as exc:
                messagebox.showerror("Error",str(exc))

        btns=tk.Frame(frame,bg=BG); btns.pack(pady=10)
        self.button(btns,"View Applicants",applicants,bg="#6366f1").pack(side="left",padx=5)
        self.button(btns,"Advance Status",advance,bg=SUCCESS).pack(side="left",padx=5)
        def review_work():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning('Select project', 'Select a project to review.')
                return
            self.show_project_workspace(int(tree.item(selected[0], 'values')[0]))
        self.button(btns, 'Review Submission', review_work, width=22).pack(side='left', padx=5)

    def show_business_tasks(self):
        self.clear()
        main, _ = self._business_shell('tasks', 'My Tasks', 'Manage posted projects, review applicants, and approve submitted work.')
        self._business_task_table(parent=main)

    def show_post_task(self):
        self.clear()
        main, _ = self._business_shell('post', 'Post New Task', 'Describe the work, requirements, and deliverables for your next project.')
        content = self._scroll_page(main)
        box=self.card(content); box.pack(fill='x', pady=12)

        labels=["Title","Category","Description","Required skills (comma-separated)",
                "Budget","Deadline (YYYY-MM-DD)","Schedule (comma-separated)","Deliverables (optional)"]
        entries={}
        for i,label in enumerate(labels):
            tk.Label(box,text=label,fg=TEXT,bg=CARD).grid(row=i,column=0,sticky="w",pady=6,padx=6)
            e=self.entry(box); e.grid(row=i,column=1,ipadx=170,ipady=5,padx=6)
            entries[label]=e

        tk.Label(box,text="Experience",fg=TEXT,bg=CARD).grid(row=8,column=0,sticky="w",pady=6,padx=6)
        exp=ttk.Combobox(box,values=["Beginner","Intermediate","Advanced"],state="readonly")
        exp.set("Beginner"); exp.grid(row=8,column=1,sticky="ew",pady=6,padx=6)

        def submit():
            vals={k:e.get().strip() for k,e in entries.items()}
            if not all(vals[k] for k in ["Title","Category","Description","Required skills (comma-separated)","Budget","Deadline (YYYY-MM-DD)"]):
                messagebox.showerror("Missing Data","Complete all required fields."); return
            try:
                budget=float(vals["Budget"])
                if budget <= 0: raise ValueError
                datetime.strptime(vals["Deadline (YYYY-MM-DD)"], "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Invalid Input","Budget must be positive and deadline must use YYYY-MM-DD."); return
            tid=db.create_task(
                self.current_user["id"],vals["Title"],vals["Category"],vals["Description"],
                vals["Required skills (comma-separated)"],budget,vals["Deadline (YYYY-MM-DD)"],
                vals["Schedule (comma-separated)"],exp.get(), vals["Deliverables (optional)"]
            )
            messagebox.showinfo("Task Posted",f"Task #{tid} is now open.")
            self.show_business_tasks()

        self.button(box,"Post Task",submit,bg=SUCCESS,width=22).grid(row=9,column=0,columnspan=2,pady=18)

    def show_applicants(self, task_id):
        self.clear()
        task=db.get_task(task_id)
        main, _ = self._business_shell('applicants', 'Project Applicants', task['title'])
        frame=self.card(main); frame.pack(fill="both",expand=True,pady=10)
        cols=("app_id","student","skills","experience","rating","match","status")
        tree=ttk.Treeview(frame,columns=cols,show="headings")
        for c,w in zip(cols,[70,150,310,110,80,90,100]):
            tree.heading(c,text=c.replace("_"," ").title()); tree.column(c,width=w,anchor="w")
        for a in db.list_task_applicants(task_id):
            tree.insert("","end",values=(a["id"],a["name"],a["skills"],a["experience"],
                                         f"{a['rating']:.1f}",f"{a['match_score']:.1f}%",a["status"]))
        tree.pack(fill="both",expand=True)

        def decision(accept):
            sel=tree.selection()
            if not sel:
                messagebox.showwarning("Select Applicant","Select an applicant first."); return
            app_id=int(tree.item(sel[0],"values")[0])
            try:
                db.decide_application(app_id,accept)
                messagebox.showinfo("Updated","Applicant accepted." if accept else "Applicant rejected.")
                self.show_applicants(task_id)
            except Exception as exc:
                messagebox.showerror("Error",str(exc))

        controls=tk.Frame(frame,bg=BG); controls.pack(pady=10)
        self.button(controls,"Accept",lambda:decision(True),bg=SUCCESS).pack(side="left",padx=5)
        self.button(controls,"Reject",lambda:decision(False),bg=DANGER).pack(side="left",padx=5)

    def show_business_profile(self):
        self.clear()
        b=db.get_business(self.current_user["id"])
        main, _ = self._business_shell('profile', 'Business Profile', 'Keep your business details up to date for students and collaborators.')
        content = self._scroll_page(main)
        box=self.card(content); box.pack(fill='x', pady=12)

        tk.Label(box,text="Business Name",fg=TEXT,bg=CARD).grid(row=0,column=0,sticky="w")
        name=self.entry(box); name.insert(0,b["name"]); name.grid(row=1,column=0,ipadx=170,ipady=6,pady=(4,12))

        tk.Label(box,text="Industry",fg=TEXT,bg=CARD).grid(row=2,column=0,sticky="w")
        industry=self.entry(box); industry.insert(0,b["industry"]); industry.grid(row=3,column=0,ipadx=170,ipady=6,pady=(4,12))

        tk.Label(box,text="Description",fg=TEXT,bg=CARD).grid(row=4,column=0,sticky="w")
        desc=tk.Text(box,width=52,height=6,font=("Segoe UI",10),relief="flat")
        desc.insert("1.0",b["description"]); desc.grid(row=5,column=0,pady=(4,12))

        def save():
            db.update_business(b["id"],name.get(),industry.get(),desc.get("1.0","end").strip())
            messagebox.showinfo("Saved","Business profile updated.")
            self.show_business_dashboard()

        self.button(box,"Save Profile",save,bg=SUCCESS,width=22).grid(row=6,column=0,pady=10)

    def logout(self):
        self.current_user=None
        self._setup_values = {}
        self.show_welcome()
