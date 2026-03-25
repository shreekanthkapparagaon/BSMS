import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
from database import cursor, conn, hash_password


class UserManagement(tb.Frame):
    def __init__(self, master, current_user_role):
        super().__init__(master)
        self.user_role = current_user_role
        self.pack(fill=BOTH, expand=True)

        self.create_ui()
        self.load_users()

    def create_ui(self):
        style = tb.Style()

        # Main table style
        style.configure(
            "Custom.Treeview",
            font=("Segoe UI", 12),
            rowheight=42,
            borderwidth=0
        )

        # Header style
        style.configure(
            "Custom.Treeview.Heading",
            font=("Segoe UI", 13, "bold")
        )

        # Selection color
        style.map(
            "Custom.Treeview",
            background=[("selected", "#6c757d")],   # blue highlight
            foreground=[("selected", "white")]
        )
        # MAIN CONTAINER
        container = tb.Frame(self)
        container.pack(fill=BOTH, expand=True, padx=10, pady=10)

        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=2)
        container.rowconfigure(0, weight=1)

        # ================= LEFT SIDE =================
        left = tb.Frame(container)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

        left.columnconfigure(0, weight=1)
        left.rowconfigure(0, weight=1)

        # CENTER CARD USING GRID (NOT place)
        card = tb.Frame(left, padding=25, borderwidth=2, relief="solid")
        card.grid(row=0, column=0)

        # TITLE
        tb.Label(card, text="Add User",
                font=("Segoe UI", 20, "bold")).pack(pady=(0, 15))

        # USERNAME
        tb.Label(card, text="Username",
                font=("Segoe UI", 11, "bold")).pack(anchor="w")
        self.username = tb.Entry(card, font=("Segoe UI", 12))
        self.username.pack(fill=X, pady=8, ipady=5)

        # PASSWORD
        tb.Label(card, text="Password",
                font=("Segoe UI", 11, "bold")).pack(anchor="w")
        self.password = tb.Entry(card, show="*", font=("Segoe UI", 12))
        self.password.pack(fill=X, pady=8, ipady=5)

        # ROLE
        tb.Label(card, text="Role",
                font=("Segoe UI", 11, "bold")).pack(anchor="w")
        self.role = tb.Combobox(card, values=["admin", "staff"],
                                font=("Segoe UI", 12))
        self.role.pack(fill=X, pady=8, ipady=3)

        # BUTTON
        self.add_btn = tb.Button(
            card,
            text="Add User",
            bootstyle="success",
            command=self.add_user
        )
        self.add_btn.pack(pady=15, fill=X)

        if self.user_role != "admin":
            self.add_btn.config(state="disabled")
        # ================= RIGHT SIDE =================
        right = tb.Frame(container)
        right.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

        right.columnconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)

        tb.Label(right, text="User List",
                font=("Segoe UI", 18, "bold")).grid(row=0, column=0, sticky="w", pady=5)

        self.table = tb.Treeview(
            right,
            columns=("ID", "Username", "Role"),
            show="headings",
            style="Custom.Treeview",
            bootstyle="info"
        )
        self.table.grid(row=1, column=0, sticky="nsew")
        if self.user_role != "admin":
            self.username.config(state="disabled")
            self.password.config(state="disabled")
            self.role.config(state="disabled")

        # ===== HOVER EFFECT =====
        def on_hover(event):
            row = self.table.identify_row(event.y)

            # remove previous hover
            for item in self.table.get_children():
                tags = list(self.table.item(item, "tags"))
                if "hover" in tags:
                    tags.remove("hover")
                    self.table.item(item, tags=tags)

            if row:
                tags = list(self.table.item(row, "tags"))
                if "hover" not in tags:
                    tags.append("hover")
                    self.table.item(row, tags=tags)


        def on_leave(event):
            for item in self.table.get_children():
                tags = list(self.table.item(item, "tags"))
                if "hover" in tags:
                    tags.remove("hover")
                    self.table.item(item, tags=tags)


        # bind events
        self.table.bind("<Motion>", on_hover)
        self.table.bind("<Leave>", on_leave)
        self.table.bind("<Double-1>", self.open_edit_popup)

        # hover style
        self.table.tag_configure("hover", background="#3a8eb4")

        # COLUMN ALIGNMENT
        self.table.heading("ID", text="ID", anchor=CENTER)
        self.table.column("ID", width=60, anchor=CENTER, stretch=False)

        self.table.heading("Username", text="Username", anchor=W)
        self.table.column("Username", width=220, anchor=W)

        self.table.heading("Role", text="Role", anchor=CENTER)
        self.table.column("Role", width=120, anchor=CENTER, stretch=False)

        self.delete_btn = tb.Button(
            right,
            text="Delete Selected",
            bootstyle="danger",
            command=self.delete_user
        )
        self.delete_btn.grid(row=2, column=0, sticky="ew", pady=10)
        if self.user_role != "admin":
            self.delete_btn.config(state="disabled")
        self.update_idletasks()
        self.update()
    def load_users(self):
        for row in self.table.get_children():
            self.table.delete(row)

        for i, u in enumerate(cursor.execute("SELECT id, username, role FROM users")):
            tag = "even" if i % 2 == 0 else "odd"

            self.table.insert(
                "",
                "end",
                values=(u["id"], u["username"], u["role"]),
                tags=(tag,)
            )

        # Zebra colors
        # self.table.tag_configure("even", background="#3a3f44")   # dark gray
        # self.table.tag_configure("odd", background="#3a3f44")

        # Empty state
        if not self.table.get_children():
            self.table.insert("", "end", values=("No data found", "", ""), tags=("empty",))
            self.table.tag_configure("empty", foreground="gray")


    def add_user(self):
        if self.user_role != "admin":
            messagebox.showerror("Access Denied", "Admin only")
            return
        if not self.username.get() or not self.password.get() or not self.role.get():
            messagebox.showwarning("Input Error", "All fields required")
            return

        try:
            cursor.execute(
                "INSERT INTO users VALUES (NULL,?,?,?)",
                (
                    self.username.get(),
                    hash_password(self.password.get()),
                    self.role.get()
                )
            )
            conn.commit()
            self.load_users()

            # Clear fields
            self.username.delete(0, END)
            self.password.delete(0, END)
            self.role.set("")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_user(self):
        if self.user_role != "admin":
            messagebox.showerror("Access Denied", "Admin only")
            return
        selected = self.table.focus()
        data = self.table.item(selected, "values")

        if data:
            cursor.execute("DELETE FROM users WHERE id=?", (data[0],))
            conn.commit()
            self.load_users()
    def open_edit_popup(self, event):
        if self.user_role != "admin":
            messagebox.showerror("Access Denied", "Only admin can edit users")
            return
        selected = self.table.focus()
        data = self.table.item(selected, "values")
        if not data or data[0] == "No data found":
            return

        user_id, username, role = data

        # ===== POPUP WINDOW =====
        popup = tb.Toplevel(self)
        popup.title("Edit User")
        popup.geometry("350x300")
        popup.resizable(False, False)

        # Center popup
        popup.transient(self)
        popup.grab_set()

        container = tb.Frame(popup, padding=20)
        container.pack(fill="both", expand=True)

        # TITLE
        tb.Label(container, text="Edit User",
                font=("Segoe UI", 16, "bold")).pack(pady=(0, 15))

        # USERNAME
        tb.Label(container, text="Username").pack(anchor="w")
        username_entry = tb.Entry(container)
        username_entry.insert(0, username)
        username_entry.pack(fill="x", pady=5)

        # PASSWORD (optional)
        tb.Label(container, text="New Password (optional)").pack(anchor="w")
        password_entry = tb.Entry(container, show="*")
        password_entry.pack(fill="x", pady=5)

        # ROLE
        tb.Label(container, text="Role").pack(anchor="w")
        role_combo = tb.Combobox(container, values=["admin", "staff"])
        role_combo.set(role)
        role_combo.pack(fill="x", pady=5)

        # ===== SAVE FUNCTION =====
        def save():
            new_username = username_entry.get()
            new_password = password_entry.get()
            new_role = role_combo.get()

            try:
                if new_password:
                    cursor.execute(
                        "UPDATE users SET username=?, password=?, role=? WHERE id=?",
                        (new_username, hash_password(new_password), new_role, user_id)
                    )
                else:
                    cursor.execute(
                        "UPDATE users SET username=?, role=? WHERE id=?",
                        (new_username, new_role, user_id)
                    )

                conn.commit()
                self.load_users()
                popup.destroy()

            except Exception as e:
                messagebox.showerror("Error", str(e))

        # SAVE BUTTON
        tb.Button(container,
                text="Save Changes",
                bootstyle="success",
                command=save).pack(pady=15, fill="x")