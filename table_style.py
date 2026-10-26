from tkinter import ttk

GOLD = "#C9A34E"
BACKGROUND = "#242424"
TABLE_BACKGROUND = "#2B2B2B"
HEADER_BACKGROUND = "#343434"
TEXT = "#F5F5F5"
MUTED_TEXT = "#B0B0B0"


def configure_table_style():
    """Configures the shared dark table style."""

    style = ttk.Style()
    style.theme_use("clam")

    style.configure(
        "Luxury.Treeview",
        background=TABLE_BACKGROUND,
        foreground=TEXT,
        fieldbackground=TABLE_BACKGROUND,
        borderwidth=0,
        relief="flat",
        rowheight=42,
        font=("Segoe UI", 10),
    )

    style.configure(
        "Luxury.Treeview.Heading",
        background=HEADER_BACKGROUND,
        foreground=GOLD,
        borderwidth=0,
        relief="flat",
        padding=(12, 12),
        font=("Segoe UI", 10, "bold"),
    )

    style.map(
        "Luxury.Treeview",
        background=[("selected", "#62502B")],
        foreground=[("selected", "#FFFFFF")],
    )

    style.map("Luxury.Treeview.Heading", background=[("active", "#414141")])
