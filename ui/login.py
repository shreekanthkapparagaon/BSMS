import ttkbootstrap as tb
from tkinter import messagebox
from auth import login_user


class LoginScreen(tb.Frame):
    def __init__(self, master, on_login):
        super().__init__(master)
        self.pack(fill="both", expand=True)

        self.on_login = on_login

        # Center container
        container = tb.Frame(self)
        container.place(relx=0.5, rely=0.5, anchor="center")

        # Card / Form Frame (with border)
        card = tb.Frame(
            container,
            padding=30,
            borderwidth=2,
            relief="solid",   # gives border
        )
        card.pack()

        # Title
        tb.Label(
            card,
            text="Login",
            font=("Segoe UI", 28, "bold")
        ).pack(pady=(0, 20))

        # Username Label
        tb.Label(
            card,
            text="Username",
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w")

        # Username Entry
        self.user = tb.Entry(
            card,
            width=30,
            font=("Segoe UI", 13)
        )
        self.user.pack(pady=10, ipady=6)

        # Password Label
        tb.Label(
            card,
            text="Password",
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w")

        # Password Entry
        self.passw = tb.Entry(
            card,
            show="*",
            width=30,
            font=("Segoe UI", 13)
        )
        self.passw.pack(pady=10, ipady=6)

        # Login Button
        tb.Button(
            card,
            text="Login",
            width=20,
            bootstyle="primary",
            command=self.login
        ).pack(pady=20)

    def login(self):
        u = login_user(self.user.get(), self.passw.get())
        if u:
            self.on_login(u)
        else:
            messagebox.showerror("Error", "Invalid credentials")