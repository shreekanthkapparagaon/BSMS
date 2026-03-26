import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
from database import conn
import sqlite3
from auth import check_permission
import os
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

DB_NAME = "bsms.db"


class CustomerApp(tb.Frame):
    def __init__(self, master, user=None):
        super().__init__(master)
        self.user = user
        self.pack(fill=BOTH, expand=True, padx=10, pady=10)

        self.conn = conn
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

        self.selected_id = None

        # Permissions
        self.can_view, self.can_edit = check_permission(self.user["role"], "customers")

        if not self.can_view:
            tb.Label(self, text="❌ Access Denied",
                     bootstyle="danger",
                     font=("Segoe UI", 16)).pack(pady=50)
            return

        self.create_table()
        self.build_ui()
        self.load_data()

    # ===================== DB ===================== #
    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                phone TEXT,
                email TEXT,
                address TEXT
            )
        """)
        self.conn.commit()

    # ===================== UI ===================== #
    def build_ui(self):

        style = tb.Style()

        # SAME STYLE AS USER MODULE
        style.configure(
            "Custom.Treeview",
            font=("Segoe UI", 12),
            rowheight=42,
            borderwidth=0
        )

        style.configure(
            "Custom.Treeview.Heading",
            font=("Segoe UI", 13, "bold")
        )

        style.map(
            "Custom.Treeview",
            background=[("selected", "#6c757d")],
            foreground=[("selected", "white")]
        )

        tb.Label(self, text="Customer Management",
                 font=("Segoe UI", 18, "bold")).pack(anchor=W, pady=10)

        main = tb.Frame(self)
        main.pack(fill=BOTH, expand=True)

        # -------- LEFT (FORM) -------- #
        form = tb.Labelframe(
            main,
            text="Customer Form",
            bootstyle="primary",
            padding=15  
        )
        form.pack(side=LEFT, fill=Y, padx=10, pady=10)
        form.configure(width=350)   
        form.pack_propagate(False)  

        self.name = self.create_entry(form, "Name")
        self.phone = self.create_entry(form, "Phone")
        self.email = self.create_entry(form, "Email")
        self.address = self.create_entry(form, "Address")

        btn_frame = tb.Frame(form)
        btn_frame.pack(pady=15, fill=X)

        tb.Button(btn_frame,text="Statement",
          bootstyle=INFO,
          command=self.open_statement).pack(fill=X, pady=3)

        tb.Button(btn_frame, text="Save", bootstyle=SUCCESS,
                command=self.save_customer,
                state="normal" if self.can_edit else "disabled").pack(fill=X, pady=3)

        tb.Button(btn_frame, text="Update", bootstyle=WARNING,
                command=self.update_customer,
                state="normal" if self.can_edit else "disabled").pack(fill=X, pady=3)

        tb.Button(btn_frame, text="Delete", bootstyle=DANGER,
                command=self.delete_customer,
                state="normal" if self.can_edit else "disabled").pack(fill=X, pady=3)

        tb.Button(btn_frame, text="Clear", bootstyle=SECONDARY,
                command=self.clear_form).pack(fill=X, pady=3)

        # -------- RIGHT (TABLE) -------- #
        right = tb.Labelframe(main, text="Customer List", bootstyle="info")
        right.pack(side=LEFT, fill=BOTH, expand=True, padx=10, pady=10)

        right.columnconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)
        right.pack(side=LEFT, fill=BOTH, expand=True, padx=10, pady=10)

        right.columnconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)

        self.search = tb.Entry(right,font=("Segoe UI", 11))
        self.search.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        self.search.insert(0, "Search by name or phone...")
        def clear_placeholder(event):
            if self.search.get() == "Search by name or phone...":
                self.search.delete(0, END)

        self.search.bind("<FocusIn>", clear_placeholder)
        self.search.bind("<KeyRelease>", self.search_customer)

        columns = ("ID", "Name", "Phone", "Email", "Address")

        self.tree = tb.Treeview(
            right,
            columns=columns,
            show="headings",
            style="Custom.Treeview",
            bootstyle="info"
        )

        self.tree.grid(row=1, column=0, sticky="nsew")

        # Columns
        self.tree.heading("ID", text="ID", anchor=CENTER)
        self.tree.column("ID", width=60, anchor=CENTER, stretch=False)

        self.tree.heading("Name", text="Name", anchor=W)
        self.tree.column("Name", width=180, anchor=W)

        self.tree.heading("Phone", text="Phone", anchor=CENTER)
        self.tree.column("Phone", width=120, anchor=CENTER)

        self.tree.heading("Email", text="Email", anchor=W)
        self.tree.column("Email", width=200, anchor=W)

        self.tree.heading("Address", text="Address", anchor=W)
        self.tree.column("Address", width=250, anchor=W)

        # Bind events
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.bind("<Motion>", self.on_hover)
        self.tree.bind("<Leave>", self.on_leave)

        self.prev_row = None

        # Hover color
        self.tree.tag_configure("hover", background="#3a8eb4")

    def create_entry(self, parent, label):
        tb.Label(parent, text=label,
                font=("Segoe UI", 11, "bold")).pack(anchor=W, padx=10)

        entry = tb.Entry(parent, font=("Segoe UI", 12))
        entry.pack(fill=X, padx=10, pady=8, ipady=6)  # 👈 bigger height

        return entry

    # ===================== CRUD ===================== #
    def save_customer(self):
        if not self.can_edit:
            messagebox.showerror("Denied", "No permission")
            return

        name = self.name.get()
        phone = self.phone.get()

        if not name or not phone:
            messagebox.showwarning("Validation", "Name & Phone required")
            return

        self.cursor.execute("""
            INSERT INTO customers (name, phone, email, address)
            VALUES (?, ?, ?, ?)
        """, (name, phone, self.email.get(), self.address.get()))
        self.conn.commit()

        self.load_data()
        self.clear_form()

    def update_customer(self):
        if not self.can_edit:
            return

        if not self.selected_id:
            return

        self.cursor.execute("""
            UPDATE customers
            SET name=?, phone=?, email=?, address=?
            WHERE id=?
        """, (
            self.name.get(),
            self.phone.get(),
            self.email.get(),
            self.address.get(),
            self.selected_id
        ))
        self.conn.commit()

        self.load_data()
        self.clear_form()

    def delete_customer(self):
        if not self.can_edit:
            return

        if not self.selected_id:
            return

        if not messagebox.askyesno("Confirm", "Delete this customer?"):
            return

        self.cursor.execute("DELETE FROM customers WHERE id=?", (self.selected_id,))
        self.conn.commit()

        self.load_data()
        self.clear_form()

    # ===================== HELPERS ===================== #
    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        rows = self.cursor.execute("SELECT * FROM customers").fetchall()

        for i, row in enumerate(rows):
            tag = "even" if i % 2 == 0 else "odd"
            self.tree.insert("", END, values=(
            row["id"],
            row["name"],
            row["phone"],
            row["email"],
            row["address"]
        ),tags=(tag,))

        if not rows:
            self.tree.insert("", "end", values=("No data found", "", "", "", ""), tags=("empty",))
            self.tree.tag_configure("empty", foreground="gray")

    def clear_form(self):
        self.selected_id = None
        for entry in [self.name, self.phone, self.email, self.address]:
            entry.delete(0, END)

    def open_statement(self):
        if not self.selected_id:
            return

        popup = tb.Toplevel(self)
        popup.title("Customer Statement")
        popup.geometry("700x500")
        popup.iconbitmap(resource_path("assets/icon.ico"))

        # Title
        tb.Label(popup,
                text="Customer Statement",
                font=("Segoe UI", 16, "bold")).pack(pady=10)

        # Table
        columns = ("Date", "Type", "Amount")
        tree = tb.Treeview(popup, columns=columns, show="headings")

        for col in columns:
            tree.heading(col, text=col)

        tree.pack(fill=BOTH, expand=True, padx=10, pady=10)

        total_due = 0

        # SALES
        sales = self.cursor.execute("""
        SELECT sold_date, total, paid, balance FROM sales
        WHERE customer_id=?
        """, (self.selected_id,)).fetchall()

        for s in sales:
            tree.insert("", END, values=(s["sold_date"], "Sale", f"+₹{s['total']}"))
            if s["paid"] > 0:
                tree.insert("", END, values=(s["sold_date"], "Paid", f"-₹{s['paid']}"))

            total_due += s["balance"]

        # PAYMENTS
        payments = self.cursor.execute("""
        SELECT date, amount FROM payments
        WHERE customer_id=?
        """, (self.selected_id,)).fetchall()

        for p in payments:
            tree.insert("", END, values=(p["date"], "Payment", f"-₹{p['amount']}"))

        # TOTAL
        tb.Label(popup,
                text=f"Total Due: ₹{round(total_due,2)}",
                font=("Segoe UI", 14, "bold"),
                bootstyle="danger" if total_due > 0 else "success"
                ).pack(pady=10)
    
    # ===================== EVENTS ===================== #
    def on_double_click(self, event):
        self.on_select(event)

    def on_hover(self, event):
        row = self.tree.identify_row(event.y)

        if self.prev_row == row:
            return

        if self.prev_row:
            tags = self.tree.item(self.prev_row, "tags")
            base_tag = [t for t in tags if t in ("even", "odd")]
            self.tree.item(self.prev_row, tags=base_tag)

        if row:
            tags = self.tree.item(row, "tags")
            base_tag = [t for t in tags if t in ("even", "odd")]
            self.tree.item(row, tags=base_tag + ["hover"])

        self.prev_row = row

    def on_leave(self, event):
        if self.prev_row:
            tags = self.tree.item(self.prev_row, "tags")
            base_tag = [t for t in tags if t in ("even", "odd")]
            self.tree.item(self.prev_row, tags=base_tag)

        self.prev_row = None

    def on_select(self, event):
        selected = self.tree.focus()
        data = self.tree.item(selected, "values")

        if data:
            self.selected_id = data[0]
            self.name.delete(0, END)
            self.name.insert(0, data[1])

            self.phone.delete(0, END)
            self.phone.insert(0, data[2])

            self.email.delete(0, END)
            self.email.insert(0, data[3])

            self.address.delete(0, END)
            self.address.insert(0, data[4])

    def search_customer(self, event):
        keyword = self.search.get().lower()

        for row in self.tree.get_children():
            self.tree.delete(row)

        query = """
            SELECT * FROM customers
            WHERE LOWER(name) LIKE ? OR phone LIKE ?
        """

        for row in self.cursor.execute(query, (f"%{keyword}%", f"%{keyword}%")):
            self.tree.insert("", END, values=row)