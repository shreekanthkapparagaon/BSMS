import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
from database import cursor, conn
import uuid

def get_battery_types():
    cursor.execute("SELECT name FROM battery_types")
    rows = cursor.fetchall()
    return [row["name"] for row in rows]

class InventoryApp(tb.Frame):
    def __init__(self, master, user=None):
        super().__init__(master)
        self.user = user
        self.pack(fill=BOTH, expand=True)

        self.selected_id = None
        self.page = 0
        self.limit = 18
        self.search_text = ""

        self.create_ui()
        self.load_data()

    def create_ui(self):
        style = tb.Style()
        style.configure("Treeview", rowheight=32, font=("Segoe UI", 11))
        style.configure("Treeview.Heading", font=("Segoe UI", 12, "bold"))

        # Search
        top = tb.Frame(self)
        top.pack(fill=X, padx=10, pady=5)

        tb.Label(top, text="Search:").pack(side=LEFT)
        self.search_entry = tb.Entry(top)
        self.search_entry.pack(side=LEFT, padx=5)
        self.search_entry.bind("<KeyRelease>", self.on_search)

        # Form
        form = tb.LabelFrame(self, text="Add / Update Battery")
        form.pack(fill=X, padx=10, pady=5)

        inner = tb.Frame(form, padding=10)
        inner.pack(fill=X)

        font = ("Segoe UI", 11)

        self.name = tb.Entry(inner, font=font)
        self.brand = tb.Entry(inner, font=font)
        self.capacity = tb.Entry(inner, font=font)
        self.type_var = tb.StringVar()
        self.type = tb.Combobox(
            inner,
            textvariable=self.type_var,
            values=get_battery_types(),
            font=font,
            state="normal"
        )
        self.type.set("")
        self.purchase = tb.Entry(inner, font=font)
        self.selling = tb.Entry(inner, font=font)
        self.qty = tb.Entry(inner, font=font)

        labels = ["Name", "Brand", "Capacity", "Type", "Purchase", "Selling", "Qty"]
        widgets = [self.name, self.brand, self.capacity, self.type, self.purchase, self.selling, self.qty]

        for i, (l, w) in enumerate(zip(labels, widgets)):
            tb.Label(inner, text=l).grid(row=i//4, column=(i%4)*2, padx=5, pady=5)
            w.grid(row=i//4, column=(i%4)*2+1, padx=5, pady=5)

        # Buttons
        btn = tb.Frame(self)
        btn.pack(fill=X, padx=10)

        tb.Button(btn, text="Add", bootstyle=SUCCESS, command=self.add_data).pack(side=LEFT, padx=5)
        tb.Button(btn, text="Update", bootstyle=WARNING, command=self.update_data).pack(side=LEFT, padx=5)
        tb.Button(btn, text="Delete", bootstyle=DANGER, command=self.delete_data).pack(side=LEFT, padx=5)
        tb.Button(btn, text="Clear", bootstyle=SECONDARY, command=self.clear_all).pack(side=LEFT, padx=5)

        # -------- TABLE FRAME -------- #
        table_frame = tb.Frame(self)
        table_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # -------- TREEVIEW -------- #
        self.table = tb.Treeview(
            table_frame,
            columns=("ID", "Serial", "Name", "Brand", "Capacity", "Type",
                    "Purchase", "Selling", "Qty", "Profit"),
            show="headings"
        )
        # Style

        style = tb.Style()
        style.configure("Custom.Treeview", font=("Segoe UI", 11), rowheight=38)
        style.map("Custom.Treeview",
                background=[("selected", "#6c757d")],
                foreground=[("selected", "white")])

        self.table.configure(style="Custom.Treeview")

        # ZEBRA COLORS
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

        # -------- HORIZONTAL SCROLLBAR ONLY -------- #
        scroll_x = tb.Scrollbar(table_frame, orient=HORIZONTAL, command=self.table.xview)
        self.table.configure(xscrollcommand=scroll_x.set)

        # -------- PACK -------- #
        self.table.pack(fill=BOTH, expand=True)
        scroll_x.pack(fill=X)

        # -------- FORCE WIDTH (IMPORTANT) -------- #
        # (This ensures overflow so scrollbar appears)
        self.table.column("ID", width=80)
        self.table.column("Serial", width=150)
        self.table.column("Name", width=200)
        self.table.column("Brand", width=200)
        self.table.column("Capacity", width=150)
        self.table.column("Type", width=150)
        self.table.column("Purchase", width=150)
        self.table.column("Selling", width=150)
        self.table.column("Qty", width=120)
        self.table.column("Profit", width=150)

        # -------- HEADINGS -------- #
        for col in self.table["columns"]:
            self.table.heading(col, text=col)
            self.table.column(col, anchor=CENTER)

        self.table.tag_configure("low", background="#fff3cd", foreground="black")
        self.table.bind("<ButtonRelease-1>", self.select_row)

        # Pagination
        nav = tb.Frame(self)
        nav.pack(fill=X, padx=10, pady=5)

        tb.Button(nav, text="<< Prev", command=self.prev_page).pack(side=LEFT)
        tb.Button(nav, text="Next >>", command=self.next_page).pack(side=LEFT)

        self.page_label = tb.Label(nav, text="Page 1")
        self.page_label.pack(side=LEFT, padx=10)

    def on_search(self, event):
        self.search_text = self.search_entry.get()
        self.page = 0
        self.load_data()


    def add_data(self):
        data = self.get_form_data()
        battery_type = data[3]
        cursor.execute(
            "INSERT OR IGNORE INTO battery_types (name) VALUES (?)",
            (battery_type,)
        )
        if not data:
            return

        serial = str(uuid.uuid4())[:8]  # auto-generate serial

        cursor.execute("""
        INSERT INTO batteries (
            serial, name, brand, capacity, type,
            purchase_price, selling_price, quantity
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            serial,
            data[0],  # name
            data[1],  # brand
            data[2],  # capacity
            data[3],  # type
            data[4],  # purchase_price
            data[5],  # selling_price
            data[6],  # quantity
        ))

        conn.commit()
        self.type["values"] = get_battery_types()
        self.load_data()
        self.clear_all()

    def update_data(self):
        if not self.selected_id:
            messagebox.showerror("Error", "Select record first")
            return

        data = self.get_form_data()
        battery_type = data[3]
        cursor.execute(
            "INSERT OR IGNORE INTO battery_types (name) VALUES (?)",
            (battery_type,)
        )
        if not data:
            return

        cursor.execute("""
        UPDATE batteries SET name=?,brand=?,capacity=?,type=?,purchase_price=?,selling_price=?,quantity=?
        WHERE id=?""", (*data, self.selected_id))
        conn.commit()
        self.type["values"] = get_battery_types()
        self.load_data()
        self.clear_all()

    def delete_data(self):
        if not self.selected_id:
            return

        cursor.execute("DELETE FROM batteries WHERE id=?", (self.selected_id,))
        conn.commit()

        self.load_data()
        self.clear_all()

    def load_data(self):
        for row in self.table.get_children():
            self.table.delete(row)

        query = "SELECT * FROM batteries WHERE name LIKE ? OR brand LIKE ?"
        params = (f"%{self.search_text}%", f"%{self.search_text}%")

        query += " LIMIT ? OFFSET ?"
        params += (self.limit, self.page * self.limit)

        cursor.execute(query, params)

        for i, r in enumerate(cursor.fetchall()):
            profit = float(r["selling_price"]) - float(r["purchase_price"])
            tag = "even" if i % 2 == 0 else "odd"

            if r["quantity"] < 5:
                tag = "low"

            self.table.insert("", END, values=(
                r["id"],
                r["serial"],
                r["name"],
                r["brand"],
                r["capacity"],
                r["type"],
                r["purchase_price"],
                r["selling_price"],
                r["quantity"],
                profit
            ), tags=(tag,))

        self.page_label.config(text=f"Page {self.page + 1}")

    def next_page(self):
        self.page += 1
        self.load_data()

    def prev_page(self):
        if self.page > 0:
            self.page -= 1
            self.load_data()

    def select_row(self, event):
        selected = self.table.focus()
        data = self.table.item(selected, "values")

        if data:
            self.selected_id = data[0]
            self.clear_fields()

            self.name.insert(0, data[2])
            self.brand.insert(0, data[3])
            self.capacity.insert(0, data[4])
            self.type.set(data[5])
            self.purchase.insert(0, data[6])
            self.selling.insert(0, data[7])
            self.qty.insert(0, data[8])

    def clear_fields(self):
        for f in [self.name, self.brand, self.capacity, self.purchase, self.selling, self.qty]:
            f.delete(0, END)
        self.type.set("")

    def clear_all(self):
        self.selected_id = None
        self.clear_fields()

    def get_form_data(self):
        try:
            return (
                self.name.get(),
                self.brand.get(),
                self.capacity.get(),
                self.type.get(),
                float(self.purchase.get()),
                float(self.selling.get()),
                int(self.qty.get())
            )
        except:
            messagebox.showerror("Error", "Invalid input")
            return None
    