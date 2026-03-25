import ttkbootstrap as tb

def style_table(tree):
    style = tb.Style()
    style.configure("Custom.Treeview", rowheight=36)
    tree.configure(style="Custom.Treeview")

def add_hover(tree):
    def on_hover(e):
        row = tree.identify_row(e.y)
        for item in tree.get_children():
            tree.item(item, tags=())
        if row:
            tree.item(row, tags=("hover",))

    tree.bind("<Motion>", on_hover)