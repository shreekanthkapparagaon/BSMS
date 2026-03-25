import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ui.login import LoginScreen
from ui.dashboard import Dashboard
from ui.inventory import InventoryApp
from ui.sales import SalesApp
from ui.customers import CustomerApp
from ui.users import UserManagement
from ui.settings import SettingsPage
from auth import check_permission
from PIL import Image, ImageTk
import os
import sys
from dotenv import load_dotenv
load_dotenv()

DEV_MODE = os.getenv("APP_MODE") == "DEV"

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def load_icon(path, size=(20, 20)):
    img = Image.open(resource_path(path)).resize(size)
    return ImageTk.PhotoImage(img)

def load_logo(path, size=(60, 60)):
    img = Image.open(resource_path(path)).resize(size)
    return ImageTk.PhotoImage(img)

class MainApp(tb.Window):
    def __init__(self):
        super().__init__(themename="superhero")
        icon_path = resource_path("assets/icon.ico")
        self.iconbitmap(icon_path)
        self.title("BSMS")
        self.state("zoomed")
        self.user = None
        self.frames = {}
        self.active_frame = None
        self.active_btn = None

        if DEV_MODE:
            # auto login user
            self.user = {
                "username": "admin",
                "role": "admin"
            }
            self.show_main()
        else:
            self.show_login()

    def show_login(self):
        self.frames = {}
        self.clear()
        LoginScreen(self, self.on_login)

    def on_login(self, user):
        self.user = user
        self.show_main()
    
    def show_main(self):
        self.frames = {}
        self.clear()

        container = tb.Frame(self)
        container.pack(fill=BOTH, expand=True)

        sidebar = tb.Frame(container, width=220, bootstyle="dark")
        sidebar.pack(side=LEFT, fill=Y)

        self.content = tb.Frame(container)
        self.content.pack(side=RIGHT, fill=BOTH, expand=True)

        role = self.user["role"]

        # -------- HEADER -------- #
        self.logo = load_logo(resource_path("assets/logo.png"))
        top_logo = tb.Frame(sidebar)
        top_logo.pack(pady=(20, 10))

        tb.Label(top_logo, image=self.logo).pack()

        tb.Label(
            top_logo,
            text="Battery Sales\nManagement",
            font=("Segoe UI", 10),
            justify="center",
            foreground="#adb5bd"
        ).pack()

        tb.Label(
            sidebar,
            text=f"Welcome, {self.user['username']}",
            font=("Segoe UI", 9),
            foreground="white"
        ).pack(pady=(0, 10))
        tb.Separator(sidebar).pack(fill=X, padx=10, pady=10)
        # -------- MENU BUTTON -------- #
        self.icons = {
            "dashboard": load_icon(resource_path("assets/icons/dashboard.png")),
            "inventory": load_icon(resource_path("assets/icons/inventory.png")),
            "customers": load_icon(resource_path("assets/icons/customers.png")),
            "sales": load_icon(resource_path("assets/icons/sales.png")),
            "users": load_icon(resource_path("assets/icons/users.png")),
            "logout": load_icon(resource_path("assets/icons/logout.png")),
            "settings": load_icon(resource_path("assets/icons/settings.png")),
        }
        def menu_btn(text, icon, frame_class):
            btn = tb.Button(
                sidebar,
                text=f"   {text}",
                image=self.icons[icon],
                compound=LEFT,
                bootstyle="secondary",
                padding=(10, 8)
            )

            # click action
            btn.configure(command=lambda: self.show(frame_class, btn))

            # HOVER EFFECT
            def on_enter(e):
                if btn != self.active_btn:
                    btn.configure(bootstyle="primary")

            def on_leave(e):
                if btn != self.active_btn:
                    btn.configure(bootstyle="secondary")

            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)

            btn.pack(fill=X, padx=10, pady=4)
            return btn

        # -------- MENU ITEMS -------- #
        if role == "admin":
            btn_dashboard = menu_btn("Dashboard", "dashboard", Dashboard)

        if check_permission(role, "inventory")[0]:
            btn_inventory = menu_btn("Inventory", "inventory", InventoryApp)

        if check_permission(role, "customers")[0]:
            btn_customers = menu_btn("Customers", "customers", CustomerApp)

        if check_permission(role, "sales")[0]:
            btn_sales = menu_btn("Sales", "sales", SalesApp)

        if check_permission(role, "users")[0]:
            btn_users = menu_btn("Users", "users", UserManagement)

        if check_permission(role, "settings"):
            menu_btn("Settings", "settings", SettingsPage)
        # -------- LOGOUT -------- #
        tb.Button(
            sidebar,
            text="  Logout",
            image=self.icons["logout"],
            compound=LEFT,
            bootstyle=DANGER,
            command=self.show_login,
            padding=10
        ).pack(side=BOTTOM, fill=X, padx=10, pady=10)

        # -------- DEFAULT SCREEN -------- #
        if role == "admin":
            self.show(Dashboard, btn_dashboard)
        else:
            self.show(SalesApp, btn_sales)

    def show(self, frame_class, btn):
        # Reset previous button

        if self.active_btn and self.active_btn.winfo_exists():
            self.active_btn.configure(bootstyle="secondary")

        # Hide current frame
        if self.active_frame:
            self.active_frame.pack_forget()

        # Create frame if not cached
        if frame_class not in self.frames:
            if frame_class == UserManagement:
                frame = frame_class(self.content, self.user["role"])
            else:
                frame = frame_class(self.content, self.user)
            self.frames[frame_class] = frame
        else:
            frame = self.frames[frame_class]

        # Show frame
        frame.pack(fill=BOTH, expand=True)
        frame.update_idletasks()
        frame.update()

        # Update active states
        self.active_frame = frame
        self.active_btn = btn
        btn.configure(bootstyle="primary")
        self.content.update_idletasks()
    def clear(self):
        for w in self.winfo_children():
            w.destroy()


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()