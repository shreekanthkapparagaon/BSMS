import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
from database import cursor, conn
from datetime import datetime
import os
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class SalesApp(tb.Frame):
    def __init__(self, master, user=None):
        super().__init__(master)
        self.user = user
        self.pack(fill=BOTH, expand=True)

        self.mode = "view"
        self.search_text = ""
        self.selected_items = {}
        self.total_var = tb.StringVar(value="Total: ₹0")

        self.page = 0
        self.limit = 20

        self.create_ui()
        self.load_sales()
        self.load_customers()

    # ---------- UI ----------
    def create_ui(self):

        # FORM
        form = tb.LabelFrame(self, text="New Sale")
        form.pack(fill=X, padx=10, pady=5)

        inner = tb.Frame(form, padding=10)
        inner.pack(fill=X)

        self.customer_combo = tb.Combobox(inner, state="readonly", width=30)
        self.customer_combo.grid(row=0, column=1, padx=5)
        self.customer_combo.bind("<<ComboboxSelected>>", self.on_customer_select)

        self.phone = tb.Entry(inner, state="readonly")
        self.phone.grid(row=0, column=3, padx=5)

        tb.Label(inner, text="Customer").grid(row=0, column=0)
        self.customer_combo.grid(row=0, column=1, padx=5)

        tb.Label(inner, text="Phone").grid(row=0, column=2)
        self.phone.grid(row=0, column=3, padx=5)

        tb.Button(inner, text="Add Sale",
                  bootstyle=SUCCESS,
                  command=self.start_add_sale).grid(row=0, column=4, padx=10)
        
        
        # MAIN
        main = tb.Frame(self)
        main.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # LEFT TABLE
        left = tb.Frame(main)
        left.pack(side=LEFT, fill=BOTH, expand=True)

        self.table = tb.Treeview(
            left,
            columns=("ID", "Customer", "Phone", "Date", "Total", "Paid", "Balance"),
            show="headings"
        )
        self.table.tag_configure("due", foreground="red")
        self.table.tag_configure("paid", foreground="green")
        self.table.column("ID", width=60,anchor=CENTER, stretch=False)
        self.table.column("Customer", width=200)
        self.table.column("Phone", width=150, stretch=False)
        self.table.column("Date", width=200,stretch=False)
        self.table.column("Total", width=150,stretch=False)
        self.table.column("Paid", width=120, anchor=W, stretch=False)
        self.table.column("Balance", width=120, anchor=W, stretch=False)
        for c in self.table["columns"]:
            self.table.heading(c, text=c,anchor=W)

        self.table.pack(fill=BOTH, expand=True)
        self.table.bind("<ButtonRelease-1>", self.load_sale_products)
        self.table.bind("<Double-1>", self.open_invoice)

        # PAGINATION
        nav = tb.Frame(left)
        nav.pack(fill=X)

        tb.Button(nav, text="<< Prev", command=self.prev_page).pack(side=LEFT)
        tb.Button(nav, text="Next >>", command=self.next_page).pack(side=LEFT)

        self.page_label = tb.Label(nav, text="Page 1")
        self.page_label.pack(side=LEFT, padx=10)

        # RIGHT PANEL
        right = tb.LabelFrame(main, text="Products")
        right.pack(side=RIGHT, fill=BOTH, expand=True)

        self.product_table = tb.Treeview(
            right,
            columns=("Select", "Serial", "Name", "Price", "Qty", "Total"),
            show="headings"
        )
        # ===== FIX COLUMN WIDTHS =====
        self.product_table.column("Select", width=60, anchor=CENTER, stretch=False)
        self.product_table.column("Serial", width=90, anchor=W, stretch=False)
        self.product_table.column("Name", width=150, anchor=W)   # flexible
        self.product_table.column("Price", width=80, anchor=W, stretch=False)
        self.product_table.column("Qty", width=60, anchor=W, stretch=False)
        self.product_table.column("Total", width=100, anchor=W, stretch=False)

        self.product_table.heading("Select", text="Select",anchor=CENTER)
        for c in ("Serial", "Name", "Price", "Qty", "Total"):
            self.product_table.heading(c, text=c,anchor=W)

        self.product_table.pack(fill=BOTH, expand=True)


        # ===== BOTTOM SECTION =====
        bottom = tb.Frame(right)
        bottom.pack(fill=X, pady=5)

        tb.Label(bottom, textvariable=self.total_var).pack(side=LEFT, padx=10)

        tb.Button(bottom,
                text="Remove Selected",
                bootstyle=DANGER,
                command=self.remove_selected).pack(side=RIGHT)

        tb.Button(bottom,
                text="Pay Due",
                bootstyle=SUCCESS,
                command=self.pay_due).pack(side=RIGHT, padx=5)
        
        tb.Button(bottom,
          text="Clear Due",
          bootstyle=WARNING,
          command=self.clear_due).pack(side=RIGHT, padx=5)

        self.product_table.bind("<Button-1>", self.toggle_checkbox)
        self.product_table.bind("<Double-1>", self.edit_quantity)
        style = tb.Style()

        style.configure("Custom.Treeview", font=("Segoe UI", 11), rowheight=34)
        style.map("Custom.Treeview",
                background=[("selected", "#6c757d")],
                foreground=[("selected", "white")])

        self.table.configure(style="Custom.Treeview")
        self.product_table.configure(style="Custom.Treeview")

        # ZEBRA + HOVER COLORS
        # self.table.tag_configure("even", background="#3a3f44")
        # self.table.tag_configure("odd", background="#343a40")
        self.table.tag_configure("hover", background="#3a8eb4",foreground="white")

        # HOVER EFFECT
        def on_hover(event):
            row = self.table.identify_row(event.y)

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

        self.table.bind("<Motion>", on_hover)
        self.table.bind("<Leave>", on_leave)

        self.action_btn = tb.Button(right, text="", command=self.handle_action)
        self.action_btn.pack(pady=5)

    # ---------- SALES ----------
    def load_customers(self):
        rows = cursor.execute("SELECT id, name, phone FROM customers").fetchall()
        self.customer_map = {
            f"{r['name']} ({r['phone']})": r["id"] for r in rows
        }

        self.customer_combo["values"] = list(self.customer_map.keys())
    def load_sales(self):
        self.table.delete(*self.table.get_children())

        cursor.execute("""
        SELECT s.id, c.name, c.phone, s.sold_date, s.total, s.paid, s.balance
        FROM sales s
        LEFT JOIN customers c ON s.customer_id = c.id
        ORDER BY s.id DESC
        LIMIT ? OFFSET ?
        """, (self.limit, self.page * self.limit))

        for i, r in enumerate(cursor.fetchall()):
            if r[6] > 0:   # balance > 0 → due
                tag = "due"
            else:
                tag = "paid"

            self.table.insert("", END,
                values=(r[0], r[1], r[2], r[3], r[4], r[5], r[6]),
                tags=(tag,))

        self.page_label.config(text=f"Page {self.page + 1}")

    def on_customer_select(self, event):
        selected = self.customer_combo.get()
        cid = self.customer_map.get(selected)

        if not cid:
            return

        row = cursor.execute("SELECT phone FROM customers WHERE id=?", (cid,)).fetchone()
        self.phone.config(state="normal")
        self.phone.delete(0, END)
        self.phone.insert(0, row["phone"])
        self.phone.config(state="readonly")
    
    def next_page(self):
        self.page += 1
        self.load_sales()

    def prev_page(self):
        if self.page > 0:
            self.page -= 1
            self.load_sales()

    # ---------- MODE ----------
    def start_add_sale(self):
        if not self.customer_combo.get() or not self.phone.get():
            messagebox.showerror("Error", "Enter customer details")
            return

        self.mode = "select"
        self.selected_items.clear()
        self.total_var.set("Total: ₹0")
        self.action_btn.config(text="Confirm Sale", bootstyle=SUCCESS)

        self.load_inventory_products()

    def load_inventory_products(self):
        self.product_table.delete(*self.product_table.get_children())

        cursor.execute("SELECT * FROM batteries")

        for r in cursor.fetchall():
            self.product_table.insert("", END, values=(
                "☐", r[1], r[2], r[7], 0, 0
            ))

    def load_sale_products(self, event):
        self.mode = "view"
        self.action_btn.config(text="Print Invoice", bootstyle=PRIMARY)

        item = self.table.focus()
        data = self.table.item(item, "values")

        if not data:
            return

        sale_id = data[0]

        self.product_table.delete(*self.product_table.get_children())

        cursor.execute("""
            SELECT serial, product_name, price, quantity, total
            FROM sale_items WHERE sale_id=?
        """, (sale_id,))

        for r in cursor.fetchall():
            self.product_table.insert("", END, values=(
                "", r["serial"], r["product_name"], r["price"], r["quantity"], r["total"]
            ))

    # ---------- CHECKBOX ----------
    def toggle_checkbox(self, event):
        col = self.product_table.identify_column(event.x)
        row = self.product_table.identify_row(event.y)

        if col != "#1" or not row:
            return

        values = list(self.product_table.item(row, "values"))

        if values[0] == "☐":
            values[0] = "☑"
            values[4] = 1
            values[5] = float(values[3])
            self.selected_items[row] = 1
        else:
            values[0] = "☐"
            values[4] = 0
            values[5] = 0
            self.selected_items.pop(row, None)

        self.product_table.item(row, values=values)
        self.update_total()

    def edit_quantity(self, event):
        row = self.product_table.identify_row(event.y)

        if row not in self.selected_items:
            return

        values = list(self.product_table.item(row, "values"))

        qty = tb.dialogs.Querybox.get_integer(
            "Edit Quantity",
            "Enter quantity:",
            initialvalue=values[4] or 1
        )

        if not qty:
            return

        price = float(values[3])

        values[4] = qty
        values[5] = qty * price

        self.product_table.item(row, values=values)
        self.selected_items[row] = qty

        self.update_total()

    def update_total(self):
        total = sum(float(self.product_table.item(r, "values")[5])
                    for r in self.selected_items)
        self.total_var.set(f"Total: ₹{total:.2f}")

    def remove_selected(self):
        for r in list(self.selected_items):
            values = list(self.product_table.item(r, "values"))
            values[0] = "☐"
            values[4] = 0
            values[5] = 0
            self.product_table.item(r, values=values)

        self.selected_items.clear()
        self.update_total()

    # ---------- ACTION ----------
    def handle_action(self):
        if self.mode == "select":
            self.confirm_sale()
        else:
            self.print_invoice()
    
    def clear_due(self):
        item = self.table.focus()
        data = self.table.item(item, "values")

        if not data:
            return

        sale_id = data[0]
        balance = float(data[6])

        if balance <= 0:
            messagebox.showinfo("Info", "No due to clear")
            return
        
        if not messagebox.askyesno("Confirm", f"Clear full due ₹{balance:.2f}?"):
            return

        # Get customer_id
        row = cursor.execute(
            "SELECT customer_id FROM sales WHERE id=?",
            (sale_id,)
        ).fetchone()

        customer_id = row["customer_id"]

        # Save payment (full amount)
        cursor.execute("""
        INSERT INTO payments (customer_id, sale_id, amount, date)
        VALUES (?, ?, ?, datetime('now'))
        """, (customer_id, sale_id, balance))

        # Update sale → FULLY PAID
        cursor.execute("""
        UPDATE sales
        SET paid = paid + ?,
            balance = 0,
            status = 'Paid'
        WHERE id=?
        """, (balance, sale_id))

        # Update customer balance
        cursor.execute("""
        UPDATE customers
        SET balance = balance - ?
        WHERE id=?
        """, (balance, customer_id))

        conn.commit()

        self.load_sales()
        messagebox.showinfo("Success", "Due cleared بالكامل")
    def pay_due(self):
        item = self.table.focus()
        data = self.table.item(item, "values")

        if not data:
            return

        sale_id = data[0]
        balance = round(float(data[6]), 2)
 

        if balance <= 0:
            messagebox.showinfo("Info", "No due for this sale")
            return

        amount = tb.dialogs.Querybox.get_float(
            "Payment",
            f"Enter amount (Due: ₹{balance})"
        )
        amount=round(amount,2)
        if not amount or amount <= 0:
            return

        # 🔍 Get customer_id
        row = cursor.execute(
            "SELECT customer_id FROM sales WHERE id=?",
            (sale_id,)
        ).fetchone()

        customer_id = row["customer_id"]

        # 💾 Save payment
        cursor.execute("""
        INSERT INTO payments (customer_id, sale_id, amount, date)
        VALUES (?, ?, ?, datetime('now'))
        """, (customer_id, sale_id, amount))

        # 🔄 Update sale
        cursor.execute("""
        UPDATE sales
        SET paid = paid + ?,
            balance = balance - ?,
            status = CASE
                WHEN balance - ? <= 0 THEN 'Paid'
                ELSE 'Due'
            END
        WHERE id=?
        """, (amount, amount, amount, sale_id))

        # 🔄 Update customer balance
        cursor.execute("""
        UPDATE customers
        SET balance = balance - ?
        WHERE id=?
        """, (amount, customer_id))

        conn.commit()

        self.load_sales()
        messagebox.showinfo("Success", "Payment updated")
    # ---------- SAVE ----------
    def confirm_sale(self):
        if not self.selected_items:
            return

        total = sum(float(self.product_table.item(r, "values")[5])
                    for r in self.selected_items)

        paid = tb.dialogs.Querybox.get_float("Payment", "Enter paid amount:", initialvalue=0)
        if paid is None:
            return

        customer_text = self.customer_combo.get()
        customer_id = self.customer_map.get(customer_text)

        balance = round(total - paid,2)
        total = round(total, 2)
        paid = round(paid, 2)
        status = "Paid" if paid >= total else "Due"


        cursor.execute("""
        INSERT INTO sales (customer_id, user, sold_date, total, paid, balance, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (customer_id, "admin", str(datetime.now()), total, paid, balance, status))

        cursor.execute("""
        UPDATE customers
        SET balance = balance + ?
        WHERE id = ?
        """, (balance, customer_id))

        sid = cursor.lastrowid

        for r, qty in self.selected_items.items():
            data = self.product_table.item(r, "values")
            serial = data[1]
            name = data[2]
            price = float(data[3])

            cursor.execute("SELECT id FROM batteries WHERE serial=?", (serial,))
            pid = cursor.fetchone()[0]

            cursor.execute("""
            INSERT INTO sale_items (sale_id, product_id, serial, product_name, price, quantity, total)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (sid, pid, serial, name, price, qty, price * qty))

            cursor.execute("UPDATE batteries SET quantity = quantity - ? WHERE id=?", (qty, pid))

        conn.commit()

        self.show_invoice(sid)
        self.reset_after_sale()

    def reset_after_sale(self):
        self.product_table.delete(*self.product_table.get_children())
        self.selected_items.clear()
        self.total_var.set("Total: ₹0")
        self.customer_combo.set("")
        self.phone.config(state="normal")
        self.phone.delete(0, END)
        self.phone.config(state="readonly")
        self.phone.delete(0, END)
        self.mode = "view"
        self.action_btn.config(text="")
        self.load_sales()

    # ---------- INVOICE ----------
    def print_invoice(self,event=None):
        item = self.table.focus()
        if not item:
            return
        sid = self.table.item(item, "values")[0]
        self.show_invoice(sid)

    def show_invoice(self, sid):
        win = tb.Toplevel(self)
        win.title("Invoice")
        win.geometry("300x450+500+200")
        win.iconbitmap(resource_path("assets/icon.ico"))

        container = tb.Frame(win, padding=15)
        container.pack(fill="both", expand=True)

        # TITLE
        tb.Label(container,
                text=f"Invoice #{sid}",
                font=("Segoe UI", 14, "bold")).pack(pady=(0, 10))

        text = ""

        # PRODUCTS
        cursor.execute("SELECT * FROM sale_items WHERE sale_id=?", (sid,))
        for r in cursor.fetchall():
            text += f"{r['product_name']} x{r['quantity']} = ₹{r['total']}\n"

        # FETCH SALE DATA (IMPORTANT)
        cursor.execute("""
        SELECT total, paid, balance FROM sales WHERE id=?
        """, (sid,))
        sale = cursor.fetchone()

        # ADD SUMMARY
        text += f"\n\nTotal: ₹{sale['total']}"
        text += f"\nPaid: ₹{sale['paid']}"
        text += f"\nBalance: ₹{sale['balance']}"

        # INVOICE TEXT
        tb.Label(container,
                text=text,
                justify="left",
                font=("Segoe UI", 11)).pack(anchor="w")

        # PRINT BUTTON
        tb.Button(container,
                text="Print",
                bootstyle="primary",
                command=lambda: self.print_text(text)).pack(pady=10)
    def print_text(self, text):
        import tempfile
        import os

        file = tempfile.mktemp(".txt")

        with open(file, "w", encoding="utf-8") as f:
            f.write(text)

        os.startfile(file, "print")
    def open_invoice(self, event):
        row = self.table.identify_row(event.y)

        if not row:
            return

        data = self.table.item(row, "values")

        if not data:
            return

        sale_id = data[0]

        self.show_invoice(sale_id)