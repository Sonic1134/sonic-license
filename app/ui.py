import requests
import csv
import json
import math
import shutil
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import sys
from pathlib import Path
import os
import uuid
import hashlib


def resource_path(relative_path):
    try:
        base_path = Path(sys._MEIPASS)
    except Exception:
        base_path = Path(__file__).resolve().parent
    return base_path / relative_path


APP_NAME = "Plånbokens Månadsplanering"
APP_VERSION = "4.0"

LICENSE_SERVER_URL = "https://web-production-0746.up.railway.app"

APP_BG = "#12385F"

SIDEBAR_BG = "#262A63"
SIDEBAR_BG_DARK = "#202454"
SIDEBAR_MUTED = "#AAB0DC"

TOPBAR_BG = "#ECE9D8"
TOPBAR_BORDER = "#ACA899"
TOPBAR_BUTTON_BG = "#F0F0F0"
TOPBAR_BUTTON_FG = "#000000"
TOPBAR_BUTTON_ACTIVE = "#DDE6F7"
TOPBAR_BUTTON_BORDER_LIGHT = "#FFFFFF"
TOPBAR_BUTTON_BORDER_DARK = "#7A7A7A"
TOPBAR_SEPARATOR = "#B8B4A8"

WORKSPACE_BG = "#F5F7FB"
PANEL_BG = "#FFFFFF"
PANEL_BORDER = "#E2E8F0"

CARD_BG = "#FFFFFF"
CARD_BORDER = "#E5EAF2"
CARD_HEADER_BG = SIDEBAR_BG
CARD_HEADER_TEXT = "#FFFFFF"

ROW_BG = "#FFFFFF"
ROW_ALT_BG = "#FAFBFD"
ROW_HOVER = "#F2F7FF"

INPUT_BG = "#FFFFFF"
INPUT_UNDERLINE = "#D6DEE8"
INPUT_FOCUS_UNDERLINE = "#4A90E2"

TITLE_RED = "#E53935"
KPI_VALUE_COLOR = "#FFFFFF"
NEGATIVE_RED = "#FF6B6B"

BUTTON_BG_SECONDARY = "#EEF3F8"
BUTTON_FG_SECONDARY = "#334155"

TEXT_COLOR = "#000000"
MUTED_TEXT = "#64748B"

DIALOG_BG = "#A9C7EB"
DIALOG_PRIMARY = "#4F86F7"
DIALOG_CANCEL_BG = "#F2F2F2"
DIALOG_CANCEL_BORDER = "#9E9E9E"

WINDOW_WIDTH = 1560
WINDOW_HEIGHT = 940
WINDOW_MIN_WIDTH = 1280
WINDOW_MIN_HEIGHT = 780

SECTION_ORDER = [
    "INKOMST",
    "MATKONTO",
    "FRITID",
    "KREDITER",
    "BOENDE",
    "MEDIA",
    "TRANSPORT",
    "SPARANDE",
    "OVRIGT",
]

SECTION_LABELS = {
    "INKOMST": "Inkomst",
    "MATKONTO": "Matkonto",
    "FRITID": "Fritid",
    "KREDITER": "Krediter",
    "BOENDE": "Boende",
    "MEDIA": "Media",
    "TRANSPORT": "Transport",
    "SPARANDE": "Sparande",
    "OVRIGT": "Övrigt",
    "RESULTAT": "Resultat",
}

DEFAULT_ROWS = {
    "INKOMST": [],
    "MATKONTO": [],
    "FRITID": [],
    "KREDITER": [],
    "BOENDE": [],
    "MEDIA": [],
    "TRANSPORT": [],
    "SPARANDE": [],
    "OVRIGT": [],
}

EXPENSE_SECTION_NAMES = ["MATKONTO", "FRITID", "KREDITER", "BOENDE", "MEDIA", "TRANSPORT", "OVRIGT"]
SAVINGS_SECTION_NAMES = ["SPARANDE"]


def get_app_data_dir():
    local_appdata = os.getenv("LOCALAPPDATA")
    if local_appdata:
        return Path(local_appdata) / "Sonic"
    return Path.home() / "AppData" / "Local" / "Sonic"


APP_DATA_DIR = get_app_data_dir()
APP_DATA_DIR.mkdir(parents=True, exist_ok=True)

DATA_DIR = APP_DATA_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

MONTHS_FILE = DATA_DIR / "months.json"
SETTINGS_FILE = DATA_DIR / "settings.json"
LOCAL_LICENSE_FILE = APP_DATA_DIR / "local_license.json"

BACKUP_DIR = DATA_DIR / "backups"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

BASE_DIR = Path(__file__).resolve().parent
LOGO_FILE = Path(__file__).resolve().parent.parent / "data" / "logo.png"


def load_json(path, default=None):
    if default is None:
        default = {}
    try:
        path = Path(path)
        if not path.exists():
            return default
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    print("SPARAR JSON TILL:", path)
    print("JSON-INNEHÅLL:", data)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def create_backup(source_path, prefix):
    source_path = Path(source_path)
    if not source_path.exists():
        return
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    target = BACKUP_DIR / f"{prefix}_{ts}.json"
    shutil.copy2(source_path, target)


def format_amount(value):
    try:
        n = float(value)
    except Exception:
        n = 0.0

    if abs(n - int(n)) < 0.00001:
        return f"{int(n):,}".replace(",", " ") + " kr"

    return f"{n:,.2f}".replace(",", "X").replace(".", ",").replace("X", " ") + " kr"


def format_amount_input(value):
    try:
        n = float(value)
    except Exception:
        n = 0.0

    if abs(n - int(n)) < 0.00001:
        return f"{int(n):,}".replace(",", " ")

    return f"{n:,.2f}".replace(",", "X").replace(".", ",").replace("X", " ")


def format_amount_display(value):
    return f"{format_amount_input(value)} kr"


def parse_amount(text):
    cleaned = str(text).strip().replace("kr", "").replace(" ", "").replace(",", ".")
    if not cleaned:
        return 0.0
    try:
        return float(cleaned)
    except Exception:
        return 0.0


def month_name_to_number(month_name):
    mapping = {
        "Januari": "01",
        "Februari": "02",
        "Mars": "03",
        "April": "04",
        "Maj": "05",
        "Juni": "06",
        "Juli": "07",
        "Augusti": "08",
        "September": "09",
        "Oktober": "10",
        "November": "11",
        "December": "12",
    }
    return mapping.get(month_name)


def parse_year_from_month_name(name, fallback_key=""):
    try:
        parts = str(name).split()
        if len(parts) >= 2:
            return int(parts[-1])
    except Exception:
        pass

    try:
        return int(str(fallback_key)[:4])
    except Exception:
        return datetime.now().year


def sort_month_keys(months_data):
    def key_func(k):
        text = str(k)
        parts = text.split("-")
        year = 0
        month = 0
        suffix = 1
        try:
            if len(parts) >= 2:
                year = int(parts[0])
                month = int(parts[1])
            if len(parts) >= 3:
                suffix = int(parts[2])
        except Exception:
            pass
        return year, month, suffix, text

    return sorted(months_data.keys(), key=key_func)


def calculate_totals(rows):
    grouped = {section: 0.0 for section in SECTION_ORDER}
    for row in rows:
        if row.get("hidden", False):
            continue
        section = row.get("section", "OVRIGT")
        if section not in grouped:
            section = "OVRIGT"
        grouped[section] += float(row.get("actual", 0) or 0)

    income = grouped.get("INKOMST", 0.0)
    expenses = sum(grouped.get(section, 0.0) for section in EXPENSE_SECTION_NAMES)
    savings = sum(grouped.get(section, 0.0) for section in SAVINGS_SECTION_NAMES)
    partial = income - expenses
    result = partial - savings

    return {
        "section_totals": grouped,
        "actual_income": income,
        "actual_expense": expenses,
        "partial_result": partial,
        "actual_savings": savings,
        "actual_result": result,
    }


class NewMonthDialog(tk.Toplevel):
    def __init__(self, parent, default_month=None, default_year=None):
        super().__init__(parent)
        self.title("Skapa ny månad")
        self.geometry("380x260")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.configure(bg=DIALOG_BG)
        self.result = None

        months = [
            "Januari", "Februari", "Mars", "April", "Maj", "Juni",
            "Juli", "Augusti", "September", "Oktober", "November", "December",
        ]
        current_year = datetime.now().year
        years = [str(year) for year in range(current_year - 1, 2101)]

        if default_month is None:
            default_month = months[0]
        if default_year is None:
            default_year = str(current_year)

        body = tk.Frame(self, bg=DIALOG_BG)
        body.pack(fill="both", expand=True, padx=22, pady=20)

        tk.Label(
            body,
            text="Ny budgetmånad",
            bg=DIALOG_BG,
            fg="#000000",
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w", pady=(0, 10))

        tk.Label(
            body,
            text="Skapar en ny tom månad. Inga underkategorier eller belopp följer med.",
            bg=DIALOG_BG,
            fg="#000000",
            justify="left",
            font=("Segoe UI", 10),
            wraplength=320,
        ).pack(anchor="w", pady=(0, 14))

        fields = tk.Frame(body, bg=DIALOG_BG)
        fields.pack(fill="x")

        month_wrap = tk.Frame(fields, bg=DIALOG_BG)
        month_wrap.pack(side="left", padx=(0, 12))

        tk.Label(
            month_wrap,
            text="Månad",
            bg=DIALOG_BG,
            fg="#000000",
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(0, 4))

        self.month_var = tk.StringVar(value=default_month)
        self.month_combo = ttk.Combobox(
            month_wrap,
            values=months,
            textvariable=self.month_var,
            state="readonly",
            width=14,
        )
        self.month_combo.pack(anchor="w")

        year_wrap = tk.Frame(fields, bg=DIALOG_BG)
        year_wrap.pack(side="left")

        tk.Label(
            year_wrap,
            text="År",
            bg=DIALOG_BG,
            fg="#000000",
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(0, 4))

        self.year_var = tk.StringVar(value=str(default_year))
        self.year_combo = ttk.Combobox(
            year_wrap,
            values=years,
            textvariable=self.year_var,
            state="readonly",
            width=10,
        )
        self.year_combo.pack(anchor="w")

        buttons = tk.Frame(body, bg=DIALOG_BG)
        buttons.pack(fill="x", pady=(22, 0))

        create_wrap = tk.Frame(buttons, bg=DIALOG_PRIMARY, highlightthickness=0, bd=0)
        create_wrap.pack(side="right", padx=(8, 0))

        tk.Button(
            create_wrap,
            text="Skapa månad",
            command=self._submit,
            bg=DIALOG_PRIMARY,
            fg="white",
            activebackground="#3F73DB",
            activeforeground="white",
            relief="flat",
            bd=0,
            padx=18,
            pady=10,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
        ).pack()

        cancel_outer = tk.Frame(
            buttons,
            bg=DIALOG_CANCEL_BORDER,
            highlightthickness=1,
            highlightbackground=DIALOG_CANCEL_BORDER,
        )
        cancel_outer.pack(side="right")

        cancel_inner = tk.Frame(cancel_outer, bg="white")
        cancel_inner.pack(fill="both", expand=True, padx=(1, 0), pady=(1, 0))

        tk.Button(
            cancel_inner,
            text="Avbryt",
            command=self.destroy,
            bg=DIALOG_CANCEL_BG,
            fg="#000000",
            activebackground="#E9E9E9",
            activeforeground="#000000",
            relief="flat",
            bd=0,
            padx=24,
            pady=10,
            font=("Segoe UI", 10),
            cursor="hand2",
        ).pack()

    def _submit(self):
        self.result = f"{self.month_var.get()} {self.year_var.get()}"
        self.destroy()


class SavedMonthDialog(tk.Toplevel):
    def __init__(self, parent, labels, current_label=None):
        super().__init__(parent)
        self.title("Visa sparad månad")
        self.geometry("360x165")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.configure(bg="#FFFFFF")
        self.result = None

        body = tk.Frame(self, bg="#FFFFFF")
        body.pack(fill="both", expand=True, padx=20, pady=18)

        tk.Label(
            body,
            text="Välj sparad månad",
            bg="#FFFFFF",
            fg=TEXT_COLOR,
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w", pady=(0, 8))

        self.month_var = tk.StringVar(value=current_label or (labels[0] if labels else ""))
        combo = ttk.Combobox(
            body,
            values=labels,
            textvariable=self.month_var,
            state="readonly",
            width=24,
        )
        combo.pack(anchor="w")

        button_row = tk.Frame(body, bg="#FFFFFF")
        button_row.pack(fill="x", pady=(20, 0))

        tk.Button(
            button_row,
            text="Avbryt",
            command=self.destroy,
            bg="#E5E7EB",
            fg=TEXT_COLOR,
            relief="flat",
            bd=0,
            padx=12,
            pady=6,
            cursor="hand2",
            font=("Segoe UI", 9, "bold"),
        ).pack(side="right", padx=(8, 0))

        tk.Button(
            button_row,
            text="Visa månad",
            command=self._submit,
            bg="#4A90E2",
            fg="white",
            relief="flat",
            bd=0,
            padx=12,
            pady=6,
            cursor="hand2",
            font=("Segoe UI", 9, "bold"),
        ).pack(side="right")

    def _submit(self):
        self.result = self.month_var.get().strip()
        self.destroy()


class DetailWindow(tk.Toplevel):
    def __init__(self, master, title, rows, helper_text="Dubbelklicka på ett belopp för att se underkategorierna."):
        super().__init__(master)
        self.title(title)
        self.geometry("520x560")
        self.configure(bg=WORKSPACE_BG)

        wrap = tk.Frame(self, bg=WORKSPACE_BG)
        wrap.pack(fill="both", expand=True, padx=18, pady=18)

        card = tk.Frame(wrap, bg=CARD_BG, highlightthickness=1, highlightbackground=PANEL_BORDER)
        card.pack(fill="both", expand=True)

        inner = tk.Frame(card, bg=CARD_BG)
        inner.pack(fill="both", expand=True, padx=18, pady=18)

        tk.Label(
            inner,
            text=title,
            bg=CARD_BG,
            fg=TEXT_COLOR,
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w", pady=(0, 6))

        tk.Label(
            inner,
            text=helper_text,
            bg=CARD_BG,
            fg=MUTED_TEXT,
            font=("Segoe UI", 9),
        ).pack(anchor="w", pady=(0, 12))

        tree = ttk.Treeview(inner, columns=("namn", "belopp"), show="headings")
        tree.heading("namn", text="Underkategori")
        tree.heading("belopp", text="Belopp")
        tree.column("namn", width=300, anchor="w")
        tree.column("belopp", width=150, anchor="e")

        for name, value in rows:
            tree.insert("", "end", values=(name, format_amount_display(value)))

        yscroll = ttk.Scrollbar(inner, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=yscroll.set)

        tree.pack(side="left", fill="both", expand=True)
        yscroll.pack(side="right", fill="y")

        tk.Button(
            inner,
            text="Stäng",
            command=self.destroy,
            bg="#E5E7EB",
            fg=TEXT_COLOR,
            relief="flat",
            bd=0,
            padx=12,
            pady=6,
            cursor="hand2",
            font=("Segoe UI", 9, "bold"),
        ).pack(pady=12)


class SummaryWindow(tk.Toplevel):
    def __init__(self, master, monthly_rows, year_matrix, current_year):
        super().__init__(master)
        self.master_app = master
        self.title("Sammanställning")
        self.geometry("1180x720")
        self.configure(bg=WORKSPACE_BG)

        self.monthly_rows = monthly_rows
        self.year_matrix = year_matrix
        self.current_year = current_year
        self.month_tree = None
        self.year_tree = None

        self._configure_treeview_style()

        outer = tk.Frame(self, bg="#FFFFFF", highlightthickness=1, highlightbackground=PANEL_BORDER)
        outer.pack(fill="both", expand=True, padx=18, pady=18)

        switchbar = tk.Frame(outer, bg="#FFFFFF")
        switchbar.pack(fill="x", padx=18, pady=(18, 12))

        self.btn_month = tk.Button(
            switchbar,
            text="Sammanställning per månad",
            command=self.show_month_tab,
            bg="#4A90E2",
            fg="white",
            relief="flat",
            bd=0,
            font=("Segoe UI", 10, "bold"),
            padx=14,
            pady=8,
            cursor="hand2",
        )
        self.btn_month.pack(side="left", padx=(0, 8))

        self.btn_year = tk.Button(
            switchbar,
            text="År vs År",
            command=self.show_year_tab,
            bg="#FFFFFF",
            fg=TEXT_COLOR,
            relief="solid",
            bd=1,
            font=("Segoe UI", 10),
            padx=14,
            pady=8,
            cursor="hand2",
        )
        self.btn_year.pack(side="left")

        self.content = tk.Frame(outer, bg="#FFFFFF")
        self.content.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        self.month_column_map = {
            "#2": "INKOMST",
            "#3": "MATKONTO",
            "#4": "FRITID",
            "#5": "KREDITER",
            "#6": "BOENDE",
            "#7": "MEDIA",
            "#8": "TRANSPORT",
            "#9": "SPARANDE",
            "#10": "OVRIGT",
        }

        self.show_month_tab()

    def _configure_treeview_style(self):
        style = ttk.Style(self)
        style.configure(
            "Budget.Treeview",
            background="#FFFFFF",
            foreground=TEXT_COLOR,
            fieldbackground="#FFFFFF",
            rowheight=30,
            borderwidth=0,
            relief="flat",
            font=("Segoe UI", 10),
        )
        style.configure(
            "Budget.Treeview.Heading",
            background="#F3F7FD",
            foreground=TEXT_COLOR,
            relief="flat",
            borderwidth=0,
            font=("Segoe UI", 10, "bold"),
            padding=(8, 8),
        )

    def _clear_content(self):
        for child in self.content.winfo_children():
            child.destroy()
        self.month_tree = None
        self.year_tree = None

    def _set_tab_buttons(self, active_tab):
        if active_tab == "month":
            self.btn_month.configure(bg="#4A90E2", fg="white", relief="flat", bd=0, font=("Segoe UI", 10, "bold"))
            self.btn_year.configure(bg="#FFFFFF", fg=TEXT_COLOR, relief="solid", bd=1, font=("Segoe UI", 10))
        else:
            self.btn_year.configure(bg="#4A90E2", fg="white", relief="flat", bd=0, font=("Segoe UI", 10, "bold"))
            self.btn_month.configure(bg="#FFFFFF", fg=TEXT_COLOR, relief="solid", bd=1, font=("Segoe UI", 10))

    def show_month_tab(self):
        self._clear_content()
        self._set_tab_buttons("month")

        tk.Label(
            self.content,
            text=f"Sammanställning per månad • {self.current_year}",
            bg="#FFFFFF",
            fg=TEXT_COLOR,
            font=("Segoe UI", 13, "bold"),
        ).pack(anchor="w", pady=(0, 4))

        tk.Label(
            self.content,
            text="Dubbelklicka på ett belopp för att se underkategorierna.",
            bg="#FFFFFF",
            fg=MUTED_TEXT,
            font=("Segoe UI", 9),
        ).pack(anchor="w", pady=(0, 12))

        table_wrap = tk.Frame(self.content, bg="#FFFFFF")
        table_wrap.pack(fill="both", expand=True)

        columns = [
            "månad", "inkomst", "matkonto", "fritid", "krediter",
            "boende", "media", "transport", "sparande", "ovrigt", "resultat",
        ]

        headings = {
            "månad": "Månad",
            "inkomst": "Inkomst",
            "matkonto": "Matkonto",
            "fritid": "Fritid",
            "krediter": "Krediter",
            "boende": "Boende",
            "media": "Media",
            "transport": "Transport",
            "sparande": "Sparande",
            "ovrigt": "Övrigt",
            "resultat": "Resultat",
        }

        tree = ttk.Treeview(table_wrap, columns=columns, show="headings", style="Budget.Treeview")

        for key in columns:
            tree.heading(key, text=headings[key], anchor="center")
            tree.column(key, width=120 if key != "månad" else 160, anchor="w" if key == "månad" else "e", stretch=False)

        for row in self.monthly_rows:
            tree.insert(
                "",
                "end",
                values=[
                    row["month_label"],
                    format_amount_display(row.get("INKOMST", 0)),
                    format_amount_display(row.get("MATKONTO", 0)),
                    format_amount_display(row.get("FRITID", 0)),
                    format_amount_display(row.get("KREDITER", 0)),
                    format_amount_display(row.get("BOENDE", 0)),
                    format_amount_display(row.get("MEDIA", 0)),
                    format_amount_display(row.get("TRANSPORT", 0)),
                    format_amount_display(row.get("SPARANDE", 0)),
                    format_amount_display(row.get("OVRIGT", 0)),
                    format_amount_display(row.get("RESULTAT", 0)),
                ],
            )

        tree.bind("<Double-1>", self._open_month_detail)

        yscroll = ttk.Scrollbar(table_wrap, orient="vertical", command=tree.yview)
        xscroll = ttk.Scrollbar(table_wrap, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)

        tree.pack(side="top", fill="both", expand=True)
        xscroll.pack(side="bottom", fill="x")
        yscroll.pack(side="right", fill="y")

        self.month_tree = tree

    def show_year_tab(self):
        self._clear_content()
        self._set_tab_buttons("year")

        years = self.year_matrix["years"]
        rows = self.year_matrix["rows"]

        tk.Label(
            self.content,
            text="År vs År",
            bg="#FFFFFF",
            fg=TEXT_COLOR,
            font=("Segoe UI", 13, "bold"),
        ).pack(anchor="w", pady=(0, 4))

        tk.Label(
            self.content,
            text="Dubbelklicka på ett belopp för att se underkategorierna för valt år.",
            bg="#FFFFFF",
            fg=MUTED_TEXT,
            font=("Segoe UI", 9),
        ).pack(anchor="w", pady=(0, 12))

        table_wrap = tk.Frame(self.content, bg="#FFFFFF")
        table_wrap.pack(fill="both", expand=True)

        columns = ["kategori"] + [str(y) for y in years]
        tree = ttk.Treeview(table_wrap, columns=columns, show="headings", style="Budget.Treeview")

        tree.heading("kategori", text="Huvudkategori", anchor="center")
        tree.column("kategori", width=180, anchor="w", stretch=False)

        for year in years:
            tree.heading(str(year), text=str(year), anchor="center")
            tree.column(str(year), width=120, anchor="e", stretch=False)

        for row in rows:
            values = [row["category_label"]]
            for year in years:
                values.append(format_amount_display(row["values"].get(year, 0)))
            tree.insert("", "end", values=values)

        tree.bind("<Double-1>", self._open_year_detail)

        yscroll = ttk.Scrollbar(table_wrap, orient="vertical", command=tree.yview)
        xscroll = ttk.Scrollbar(table_wrap, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)

        tree.pack(side="top", fill="both", expand=True)
        xscroll.pack(side="bottom", fill="x")
        yscroll.pack(side="right", fill="y")

        self.year_tree = tree

    def _open_month_detail(self, event):
        if not self.month_tree:
            return

        row_id = self.month_tree.identify_row(event.y)
        col_id = self.month_tree.identify_column(event.x)

        if not row_id or col_id not in self.month_column_map:
            return

        values = self.month_tree.item(row_id, "values")
        if not values:
            return

        month_label_text = values[0]
        section_name = self.month_column_map[col_id]
        rows = self.master_app.get_detail_rows_for_month_label(month_label_text, section_name)

        DetailWindow(
            self,
            f"{SECTION_LABELS.get(section_name, section_name)} — {month_label_text}",
            rows,
        )

    def _open_year_detail(self, event):
        if not self.year_tree:
            return

        row_id = self.year_tree.identify_row(event.y)
        col_id = self.year_tree.identify_column(event.x)

        if not row_id or col_id == "#1":
            return

        values = self.year_tree.item(row_id, "values")
        if not values:
            return

        category_label = values[0]
        if category_label == SECTION_LABELS["RESULTAT"]:
            return

        year_index = int(col_id.replace("#", "")) - 2
        years = self.year_matrix["years"]

        if year_index < 0 or year_index >= len(years):
            return

        year = years[year_index]

        category_key = None
        for key, label in SECTION_LABELS.items():
            if label == category_label:
                category_key = key
                break

        if not category_key or category_key == "RESULTAT":
            return

        rows = self.master_app.get_detail_rows_for_year(year, category_key)

        DetailWindow(
            self,
            f"{SECTION_LABELS.get(category_key, category_key)} — {year}",
            rows,
            helper_text="Visar totalsumma per underkategori för valt år.",
        )


class BudgetApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title(f"{APP_NAME} {APP_VERSION}".strip())
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.configure(bg=APP_BG)

        self.logo_label = None
        self.logo_image = None

        self.clock_canvas = None
        self.clock_job = None
        self.clock_date_var = tk.StringVar(value="")

        self.month_var = tk.StringVar()

        self.sections_canvas = None
        self.sections_inner = None
        self.sections_window = None

        self.row_vars = {}
        self.row_entries = {}
        self.entry_order = []
        self.section_total_labels = {}
        self.summary_value_labels = {}
        self.row_underlines = {}

        self.month_combo = None
        self.month_label_map = {}

        self.settings = self._load_settings()
        self.months_data = self._load_months()

        self._ensure_settings_defaults()
        self._ensure_trial_started()
        self._auto_load_saved_license()
        self._remove_empty_duplicate_months()
        self._save_all_data()

        if self._is_trial_expired():
            messagebox.showerror(
                "Trial slut",
                "Din testperiod har gått ut.\n\nKöp PRO-versionen för att fortsätta använda programmet."
            )
            self.destroy()
            return

        self._configure_styles()
        self._build_ui()
        self._refresh_totals()

        self.bind_all("<MouseWheel>", self._on_mousewheel_windows)
        self.bind_all("<Button-4>", self._on_mousewheel_linux_up)
        self.bind_all("<Button-5>", self._on_mousewheel_linux_down)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _is_trial_expired(self):
        if self.settings.get("license_type") == "PRO":
            return False

        expiry_date_str = self.settings.get("expiry_date")
        if not expiry_date_str:
            return False

        try:
            expiry_date = datetime.fromisoformat(expiry_date_str).date()
            today = datetime.now().date()
            return today > expiry_date
        except Exception:
            return False

    def _get_local_license_path(self):
        return LOCAL_LICENSE_FILE

    def _save_local_license(self, license_key, status):
        data = {
            "license_key": str(license_key).strip().upper(),
            "status": str(status).strip().upper(),
            "machine_id": self._get_machine_id(),
            "saved_at": datetime.now().isoformat()
        }

        try:
            save_json(self._get_local_license_path(), data)
        except Exception as e:
            print("Kunde inte spara lokal licens:", e)

    def _load_local_license(self):
        data = load_json(self._get_local_license_path(), None)
        if isinstance(data, dict) and data.get("license_key"):
            return data

        # Fallback för äldre installationer som redan sparat licens i settings
        if self.settings.get("license_type") == "PRO" and self.settings.get("license_key"):
            return {
                "license_key": self.settings.get("license_key", ""),
                "status": "PRO",
                "machine_id": self.settings.get("activated_machine_id", "")
            }

        return None

    def _clear_local_license(self):
        try:
            path = self._get_local_license_path()
            if Path(path).exists():
                Path(path).unlink()
        except Exception as e:
            print("Kunde inte ta bort lokal licens:", e)

    def _auto_load_saved_license(self):
        saved = self._load_local_license()
        if not saved:
            return

        key = str(saved.get("license_key", "")).strip().upper()
        if not key:
            return

        valid, result = self._validate_license_key(key)
        message = str(result.get("message", ""))

        if valid:
            status = str(result.get("status", "PRO")).upper()
            self.settings["license_type"] = status
            self.settings["license_key"] = key
            self.settings["activated_machine_id"] = self._get_machine_id()
            self._save_local_license(key, status)
            self._save_settings()
            print("Sparad licens verifierad:", status)
            return

        # Om servern tillfälligt inte svarar, behåll lokal licensstatus tills vidare
        if "Kunde inte ansluta till licensservern" in message and saved.get("status", "").upper() == "PRO":
            self.settings["license_type"] = "PRO"
            self.settings["license_key"] = key
            self.settings["activated_machine_id"] = self._get_machine_id()
            self._save_settings()
            print("Licensservern kunde inte nås. Behåller sparad PRO-status tillfälligt.")
            return

        self.settings["license_type"] = "Trial"
        self.settings["license_key"] = ""
        self.settings["activated_machine_id"] = ""
        self._clear_local_license()
        self._save_settings()
        print("Sparad licens är inte längre giltig.")

    def _validate_license_key(self, key):
        try:
            url = f"{LICENSE_SERVER_URL}/verify"

            payload = {
                "license_key": key.strip().upper(),
                "machine_id": self._get_machine_id()
            }

            response = requests.post(url, json=payload, timeout=5)
            data = response.json()

            return data.get("valid", False), data

        except Exception as e:
            return False, {"message": f"Kunde inte ansluta till licensservern: {e}"}

    def _get_machine_id(self):
        raw = str(uuid.getnode()) + os.getenv("COMPUTERNAME", "")
        return hashlib.sha256(raw.encode()).hexdigest()

    def f(self, size, bold=False):
        weight = "bold" if bold else "normal"
        return ("Segoe UI", size, weight)

    def _configure_styles(self):
        style = ttk.Style(self)
        try:
            style.theme_use("vista")
        except Exception:
            pass

        style.configure(
            "Modern.TCombobox",
            padding=4,
            fieldbackground="#FFFFFF",
            background="#FFFFFF",
            foreground="#000000",
        )

    def _load_settings(self):
        data = load_json(SETTINGS_FILE, {})
        return data if isinstance(data, dict) else {}

    def _load_months(self):
        data = load_json(MONTHS_FILE, {})
        return data if isinstance(data, dict) else {}

    def _ensure_settings_defaults(self):
        if not isinstance(self.settings.get("category_templates"), dict):
            self.settings["category_templates"] = {section: [] for section in SECTION_ORDER}

        if not isinstance(self.settings.get("hidden_templates"), dict):
            self.settings["hidden_templates"] = {section: [] for section in SECTION_ORDER}

        for section in SECTION_ORDER:
            if section not in self.settings["category_templates"]:
                self.settings["category_templates"][section] = []
            if section not in self.settings["hidden_templates"]:
                self.settings["hidden_templates"][section] = []

        if "license_type" not in self.settings:
            self.settings["license_type"] = "Trial"

        if "first_run_date" not in self.settings:
            self.settings["first_run_date"] = ""

        if "expiry_date" not in self.settings:
            self.settings["expiry_date"] = ""

        if "license_key" not in self.settings:
            self.settings["license_key"] = ""

        if "activated_machine_id" not in self.settings:
            self.settings["activated_machine_id"] = ""

    def _ensure_trial_started(self):
        if not self.settings.get("license_type"):
            self.settings["license_type"] = "Trial"

        if "license_key" not in self.settings:
            self.settings["license_key"] = ""

        if self.settings.get("license_type") == "PRO":
            return

        if not self.settings.get("first_run_date"):
            today = datetime.now().date()
            expiry = today + timedelta(days=75)

            self.settings["first_run_date"] = today.isoformat()
            self.settings["expiry_date"] = expiry.isoformat()

    def _remove_empty_duplicate_months(self):
        seen = {}
        keys_to_delete = []

        for key in sort_month_keys(self.months_data):
            month_data = self.months_data.get(key, {})
            name = str(month_data.get("name", "")).strip().lower()
            rows = month_data.get("rows", [])

            has_values = any(float(r.get("actual", 0) or 0) != 0 for r in rows)

            if not name:
                continue

            if name not in seen:
                seen[name] = (key, has_values)
                continue

            first_key, first_has_values = seen[name]

            if not has_values:
                keys_to_delete.append(key)
            elif not first_has_values:
                keys_to_delete.append(first_key)
                seen[name] = (key, has_values)
            else:
                keys_to_delete.append(key)

        if not keys_to_delete:
            return

        current_month = self.settings.get("current_month")
        for key in keys_to_delete:
            if current_month == key:
                self.settings["current_month"] = None
            self.months_data.pop(key, None)

        if self.settings.get("current_month") is None and self.months_data:
            self.settings["current_month"] = sort_month_keys(self.months_data)[0]

    def _save_settings(self):
        if SETTINGS_FILE.exists():
            create_backup(SETTINGS_FILE, "settings")
        save_json(SETTINGS_FILE, self.settings)

    def _save_months(self):
        if MONTHS_FILE.exists():
            create_backup(MONTHS_FILE, "months")
        save_json(MONTHS_FILE, self.months_data)

    def _save_all_data(self):
        self._save_months()
        self._save_settings()

    def _get_current_month_key(self):
        current_month = self.settings.get("current_month")
        if current_month and current_month in self.months_data:
            return current_month
        if self.months_data:
            return sort_month_keys(self.months_data)[0]
        return None

    def _get_current_month_data(self):
        key = self._get_current_month_key()
        if not key:
            return {}
        return self.months_data.get(key, {})

    def _get_current_month_label(self):
        data = self._get_current_month_data()
        if not data:
            return "Ingen månad vald"
        return data.get("name", "Ingen månad vald")

    def _get_all_rows_for_current_month(self):
        current = self._get_current_month_data()
        if not current:
            return []
        return current.get("rows", [])

    def _get_rows_for_current_month(self):
        return [row for row in self._get_all_rows_for_current_month() if not row.get("hidden", False)]

    def _next_row_id(self):
        month_data = self._get_current_month_data()
        if not month_data:
            return "r1"
        next_row_id = int(month_data.get("next_row_id", 1))
        month_data["next_row_id"] = next_row_id + 1
        return f"r{next_row_id}"

    def _get_default_templates(self):
        settings_templates = self.settings.get("category_templates")
        if isinstance(settings_templates, dict):
            templates = {}
            for section in SECTION_ORDER:
                values = settings_templates.get(section, [])
                templates[section] = [str(v).strip() for v in values if str(v).strip()]
            return templates

        return {section: [] for section in SECTION_ORDER}

    def _get_hidden_templates(self):
        hidden = self.settings.get("hidden_templates")
        if isinstance(hidden, dict):
            cleaned = {}
            for section in SECTION_ORDER:
                values = hidden.get(section, [])
                cleaned[section] = [str(v).strip() for v in values if str(v).strip()]
            return cleaned
        return {section: [] for section in SECTION_ORDER}

    def _sync_global_templates_from_current_month(self):
        month_data = self._get_current_month_data()
        if not month_data:
            self.settings["category_templates"] = {section: [] for section in SECTION_ORDER}
            self.settings["hidden_templates"] = {section: [] for section in SECTION_ORDER}
            self._save_settings()
            return

        templates = {section: [] for section in SECTION_ORDER}
        hidden_templates = {section: [] for section in SECTION_ORDER}

        for section in SECTION_ORDER:
            section_rows = [
                row for row in self._get_all_rows_for_current_month()
                if row.get("section", "OVRIGT") == section
            ]

            for row in section_rows:
                category = str(row.get("category", "")).strip()
                if not category:
                    continue
                templates[section].append(category)
                if row.get("hidden", False):
                    hidden_templates[section].append(category)

        self.settings["category_templates"] = templates
        self.settings["hidden_templates"] = hidden_templates
        self._save_settings()

    def _set_section_rows_for_current_month(self, section, new_section_rows):
        month_data = self._get_current_month_data()
        if not month_data:
            return

        current_rows = self._get_all_rows_for_current_month()
        grouped = {sec: [] for sec in SECTION_ORDER}

        for row in current_rows:
            sec = row.get("section", "OVRIGT")
            if sec not in grouped:
                sec = "OVRIGT"
            grouped[sec].append(row)

        grouped[section] = new_section_rows

        rebuilt = []
        for sec in SECTION_ORDER:
            rebuilt.extend(grouped.get(sec, []))

        month_data["rows"] = rebuilt

    def _create_empty_month_data(self, month_name):
        templates = self._get_default_templates()
        hidden_templates = self._get_hidden_templates()

        rows = []
        row_id = 1

        for section in SECTION_ORDER:
            items = templates.get(section, [])
            hidden_items = set(hidden_templates.get(section, []))

            for category in items:
                rows.append(
                    {
                        "id": f"r{row_id}",
                        "section": section,
                        "category": category,
                        "actual": 0.0,
                        "hidden": category in hidden_items,
                    }
                )
                row_id += 1

        return {
            "name": month_name,
            "rows": rows,
            "next_row_id": row_id,
        }

    def _refresh_month_selector(self):
        month_keys = sort_month_keys(self.months_data)
        labels = [self.months_data[k].get("name", k) for k in month_keys]
        self.month_label_map = dict(zip(labels, month_keys))
        if self.month_combo is not None:
            self.month_combo["values"] = labels
            self.month_var.set(self._get_current_month_label())

    def _on_month_selected(self, event=None):
        selected_label = self.month_var.get()
        month_key = self.month_label_map.get(selected_label)
        if not month_key:
            return
        self.settings["current_month"] = month_key
        self._save_settings()
        self._rebuild_main_view()

    def _build_ui(self):
        root = tk.Frame(self, bg=APP_BG)
        root.pack(fill="both", expand=True, padx=14, pady=14)

        app_shell = tk.Frame(root, bg=WORKSPACE_BG, bd=0, highlightthickness=0)
        app_shell.pack(fill="both", expand=True)

        self.sidebar = tk.Frame(app_shell, bg=SIDEBAR_BG, width=230)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.content = tk.Frame(app_shell, bg=WORKSPACE_BG)
        self.content.pack(side="left", fill="both", expand=True)

        self._build_sidebar()
        self._build_content()

    def _rebuild_main_view(self):
        if self.clock_job:
            try:
                self.after_cancel(self.clock_job)
            except Exception:
                pass
            self.clock_job = None

        for widget in self.sidebar.winfo_children():
            widget.destroy()
        for widget in self.content.winfo_children():
            widget.destroy()

        self.row_vars.clear()
        self.row_entries.clear()
        self.entry_order.clear()
        self.section_total_labels.clear()
        self.summary_value_labels.clear()
        self.row_underlines.clear()

        self.logo_label = None
        self.logo_image = None
        self.sections_canvas = None
        self.sections_inner = None
        self.sections_window = None
        self.clock_canvas = None

        self._build_sidebar()
        self._build_content()
        self._refresh_totals()

    def _build_sidebar(self):
        top = tk.Frame(self.sidebar, bg=SIDEBAR_BG, height=18)
        top.pack(fill="x")
        top.pack_propagate(False)

        self._build_clock()

        divider = tk.Frame(self.sidebar, bg=SIDEBAR_BG_DARK, height=1)
        divider.pack(fill="x", pady=(12, 8))

        stats_wrap = tk.Frame(self.sidebar, bg=SIDEBAR_BG)
        stats_wrap.pack(fill="x", padx=12, pady=(86, 14))

        tk.Label(
            stats_wrap,
            text="ÖVERSIKT",
            bg=SIDEBAR_BG,
            fg="#FFFFFF",
            font=self.f(11, True),
        ).pack(anchor="w", padx=6, pady=(0, 8))

        blocks = [
            ("Inkomster", "actual_income"),
            ("Utgifter", "actual_expense"),
            ("Delsumma", "partial_result"),
            ("Sparande", "actual_savings"),
            ("Resultat", "actual_result"),
        ]

        for label, key in blocks:
            box = tk.Frame(stats_wrap, bg=SIDEBAR_BG)
            box.pack(fill="x", pady=4)

            tk.Label(
                box,
                text=label,
                bg=SIDEBAR_BG,
                fg="#C7CCF1",
                font=self.f(10),
            ).pack(anchor="w", padx=6, pady=(4, 0))

            value_label = tk.Label(
                box,
                text="0 kr",
                bg=SIDEBAR_BG,
                fg=KPI_VALUE_COLOR,
                font=self.f(13, True),
            )
            value_label.pack(anchor="w", padx=6, pady=(0, 4))
            self.summary_value_labels[key] = value_label

        tk.Label(
            stats_wrap,
            text="Riktig data används",
            bg=SIDEBAR_BG,
            fg=SIDEBAR_MUTED,
            font=self.f(9),
        ).pack(anchor="w", padx=6, pady=(8, 0))

    def _build_clock(self):
        wrap = tk.Frame(self.sidebar, bg=SIDEBAR_BG)
        wrap.pack(fill="x", pady=(8, 6))

        self.clock_canvas = tk.Canvas(
            wrap,
            width=170,
            height=170,
            bg=SIDEBAR_BG,
            highlightthickness=0,
            bd=0,
        )
        self.clock_canvas.pack(anchor="center")

        tk.Label(
            wrap,
            textvariable=self.clock_date_var,
            bg=SIDEBAR_BG,
            fg="#FFFFFF",
            font=("Segoe UI", 10, "bold"),
            wraplength=210,
            justify="center",
        ).pack(anchor="center", pady=(4, 0))

        self._update_clock()

    def _update_clock(self):
        now = datetime.now()

        weekdays = ["Måndag", "Tisdag", "Onsdag", "Torsdag", "Fredag", "Lördag", "Söndag"]
        months = ["Januari", "Februari", "Mars", "April", "Maj", "Juni", "Juli", "Augusti", "September", "Oktober", "November", "December"]

        self.clock_date_var.set(f"{weekdays[now.weekday()]} {now.day} {months[now.month - 1]} {now.year}")

        canvas = self.clock_canvas
        canvas.delete("all")

        w = 170
        h = 170
        cx = w / 2
        cy = h / 2
        r = 60

        canvas.create_oval(cx - r - 10, cy - r - 10, cx + r + 10, cy + r + 10, fill="#b8932f", outline="#7a5f18", width=2)
        canvas.create_oval(cx - r - 4, cy - r - 4, cx + r + 4, cy + r + 4, fill="#d7bf72", outline="#9b7b21", width=2)
        canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill="#f7f1db", outline="#d5cba7", width=2)

        for i in range(60):
            angle = math.radians(i * 6 - 90)
            outer = r - 4
            inner = r - 15 if i % 5 == 0 else r - 8
            width = 2 if i % 5 == 0 else 1
            color = "#3f3a2b" if i % 5 == 0 else "#7e7a6a"

            x1 = cx + math.cos(angle) * inner
            y1 = cy + math.sin(angle) * inner
            x2 = cx + math.cos(angle) * outer
            y2 = cy + math.sin(angle) * outer
            canvas.create_line(x1, y1, x2, y2, fill=color, width=width)

        positions = {
            "12": (cx, cy - r + 20),
            "3": (cx + r - 18, cy),
            "6": (cx, cy + r - 18),
            "9": (cx - r + 18, cy),
        }
        for txt, (x, y) in positions.items():
            canvas.create_text(x, y, text=txt, fill="#2e2b23", font=("Times New Roman", 10, "bold"))

        sec = now.second
        minute = now.minute + sec / 60
        hour = (now.hour % 12) + minute / 60

        sec_angle = math.radians(sec * 6 - 90)
        min_angle = math.radians(minute * 6 - 90)
        hour_angle = math.radians(hour * 30 - 90)

        hour_x = cx + math.cos(hour_angle) * (r * 0.45)
        hour_y = cy + math.sin(hour_angle) * (r * 0.45)
        min_x = cx + math.cos(min_angle) * (r * 0.68)
        min_y = cy + math.sin(min_angle) * (r * 0.68)
        sec_x = cx + math.cos(sec_angle) * (r * 0.82)
        sec_y = cy + math.sin(sec_angle) * (r * 0.82)

        canvas.create_line(cx, cy, hour_x, hour_y, fill="#151515", width=6, capstyle=tk.ROUND)
        canvas.create_line(cx, cy, min_x, min_y, fill="#151515", width=4, capstyle=tk.ROUND)
        canvas.create_line(cx, cy, sec_x, sec_y, fill="#c62828", width=1)
        canvas.create_oval(cx - 5, cy - 5, cx + 5, cy + 5, fill="#8d6a16", outline="#6f5112")

        self.clock_job = self.after(1000, self._update_clock)

    def _toolbar_button(self, parent, text, command):
        outer = tk.Frame(
            parent,
            bg=TOPBAR_BUTTON_BORDER_DARK,
            highlightthickness=1,
            highlightbackground=TOPBAR_BUTTON_BORDER_DARK,
        )

        inner = tk.Frame(outer, bg=TOPBAR_BUTTON_BORDER_LIGHT)
        inner.pack(fill="both", expand=True, padx=(1, 0), pady=(1, 0))

        btn = tk.Button(
            inner,
            text=text,
            command=command,
            bg=TOPBAR_BUTTON_BG,
            fg=TOPBAR_BUTTON_FG,
            activebackground=TOPBAR_BUTTON_ACTIVE,
            activeforeground=TOPBAR_BUTTON_FG,
            relief="flat",
            bd=0,
            highlightthickness=0,
            font=("Segoe UI", 9),
            padx=10,
            pady=4,
            cursor="hand2",
        )
        btn.pack()

        return outer

    def _toolbar_separator(self, parent):
        sep = tk.Frame(parent, bg=TOPBAR_BG, width=8)
        line_dark = tk.Frame(sep, bg=TOPBAR_SEPARATOR, width=1)
        line_dark.pack(side="left", fill="y", pady=4)
        line_light = tk.Frame(sep, bg="#FFFFFF", width=1)
        line_light.pack(side="left", fill="y", pady=4)
        return sep

    def _build_content(self):
        topbar = tk.Frame(
            self.content,
            bg=TOPBAR_BG,
            height=52,
            highlightthickness=1,
            highlightbackground=TOPBAR_BORDER,
        )
        topbar.pack(fill="x")
        topbar.pack_propagate(False)

        inner_topbar = tk.Frame(topbar, bg=TOPBAR_BG)
        inner_topbar.pack(fill="both", expand=True, padx=8, pady=6)

        toolbar_left = tk.Frame(inner_topbar, bg=TOPBAR_BG)
        toolbar_left.pack(side="left")

        self._toolbar_button(toolbar_left, "Ny månad", self.create_new_month).pack(side="left")
        self._toolbar_button(toolbar_left, "Visa sparad månad", self.show_saved_month_dialog).pack(side="left", padx=(4, 0))
        self._toolbar_separator(toolbar_left).pack(side="left", padx=8)
        self._toolbar_button(toolbar_left, "Sammanställning", self.open_summary_window).pack(side="left")
        self._toolbar_button(toolbar_left, "Visa dolda underkategorier", self.edit_hidden_rows).pack(side="left", padx=(4, 0))
        self._toolbar_separator(toolbar_left).pack(side="left", padx=8)
        self._toolbar_button(toolbar_left, "Aktivera licens", self.activate_license_from_menu).pack(side="left")
        self._toolbar_button(toolbar_left, "Licensstatus", self.show_license_status).pack(side="left", padx=(4, 0))
        self._toolbar_separator(toolbar_left).pack(side="left", padx=8)
        self._toolbar_button(toolbar_left, "Backup", self.restore_latest_backup).pack(side="left")
        self._toolbar_button(toolbar_left, "Exportera månad", self.export_current_month).pack(side="left", padx=(4, 0))

        toolbar_right = tk.Frame(inner_topbar, bg=TOPBAR_BG)
        toolbar_right.pack(side="right")

        tk.Label(
            toolbar_right,
            text="Månad",
            bg=TOPBAR_BG,
            fg="#000000",
            font=("Segoe UI", 9),
        ).pack(side="left", padx=(0, 8))

        self.month_combo = ttk.Combobox(
            toolbar_right,
            textvariable=self.month_var,
            state="readonly",
            width=18,
            style="Modern.TCombobox",
        )
        self.month_combo.pack(side="left")
        self.month_combo.bind("<<ComboboxSelected>>", self._on_month_selected)
        self._refresh_month_selector()

        content_pad = tk.Frame(self.content, bg=WORKSPACE_BG)
        content_pad.pack(fill="both", expand=True, padx=18, pady=18)

        hero = tk.Frame(content_pad, bg=PANEL_BG, highlightthickness=1, highlightbackground=PANEL_BORDER)
        hero.pack(fill="x", pady=(0, 4))

        hero_inner = tk.Frame(hero, bg=PANEL_BG)
        hero_inner.pack(fill="x", padx=18, pady=0)

        self.logo_label = tk.Label(hero_inner, bg=PANEL_BG)
        self.logo_label.pack(anchor="w", pady=(4, 6))
        self._load_logo()

        month_panel = tk.Frame(content_pad, bg=PANEL_BG, highlightthickness=1, highlightbackground=PANEL_BORDER)
        month_panel.pack(fill="x", pady=(0, 12))

        month_inner = tk.Frame(month_panel, bg=PANEL_BG)
        month_inner.pack(fill="both", expand=True, padx=18, pady=14)

        tk.Label(
            month_inner,
            text=self._get_current_month_label(),
            bg=PANEL_BG,
            fg=TITLE_RED,
            font=self.f(24, True),
        ).pack(anchor="w")

        subtitle_text = "Månadsplanering" if self._get_current_month_key() else "Skapa din första månad för att börja"

        tk.Label(
            month_inner,
            text=subtitle_text,
            bg=PANEL_BG,
            fg=MUTED_TEXT,
            font=self.f(10),
        ).pack(anchor="w", pady=(4, 0))

        workspace = tk.Frame(content_pad, bg=PANEL_BG, highlightthickness=1, highlightbackground=PANEL_BORDER)
        workspace.pack(fill="both", expand=True)

        tk.Label(
            workspace,
            text="Huvudkategorier",
            bg=PANEL_BG,
            fg=TEXT_COLOR,
            font=self.f(12, True),
        ).pack(anchor="w", padx=18, pady=(14, 10))

        if not self._get_current_month_key():
            empty_wrap = tk.Frame(workspace, bg=PANEL_BG)
            empty_wrap.pack(fill="both", expand=True, padx=24, pady=(0, 24))

            tk.Label(
                empty_wrap,
                text="Inga månader skapade ännu.",
                bg=PANEL_BG,
                fg=TEXT_COLOR,
                font=self.f(12, True),
            ).pack(anchor="w", pady=(12, 6))

            tk.Label(
                empty_wrap,
                text="Klicka på 'Ny månad' för att skapa en tom månad utan underkategorier och belopp.",
                bg=PANEL_BG,
                fg=MUTED_TEXT,
                font=self.f(10),
                wraplength=700,
                justify="left",
            ).pack(anchor="w")
            return

        canvas_wrap = tk.Frame(workspace, bg=PANEL_BG)
        canvas_wrap.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.sections_canvas = tk.Canvas(canvas_wrap, bg=PANEL_BG, highlightthickness=0, bd=0)
        self.sections_canvas.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(canvas_wrap, orient="vertical", command=self.sections_canvas.yview)
        scrollbar.pack(side="right", fill="y")
        self.sections_canvas.configure(yscrollcommand=scrollbar.set)

        self.sections_inner = tk.Frame(self.sections_canvas, bg=PANEL_BG)
        self.sections_window = self.sections_canvas.create_window((0, 0), window=self.sections_inner, anchor="nw")

        self.sections_inner.bind("<Configure>", self._on_sections_frame_configure)
        self.sections_canvas.bind("<Configure>", self._on_sections_canvas_configure)

        self._build_sections(self.sections_inner)

    def _build_sections(self, parent):
        rows = self._get_rows_for_current_month()
        grouped = {section: [] for section in SECTION_ORDER}
        for row in rows:
            section = row.get("section", "OVRIGT")
            if section not in grouped:
                section = "OVRIGT"
            grouped.setdefault(section, []).append(row)

        grid = tk.Frame(parent, bg=PANEL_BG)
        grid.pack(fill="both", expand=True)

        for i in range(3):
            grid.grid_columnconfigure(i, weight=1, uniform="sectioncol")

        for index, section in enumerate(SECTION_ORDER):
            row_index = index // 3
            col_index = index % 3

            shell = tk.Frame(grid, bg=PANEL_BG)
            shell.grid(row=row_index, column=col_index, sticky="nsew", padx=8, pady=8)

            card = tk.Frame(shell, bg=CARD_BG, highlightthickness=1, highlightbackground=CARD_BORDER)
            card.pack(fill="both", expand=True)

            self._build_section_card(card, section, grouped.get(section, []))

    def _build_section_card(self, card, section, section_rows):
        header = tk.Frame(card, bg=CARD_HEADER_BG, height=38)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text=SECTION_LABELS.get(section, section),
            bg=CARD_HEADER_BG,
            fg=CARD_HEADER_TEXT,
            font=self.f(10, True),
        ).pack(side="left", padx=12, pady=10)

        total_label = tk.Label(
            header,
            text="0 kr",
            bg=CARD_HEADER_BG,
            fg=CARD_HEADER_TEXT,
            font=self.f(10, True),
        )
        total_label.pack(side="right", padx=12, pady=10)
        self.section_total_labels[section] = total_label

        body = tk.Frame(card, bg=CARD_BG)
        body.pack(fill="both", expand=True, padx=10, pady=10)

        tk.Button(
            body,
            text="Redigera underkategorier",
            command=lambda s=section: self.open_edit_subcategories_dialog(s),
            font=self.f(8),
            bg=BUTTON_BG_SECONDARY,
            fg=BUTTON_FG_SECONDARY,
            activebackground="#E2E8F0",
            activeforeground=BUTTON_FG_SECONDARY,
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=10,
            pady=4,
        ).pack(anchor="w", pady=(0, 8))

        if section_rows:
            for i, row in enumerate(section_rows):
                self._build_row(body, row, i)
        else:
            tk.Label(
                body,
                text="Inga underkategorier ännu",
                bg=CARD_BG,
                fg=MUTED_TEXT,
                font=self.f(10),
            ).pack(anchor="w", pady=4)

    def _build_row(self, parent, row, i):
        bg = ROW_BG if i % 2 == 0 else ROW_ALT_BG
        row_id = row.get("id")

        row_frame = tk.Frame(parent, bg=bg, height=34)
        row_frame.pack(fill="x", pady=1)
        row_frame.pack_propagate(False)

        name_label = tk.Label(
            row_frame,
            text=row.get("category", ""),
            bg=bg,
            fg=TEXT_COLOR,
            font=self.f(9),
            anchor="w",
        )
        name_label.pack(side="left", fill="x", expand=True, padx=(12, 8), pady=8)

        value_var = tk.StringVar(value=format_amount_display(row.get("actual", 0)))
        self.row_vars[row_id] = value_var

        entry_wrap = tk.Frame(row_frame, bg=bg)
        entry_wrap.pack(side="right", padx=(8, 12), pady=(5, 3))

        entry = tk.Entry(
            entry_wrap,
            textvariable=value_var,
            width=10,
            justify="right",
            font=self.f(9),
            bd=0,
            relief="flat",
            highlightthickness=0,
            bg=INPUT_BG,
            fg=TEXT_COLOR,
            insertbackground=TEXT_COLOR,
        )
        entry.pack(anchor="e")
        self.row_entries[row_id] = entry
        self.entry_order.append(row_id)

        underline = tk.Frame(entry_wrap, height=1, bg=INPUT_UNDERLINE)
        underline.pack(fill="x", pady=(2, 0))
        self.row_underlines[row_id] = underline

        def set_row_bg(color):
            row_frame.config(bg=color)
            name_label.config(bg=color)
            entry_wrap.config(bg=color)

        def on_enter(_):
            set_row_bg(ROW_HOVER)

        def on_leave(_):
            if entry.focus_get() == entry:
                set_row_bg(ROW_HOVER)
            else:
                set_row_bg(bg)

        def on_focus_in(_):
            set_row_bg(ROW_HOVER)
            underline.config(bg=INPUT_FOCUS_UNDERLINE)
            self._on_entry_focus_in(value_var)

        def on_focus_out(_):
            set_row_bg(bg)
            underline.config(bg=INPUT_UNDERLINE)
            self._commit_value(row_id, value_var)

        row_frame.bind("<Enter>", on_enter)
        row_frame.bind("<Leave>", on_leave)
        name_label.bind("<Enter>", on_enter)
        name_label.bind("<Leave>", on_leave)

        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)
        entry.bind("<Return>", lambda e, rid=row_id, var=value_var: self._commit_and_focus_next(rid, var))

    def _on_entry_focus_in(self, var):
        value = parse_amount(var.get())
        if value == int(value):
            var.set(format_amount_input(int(value)))
        else:
            var.set(format_amount_input(value))

    def _commit_value(self, row_id, var):
        if not self._get_current_month_key():
            return

        value = parse_amount(var.get())

        for row in self._get_all_rows_for_current_month():
            if row.get("id") == row_id:
                row["actual"] = value
                break

        var.set(format_amount_display(value))
        self._save_months()
        self._refresh_totals()

    def _commit_and_focus_next(self, row_id, var):
        self._commit_value(row_id, var)
        if row_id in self.entry_order:
            current_pos = self.entry_order.index(row_id)
            next_pos = current_pos + 1
            if next_pos < len(self.entry_order):
                next_row_id = self.entry_order[next_pos]
                next_entry = self.row_entries.get(next_row_id)
                if next_entry:
                    self.after_idle(lambda: self._focus_entry(next_entry))
        return "break"

    def _focus_entry(self, entry):
        entry.focus_set()
        entry.icursor(tk.END)
        entry.selection_range(0, tk.END)

    def _refresh_totals(self):
        totals = calculate_totals(self._get_all_rows_for_current_month())
        section_totals = totals["section_totals"]

        for section, total in section_totals.items():
            label = self.section_total_labels.get(section)
            if label:
                label.config(text=format_amount_display(total))

        mapping = {
            "actual_income": totals["actual_income"],
            "actual_expense": totals["actual_expense"],
            "partial_result": totals["partial_result"],
            "actual_savings": totals["actual_savings"],
            "actual_result": totals["actual_result"],
        }

        for key, value in mapping.items():
            label = self.summary_value_labels.get(key)
            if label:
                label.config(text=format_amount_display(value))
                if key == "actual_result":
                    label.config(fg=NEGATIVE_RED if value < 0 else KPI_VALUE_COLOR)

    def _load_logo(self):
        if not LOGO_FILE.exists():
            self.logo_label.config(
                text=APP_NAME,
                fg=TEXT_COLOR,
                bg=PANEL_BG,
                font=self.f(18, True),
            )
            return

        try:
            from PIL import Image, ImageTk

            img = Image.open(LOGO_FILE)
            img = img.resize((260, 80), Image.LANCZOS)

            self.logo_image = ImageTk.PhotoImage(img)
            self.logo_label.config(image=self.logo_image, text="")
        except Exception:
            self.logo_label.config(
                text=APP_NAME,
                fg=TEXT_COLOR,
                bg=PANEL_BG,
                font=self.f(18, True),
            )

    def create_new_month(self):
        if self.settings.get("license_type") != "PRO":
            if len(self.months_data) >= 6:
                messagebox.showwarning(
                    "Begränsning",
                    "I trial-versionen kan du skapa max 6 månader.",
                    parent=self
                )
                return

        current_name = self._get_current_month_label()
        parts = current_name.split()

        default_month = parts[0] if len(parts) >= 1 and current_name != "Ingen månad vald" else "Januari"
        default_year = parts[1] if len(parts) >= 2 else str(datetime.now().year)

        dialog = NewMonthDialog(self, default_month=default_month, default_year=default_year)
        self.wait_window(dialog)

        if not dialog.result:
            return

        pretty_name = dialog.result
        parts = pretty_name.split()

        if len(parts) != 2:
            messagebox.showwarning("Fel", "Ogiltigt månadsval.", parent=self)
            return

        month_name, year_text = parts[0], parts[1]

        month_number = month_name_to_number(month_name)
        if not month_number:
            messagebox.showwarning("Fel", "Ogiltig månad.", parent=self)
            return

        month_key = f"{year_text}-{month_number}"

        if month_key in self.months_data:
            messagebox.showwarning(
                "Månad finns redan",
                f"{pretty_name} är redan skapad.",
                parent=self,
            )
            return

        for existing in self.months_data.values():
            if str(existing.get("name", "")).strip().lower() == pretty_name.lower():
                messagebox.showwarning(
                    "Månad finns redan",
                    f"{pretty_name} finns redan.",
                    parent=self,
                )
                return

        self.months_data[month_key] = self._create_empty_month_data(pretty_name)
        self.settings["current_month"] = month_key

        self._save_all_data()
        self._rebuild_main_view()

    def show_saved_month_dialog(self):
        labels = [self.months_data[k].get("name", k) for k in sort_month_keys(self.months_data)]
        if not labels:
            messagebox.showinfo("Månad", "Det finns inga sparade månader.", parent=self)
            return

        dialog = SavedMonthDialog(self, labels, self._get_current_month_label())
        self.wait_window(dialog)

        if not dialog.result:
            return

        month_key = self.month_label_map.get(dialog.result)
        if not month_key:
            messagebox.showinfo("Månad", "Kunde inte hitta vald månad.", parent=self)
            return

        self.settings["current_month"] = month_key
        self._save_settings()
        self._rebuild_main_view()

    def _monthly_summary_rows_for_current_year(self):
        current_key = self._get_current_month_key()
        if not current_key:
            return [], datetime.now().year

        current_name = self._get_current_month_label()
        current_year = parse_year_from_month_name(current_name, current_key)

        rows = []
        for m_key in sort_month_keys(self.months_data):
            month_data = self.months_data[m_key]
            year = parse_year_from_month_name(month_data.get("name", m_key), m_key)
            if year != current_year:
                continue

            totals = calculate_totals(month_data.get("rows", []))
            section_totals = totals["section_totals"]

            rows.append(
                {
                    "month_label": month_data.get("name", m_key),
                    "INKOMST": section_totals.get("INKOMST", 0.0),
                    "MATKONTO": section_totals.get("MATKONTO", 0.0),
                    "FRITID": section_totals.get("FRITID", 0.0),
                    "KREDITER": section_totals.get("KREDITER", 0.0),
                    "BOENDE": section_totals.get("BOENDE", 0.0),
                    "MEDIA": section_totals.get("MEDIA", 0.0),
                    "TRANSPORT": section_totals.get("TRANSPORT", 0.0),
                    "SPARANDE": section_totals.get("SPARANDE", 0.0),
                    "OVRIGT": section_totals.get("OVRIGT", 0.0),
                    "RESULTAT": totals["actual_result"],
                }
            )

        return rows, current_year

    def _year_vs_year_matrix(self):
        by_year = {}

        for m_key, month_data in self.months_data.items():
            year = parse_year_from_month_name(month_data.get("name", m_key), m_key)
            totals = calculate_totals(month_data.get("rows", []))
            section_totals = totals["section_totals"]

            if year not in by_year:
                by_year[year] = {section: 0.0 for section in SECTION_ORDER}
                by_year[year]["RESULTAT"] = 0.0

            for section in SECTION_ORDER:
                by_year[year][section] += section_totals.get(section, 0.0)
            by_year[year]["RESULTAT"] += totals["actual_result"]

        years = sorted(by_year.keys())
        rows = []
        for key in SECTION_ORDER + ["RESULTAT"]:
            rows.append(
                {
                    "category_key": key,
                    "category_label": SECTION_LABELS.get(key, key),
                    "values": {year: by_year[year].get(key, 0.0) for year in years},
                }
            )
        return {"years": years, "rows": rows}

    def get_detail_rows_for_month_label(self, month_label_text, section_name):
        month_key = None
        for key, month_data in self.months_data.items():
            if month_data.get("name", key) == month_label_text:
                month_key = key
                break

        if not month_key:
            return []

        rows = [
            row for row in self.months_data[month_key].get("rows", [])
            if row.get("section") == section_name and not row.get("hidden", False)
        ]

        detail_rows = []
        for row in rows:
            value = float(row.get("actual", 0) or 0)
            if value != 0:
                detail_rows.append((row.get("category", ""), value))

        if not detail_rows:
            detail_rows.append(("Ingen registrerad post", 0.0))

        return detail_rows

    def get_detail_rows_for_year(self, year, section_name):
        totals_by_category = {}

        for m_key, month_data in self.months_data.items():
            row_year = parse_year_from_month_name(month_data.get("name", m_key), m_key)
            if row_year != year:
                continue

            for row in month_data.get("rows", []):
                if row.get("hidden", False):
                    continue
                if row.get("section") != section_name:
                    continue

                category = row.get("category", "")
                value = float(row.get("actual", 0) or 0)
                totals_by_category[category] = totals_by_category.get(category, 0.0) + value

        detail_rows = [(name, value) for name, value in totals_by_category.items() if value != 0]

        if not detail_rows:
            detail_rows.append(("Ingen registrerad post", 0.0))

        return detail_rows

    def open_summary_window(self):
        monthly_rows, current_year = self._monthly_summary_rows_for_current_year()
        year_matrix = self._year_vs_year_matrix()

        if not monthly_rows and not year_matrix["years"]:
            messagebox.showinfo("Sammanställning", "Det finns ännu inga sparade månader att visa.", parent=self)
            return

        SummaryWindow(self, monthly_rows, year_matrix, current_year)

    def edit_hidden_rows(self):
        if not self._get_current_month_key():
            messagebox.showinfo("Dolda underkategorier", "Det finns ingen månad vald.", parent=self)
            return

        hidden_rows = [row for row in self._get_all_rows_for_current_month() if row.get("hidden", False)]

        dialog = tk.Toplevel(self)
        dialog.title("Dolda underkategorier")
        dialog.geometry("520x420")
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(bg="#FFFFFF")

        wrap = tk.Frame(dialog, bg="#FFFFFF")
        wrap.pack(fill="both", expand=True, padx=18, pady=18)

        tk.Label(
            wrap,
            text="Dolda underkategorier",
            bg="#FFFFFF",
            fg=TEXT_COLOR,
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w", pady=(0, 12))

        list_frame = tk.Frame(wrap, bg="#FFFFFF")
        list_frame.pack(fill="both", expand=True)

        listbox = tk.Listbox(list_frame, font=("Segoe UI", 10), activestyle="none")
        listbox.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=listbox.yview)
        scrollbar.pack(side="right", fill="y")
        listbox.configure(yscrollcommand=scrollbar.set)

        for row in hidden_rows:
            listbox.insert(tk.END, f"{row.get('section', '')} / {row.get('category', '')}")

        def unhide_selected():
            sel = listbox.curselection()
            if not sel:
                messagebox.showinfo("Val saknas", "Välj en rad först.", parent=dialog)
                return
            hidden_rows[sel[0]]["hidden"] = False
            self._sync_global_templates_from_current_month()
            self._save_months()
            dialog.destroy()
            self._rebuild_main_view()

        button_row = tk.Frame(wrap, bg="#FFFFFF")
        button_row.pack(fill="x", pady=(12, 0))

        tk.Button(
            button_row,
            text="Visa igen",
            command=unhide_selected,
            bg="#4A90E2",
            fg="white",
            relief="flat",
            bd=0,
            padx=12,
            pady=6,
            cursor="hand2",
            font=("Segoe UI", 9, "bold"),
        ).pack(side="left")

        tk.Button(
            button_row,
            text="Stäng",
            command=dialog.destroy,
            bg="#E5E7EB",
            fg=TEXT_COLOR,
            relief="flat",
            bd=0,
            padx=12,
            pady=6,
            cursor="hand2",
            font=("Segoe UI", 9, "bold"),
        ).pack(side="right")

    def open_edit_subcategories_dialog(self, section):
        if not self._get_current_month_key():
            messagebox.showinfo("Ingen månad vald", "Skapa först en månad.", parent=self)
            return

        dialog = tk.Toplevel(self)
        dialog.title(f"Redigera underkategorier – {SECTION_LABELS.get(section, section)}")
        dialog.geometry("820x470")
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(bg="#F3F4F6")

        tk.Label(
            dialog,
            text=f"Underkategorier i {SECTION_LABELS.get(section, section)}",
            bg="#F3F4F6",
            fg=TEXT_COLOR,
            font=self.f(11),
        ).pack(anchor="w", padx=18, pady=(18, 10))

        list_frame = tk.Frame(dialog, bg="#F3F4F6")
        list_frame.pack(fill="both", expand=True, padx=18, pady=(0, 14))

        listbox = tk.Listbox(
            list_frame,
            font=self.f(10),
            activestyle="none",
            borderwidth=1,
            relief="solid",
        )
        listbox.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=listbox.yview)
        scrollbar.pack(side="right", fill="y")
        listbox.configure(yscrollcommand=scrollbar.set)

        tooltip = tk.Label(
            dialog,
            text="",
            bg="#FFF3A3",
            fg="#000000",
            relief="solid",
            bd=1,
            font=("Segoe UI", 9),
            padx=6,
            pady=3,
        )
        tooltip.place_forget()

        def current_section_rows():
            return [
                row for row in self._get_all_rows_for_current_month()
                if row.get("section", "OVRIGT") == section
            ]

        def refresh_list(select_index=None):
            listbox.delete(0, tk.END)
            rows = current_section_rows()
            for row in rows:
                suffix = " (dold)" if row.get("hidden", False) else ""
                listbox.insert(tk.END, f"{row.get('category', '')}{suffix}")

            if select_index is not None and rows:
                select_index = max(0, min(select_index, len(rows) - 1))
                listbox.selection_clear(0, tk.END)
                listbox.selection_set(select_index)
                listbox.activate(select_index)

        def selected_index():
            sel = listbox.curselection()
            if not sel:
                return None
            return sel[0]

        def selected_row():
            idx = selected_index()
            if idx is None:
                return None
            rows = current_section_rows()
            if idx >= len(rows):
                return None
            return rows[idx]

        def save_and_refresh(select_index=None):
            self._sync_global_templates_from_current_month()
            self._save_months()
            refresh_list(select_index)
            self._rebuild_main_view()

        def create_new():
            name = simpledialog.askstring("Ny underkategori", "Ange namn på ny underkategori:", parent=dialog)
            if not name:
                return
            name = name.strip()
            if not name:
                return

            rows = current_section_rows()
            if any(r.get("category", "").strip().lower() == name.lower() for r in rows):
                messagebox.showinfo("Finns redan", "Det finns redan en underkategori med det namnet.", parent=dialog)
                return

            rows.append(
                {
                    "id": self._next_row_id(),
                    "section": section,
                    "category": name,
                    "actual": 0.0,
                    "hidden": False,
                }
            )
            self._set_section_rows_for_current_month(section, rows)
            save_and_refresh(len(rows) - 1)

        def rename_selected():
            idx = selected_index()
            row = selected_row()
            if row is None:
                messagebox.showinfo("Val saknas", "Välj en underkategori först.", parent=dialog)
                return

            new_name = simpledialog.askstring(
                "Ändra namn",
                "Ange nytt namn:",
                initialvalue=row.get("category", ""),
                parent=dialog,
            )
            if not new_name:
                return
            new_name = new_name.strip()
            if not new_name:
                return

            rows = current_section_rows()
            for i, existing in enumerate(rows):
                if i != idx and existing.get("category", "").strip().lower() == new_name.lower():
                    messagebox.showinfo("Finns redan", "Det finns redan en underkategori med det namnet.", parent=dialog)
                    return

            row["category"] = new_name
            self._set_section_rows_for_current_month(section, rows)
            save_and_refresh(idx)

        def toggle_hidden():
            idx = selected_index()
            row = selected_row()
            if row is None:
                messagebox.showinfo("Val saknas", "Välj en underkategori först.", parent=dialog)
                return

            row["hidden"] = not row.get("hidden", False)
            rows = current_section_rows()
            self._set_section_rows_for_current_month(section, rows)
            save_and_refresh(idx)

        def move_up():
            idx = selected_index()
            if idx is None:
                messagebox.showinfo("Val saknas", "Välj en underkategori först.", parent=dialog)
                return
            if idx <= 0:
                return

            rows = current_section_rows()
            rows[idx - 1], rows[idx] = rows[idx], rows[idx - 1]
            self._set_section_rows_for_current_month(section, rows)
            save_and_refresh(idx - 1)

        def move_down():
            idx = selected_index()
            if idx is None:
                messagebox.showinfo("Val saknas", "Välj en underkategori först.", parent=dialog)
                return

            rows = current_section_rows()
            if idx >= len(rows) - 1:
                return

            rows[idx], rows[idx + 1] = rows[idx + 1], rows[idx]
            self._set_section_rows_for_current_month(section, rows)
            save_and_refresh(idx + 1)

        def delete_selected():
            idx = selected_index()
            row = selected_row()
            if row is None:
                messagebox.showinfo("Val saknas", "Välj en underkategori först.", parent=dialog)
                return

            ok = messagebox.askyesno(
                "Ta bort underkategori",
                f"Vill du ta bort '{row.get('category', '')}'?",
                parent=dialog,
            )
            if not ok:
                return

            rows = current_section_rows()
            rows[:] = [r for r in rows if r.get("id") != row.get("id")]
            self._set_section_rows_for_current_month(section, rows)
            save_and_refresh(max(0, idx - 1))

        def on_motion(event):
            if listbox.size() == 0:
                tooltip.place_forget()
                return

            index = listbox.nearest(event.y)
            if index < 0 or index >= listbox.size():
                tooltip.place_forget()
                return

            bbox = listbox.bbox(index)
            if bbox is None:
                tooltip.place_forget()
                return

            x, y, width, height = bbox
            if not (y <= event.y <= y + height):
                tooltip.place_forget()
                return

            text = listbox.get(index)
            if not text:
                tooltip.place_forget()
                return

            tooltip.config(text=text)

            pos_x = event.x_root - dialog.winfo_rootx() + 12
            pos_y = event.y_root - dialog.winfo_rooty() + 12
            tooltip.place(x=pos_x, y=pos_y)

        def on_leave(_event):
            tooltip.place_forget()

        listbox.bind("<Motion>", on_motion)
        listbox.bind("<Leave>", on_leave)

        button_row = tk.Frame(dialog, bg="#F3F4F6")
        button_row.pack(fill="x", padx=18, pady=(0, 18))

        ttk.Button(button_row, text="Skapa ny", command=create_new).pack(side="left", padx=(0, 8))
        ttk.Button(button_row, text="Ändra namn", command=rename_selected).pack(side="left", padx=(0, 8))
        ttk.Button(button_row, text="Dölj / visa", command=toggle_hidden).pack(side="left", padx=(0, 8))
        ttk.Button(button_row, text="Flytta upp", command=move_up).pack(side="left", padx=(0, 8))
        ttk.Button(button_row, text="Flytta ner", command=move_down).pack(side="left", padx=(0, 8))
        ttk.Button(button_row, text="Ta bort", command=delete_selected).pack(side="left", padx=(0, 8))
        ttk.Button(button_row, text="Stäng", command=dialog.destroy).pack(side="right")

        refresh_list()

    def activate_license_from_menu(self):
        key = simpledialog.askstring("Aktivera licens", "Ange din licensnyckel:", parent=self)

        if not key:
            return

        key = key.strip().upper()

        valid, result = self._validate_license_key(key)

        if valid:
            status = str(result.get("status", "PRO")).upper()

            self.settings["license_type"] = status
            self.settings["license_key"] = key
            self.settings["activated_machine_id"] = self._get_machine_id()

            self._save_local_license(key, status)
            self._save_settings()

            messagebox.showinfo(
                "Licens",
                result.get("message", "Licens aktiverad! Du har nu PRO-versionen."),
                parent=self
            )

            self._rebuild_main_view()
        else:
            messagebox.showerror(
                "Fel",
                result.get("message", "Ogiltig licensnyckel."),
                parent=self
            )

    def show_license_status(self):
        license_type = self.settings.get("license_type", "Trial")

        if license_type == "PRO":
            message = f"PRO-version aktiv.\n\nLicensnyckel:\n{self.settings.get('license_key', '')}"
        else:
            expiry_date_str = self.settings.get("expiry_date")
            days_left = None

            if expiry_date_str:
                try:
                    expiry_date = datetime.fromisoformat(expiry_date_str).date()
                    today = datetime.now().date()
                    days_left = (expiry_date - today).days
                except Exception:
                    days_left = None

            if days_left is None:
                message = "Trial aktiv.\nKunde inte räkna dagar kvar."
            elif days_left >= 0:
                message = f"Trial aktiv.\n\nDagar kvar: {days_left}"
            else:
                message = "Trial har gått ut.\n\nKöp PRO för att fortsätta använda programmet."

        messagebox.showinfo("Licensstatus", message, parent=self)

    def restore_latest_backup(self):
        month_backups = sorted(BACKUP_DIR.glob("months_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        settings_backups = sorted(BACKUP_DIR.glob("settings_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)

        if not month_backups and not settings_backups:
            messagebox.showinfo("Backup", "Det finns ingen backup att återställa.", parent=self)
            return

        ok = messagebox.askyesno("Backup", "Vill du återställa senaste backup?", parent=self)
        if not ok:
            return

        try:
            if month_backups:
                shutil.copy2(month_backups[0], MONTHS_FILE)
            if settings_backups:
                shutil.copy2(settings_backups[0], SETTINGS_FILE)

            self.settings = self._load_settings()
            self.months_data = self._load_months()

            self._ensure_settings_defaults()
            self._ensure_trial_started()
            self._auto_load_saved_license()
            self._remove_empty_duplicate_months()
            self._save_all_data()

            self._rebuild_main_view()
            messagebox.showinfo("Backup", "Senaste backup återställd.", parent=self)
        except Exception as exc:
            messagebox.showerror("Fel", f"Kunde inte återställa backup.\n\n{exc}", parent=self)

    def export_current_month(self):
        if self.settings.get("license_type") != "PRO":
            messagebox.showwarning(
                "PRO-funktion",
                "Exportera månad är endast tillgängligt i PRO-versionen.",
                parent=self
            )
            return

        month_key = self._get_current_month_key()
        month_data = self._get_current_month_data()

        if not month_key or not month_data:
            messagebox.showwarning("Ingen månad vald", "Det finns ingen månad att exportera.", parent=self)
            return

        rows = self._get_all_rows_for_current_month()
        if not rows:
            messagebox.showwarning("Ingen data", "Den valda månaden innehåller inga rader att exportera.", parent=self)
            return

        folder = filedialog.askdirectory(title="Välj mapp för export")
        if not folder:
            return

        export_path = Path(folder) / f"{month_key}.csv"

        try:
            with open(export_path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow(["Månad", month_data.get("name", month_key)])
                writer.writerow([])
                writer.writerow(["Sektion", "Underkategori", "Belopp", "Dold"])

                for row in rows:
                    writer.writerow([
                        row.get("section", ""),
                        row.get("category", ""),
                        row.get("actual", 0),
                        "Ja" if row.get("hidden", False) else "Nej",
                    ])

            messagebox.showinfo("Export klar", f"Månaden exporterades till:\n\n{export_path}", parent=self)
        except Exception as e:
            messagebox.showerror("Exportfel", f"Kunde inte exportera månaden.\n\n{e}", parent=self)

    def _on_sections_frame_configure(self, event=None):
        if self.sections_canvas:
            self.sections_canvas.configure(scrollregion=self.sections_canvas.bbox("all"))

    def _on_sections_canvas_configure(self, event):
        if self.sections_window:
            self.sections_canvas.itemconfigure(self.sections_window, width=event.width)

    def _on_mousewheel_windows(self, event):
        if self.sections_canvas:
            self.sections_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_mousewheel_linux_up(self, event):
        if self.sections_canvas:
            self.sections_canvas.yview_scroll(-1, "units")

    def _on_mousewheel_linux_down(self, event):
        if self.sections_canvas:
            self.sections_canvas.yview_scroll(1, "units")

    def _on_close(self):
        if self.clock_job:
            try:
                self.after_cancel(self.clock_job)
            except Exception:
                pass
        self.destroy()


if __name__ == "__main__":
    app = BudgetApp()
    app.mainloop()