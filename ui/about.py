import ttkbootstrap as tb
from ttkbootstrap.constants import *
import os
import sys
from utils.version import get_version

version = get_version()


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class AboutDialog:
    def __init__(self, master):
        popup = tb.Toplevel(master)
        popup.title("About")
        popup.geometry("400x300")
        popup.resizable(False, False)
        popup.iconbitmap(resource_path("assets/icon.ico"))
        
        popup.transient(master)
        popup.grab_set()

        container = tb.Frame(popup, padding=20)
        container.pack(fill=BOTH, expand=True)

        tb.Label(
            container,
            text="BSMS",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=(0, 10))

        tb.Label(
            container,
            text="Battery Sales Management System"
        ).pack()

        tb.Separator(container).pack(fill=X, pady=10)

        tb.Label(container, text=f"Version: {version}").pack(anchor="w")
        tb.Label(container, text="Developed by: Shreekant N.K").pack(anchor="w")
        tb.Label(container, text="License: MIT").pack(anchor="w")

        tb.Button(
            container,
            text="Close",
            command=popup.destroy
        ).pack(pady=15)