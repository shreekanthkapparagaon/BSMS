import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
from database import cursor, conn
import shutil
import os
from utils.settings_utils import is_valid_db


class SettingsPage(tb.Frame):
    def __init__(self, master, user):
        super().__init__(master)
        self.user = user
        self.role = user["role"]

        self.pack(fill=BOTH, expand=True)

        # variables
        self.db_path_var = tb.StringVar()
        self.theme_var = tb.StringVar()
        self.invoice_prefix_var = tb.StringVar()

        self.create_ui()
        self.load_settings()

    # ================= UI ================= #
    def create_ui(self):
        tb.Label(self, text="Settings",
                 font=("Segoe UI", 22, "bold")).pack(pady=10)

        container = tb.Frame(self)
        container.pack(fill=BOTH, expand=True, padx=20, pady=10)

        self.general_settings(container)
        self.invoice_settings(container)

        # show admin only if allowed
        if os.getenv("ALLOW_DB_SWITCH", "True") == "True":
            self.admin_settings(container)

    # ================= GENERAL ================= #
    def general_settings(self, parent):
        frame = tb.Labelframe(parent, text="General Settings", padding=15)
        frame.pack(fill=X, pady=10)

        tb.Label(frame, text="Theme").pack(anchor="w")

        theme_combo = tb.Combobox(
            frame,
            values=["superhero", "flatly", "darkly"],
            textvariable=self.theme_var,
            state="readonly"
        )
        theme_combo.pack(fill=X, pady=5)

    # ================= INVOICE ================= #
    def invoice_settings(self, parent):
        frame = tb.Labelframe(parent, text="Invoice Settings", padding=15)
        frame.pack(fill=X, pady=10)

        tb.Label(frame, text="Invoice Prefix").pack(anchor="w")

        tb.Entry(frame, textvariable=self.invoice_prefix_var)\
            .pack(fill=X, pady=5)

    # ================= ADMIN ================= #
    def admin_settings(self, parent):
        if self.role != "admin":
            return

        frame = tb.Labelframe(parent, text="System Settings (Admin)", padding=15)
        frame.pack(fill=X, pady=10)

        # DB PATH
        tb.Label(frame, text="Database Path").pack(anchor="w")

        path_frame = tb.Frame(frame)
        path_frame.pack(fill=X, pady=5)

        tb.Entry(path_frame, textvariable=self.db_path_var)\
            .pack(side=LEFT, fill=X, expand=True)

        tb.Button(
            path_frame,
            text="Browse",
            command=self.browse_db
        ).pack(side=RIGHT, padx=5)

        # BACKUP BUTTON
        tb.Button(
            frame,
            text="Backup Database",
            bootstyle="warning",
            command=self.backup_db
        ).pack(pady=10, fill=X)

        # SAVE BUTTON
        tb.Button(
            frame,
            text="Save Settings",
            bootstyle="success",
            command=self.save_settings
        ).pack(fill=X)

    # ================= FUNCTIONS ================= #

    def browse_db(self):
        path = filedialog.askopenfilename(
            title="Select Database",
            filetypes=[("SQLite DB", "*.db"), ("All Files", "*.*")]
        )

        if not path:
            return

        if is_valid_db(path):
            self.db_path_var.set(path)
        else:
            messagebox.showerror(
                "Invalid Database",
                "Selected file is not a valid BSMS database"
            )

    def backup_db(self):
        # priority: settings → env → default
        db_path = (
            self.get_setting("db_path")
            or os.getenv("DEFAULT_DB_NAME", "database.db")
        )

        if not os.path.exists(db_path):
            messagebox.showerror("Error", "Database not found")
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[("Database Backup", "*.db")]
        )

        if save_path:
            shutil.copy(db_path, save_path)
            messagebox.showinfo("Success", "Backup created successfully")

    def save_settings(self):
        path = self.db_path_var.get()

        # validate DB
        if self.role == "admin" and path:
            if not is_valid_db(path):
                messagebox.showerror("Error", "Invalid database selected")
                return

            self.set_setting("db_path", path)

        # save other settings
        self.set_setting("theme", self.theme_var.get())
        self.set_setting("invoice_prefix", self.invoice_prefix_var.get())

        messagebox.showinfo(
            "Saved",
            "Settings updated successfully.\nRestart app to apply DB changes."
        )

    def load_settings(self):
        # fallback: DB → env → default
        self.theme_var.set(
            self.get_setting("theme")
            or os.getenv("DEFAULT_THEME", "superhero")
        )

        self.invoice_prefix_var.set(
            self.get_setting("invoice_prefix") or "INV"
        )

        if self.role == "admin":
            self.db_path_var.set(self.get_setting("db_path") or "")

    # ================= DB HELPERS ================= #

    def get_setting(self, key):
        cursor.execute("SELECT value FROM settings WHERE key=?", (key,))
        row = cursor.fetchone()
        return row["value"] if row else None

    def set_setting(self, key, value):
        cursor.execute(
            "REPLACE INTO settings (key, value) VALUES (?, ?)",
            (key, value)
        )
        conn.commit()