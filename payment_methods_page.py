
import sqlite3
from tkinter import ttk, messagebox, filedialog
import csv

import customtkinter as ctk

from models import (
    list_payment_methods,
    find_payment_method,
    create_payment_method,
    update_payment_method,
    delete_payment_method,
    payment_method_has_reservations
)

from table_style import configure_table_style, GOLD


def show_payment_methods_page(parent):
    """Displays the payment methods management page."""

    for widget in parent.winfo_children():
        widget.destroy()

    configure_table_style()

    # Page header

    header_frame = ctk.CTkFrame(
        parent,
        fg_color="transparent"
    )
    header_frame.pack(fill="x", padx=25, pady=(20, 10))

    ctk.CTkLabel(
        header_frame,
        text="Payment Methods",
        font=ctk.CTkFont(size=28, weight="bold")
    ).pack(anchor="w")

    ctk.CTkLabel(
        header_frame,
        text="Manage available payment methods",
        font=ctk.CTkFont(size=13),
        text_color="#AFAFAF"
    ).pack(anchor="w", pady=(3, 0))

    # Toolbar

    toolbar = ctk.CTkFrame(
        parent,
        fg_color="transparent"
    )
    toolbar.pack(fill="x", padx=25, pady=(5, 12))

    search_entry = ctk.CTkEntry(
        toolbar,
        placeholder_text="Search payment methods...",
        width=210,
        height=38
    )
    search_entry.pack(side="left", padx=(0, 10))

    buttons_frame = ctk.CTkFrame(
        toolbar,
        fg_color="transparent"
    )
    buttons_frame.pack(side="left")

    # Table

    table_frame = ctk.CTkFrame(
        parent,
        fg_color="#292929",
        corner_radius=10
    )
    table_frame.pack(
        fill="both",
        expand=True,
        padx=25,
        pady=(0, 5)
    )

    table_frame.grid_rowconfigure(0, weight=1)
    table_frame.grid_columnconfigure(0, weight=1)

    columns = ("id", "name")

    tree = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings",
        style="Luxury.Treeview",
        selectmode="browse"
    )

    tree.heading("id", text="ID", anchor="center")
    tree.heading("name", text="Payment Method", anchor="center")

    tree.column(
        "id",
        width=100,
        minwidth=70,
        stretch=False,
        anchor="center"
    )

    tree.column(
        "name",
        width=400,
        minwidth=200,
        stretch=True,
        anchor="center"
    )

    scrollbar_y = ttk.Scrollbar(
        table_frame,
        orient="vertical",
        command=tree.yview
    )

    tree.configure(yscrollcommand=scrollbar_y.set)

    tree.grid(
        row=0,
        column=0,
        sticky="nsew",
        padx=(10, 0),
        pady=10
    )

    scrollbar_y.grid(
        row=0,
        column=1,
        sticky="ns",
        padx=(0, 10),
        pady=10
    )

    # Payment method count

    count_label = ctk.CTkLabel(
        parent,
        text="0 payment methods",
        text_color="#AFAFAF",
        font=ctk.CTkFont(size=12)
    )
    count_label.pack(
        anchor="w",
        padx=25,
        pady=(3, 10)
    )

    # Load payment methods

    def load_payment_methods():
        """Refreshes and filters the payment methods table."""

        search_text = search_entry.get().strip().lower()

        for item in tree.get_children():
            tree.delete(item)

        payment_methods = list_payment_methods()

        if search_text:
            payment_methods = [
                method
                for method in payment_methods
                if search_text in str(method["name"]).lower()
            ]

        for method in payment_methods:
            tree.insert(
                "",
                "end",
                values=(
                    method["id"],
                    method["name"]
                )
            )

        count_label.configure(
            text=f"{len(payment_methods)} payment methods"
        )

    search_entry.bind(
        "<KeyRelease>",
        lambda event: load_payment_methods()
    )

    # Selected payment method

    def get_selected_payment_method_id():
        """Returns the selected payment method ID."""

        selection = tree.selection()

        if not selection:
            messagebox.showwarning(
                "Warning",
                "Please select a payment method.",
                parent=parent.winfo_toplevel()
            )
            return None

        return int(tree.item(selection[0], "values")[0])

    # Add / Edit form

    def open_payment_method_form(method_id=None):
        """Opens the payment method form."""

        method = (
            find_payment_method(method_id)
            if method_id is not None
            else None
        )

        if method_id is not None and method is None:
            messagebox.showerror(
                "Error",
                "Payment method not found."
            )
            return

        window = ctk.CTkToplevel(parent)

        window.title(
            "Edit Payment Method"
            if method
            else "Add Payment Method"
        )

        window.geometry("500x300")
        window.minsize(450, 280)
        window.transient(parent.winfo_toplevel())

        form = ctk.CTkFrame(
            window,
            fg_color="transparent"
        )
        form.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=30
        )

        ctk.CTkLabel(
            form,
            text="Payment Method Name",
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", pady=(10, 8))

        name_entry = ctk.CTkEntry(
            form,
            height=40,
            placeholder_text="Enter payment method name"
        )
        name_entry.pack(fill="x")

        if method:
            name_entry.insert(0, str(method["name"]))

        def save_payment_method():
            """Creates or updates a payment method."""

            name = name_entry.get().strip()

            if not name:
                messagebox.showerror(
                    "Error",
                    "Payment method name is required.",
                    parent=window
                )
                return

            try:
                if method_id is not None:
                    affected_rows = update_payment_method(
                        method_id,
                        name
                    )

                    if not affected_rows:
                        messagebox.showerror(
                            "Error",
                            "Payment method not found.",
                            parent=window
                        )
                        return

                    success_message = (
                        "Payment method updated successfully."
                    )

                else:
                    create_payment_method(name)

                    success_message = (
                        "Payment method created successfully."
                    )

                window.destroy()
                load_payment_methods()

                messagebox.showinfo(
                    "Success",
                    success_message
                )

            except sqlite3.IntegrityError:
                messagebox.showerror(
                    "Error",
                    "This payment method already exists.",
                    parent=window
                )

            except Exception as error:
                messagebox.showerror(
                    "Error",
                    str(error),
                    parent=window
                )

        ctk.CTkButton(
            form,
            text="Save Payment Method",
            fg_color=GOLD,
            hover_color="#A8873E",
            text_color="#171717",
            width=220,
            height=40,
            command=save_payment_method
        ).pack(pady=35)

        name_entry.focus_set()
        window.after(100, window.grab_set)

    # Edit payment method

    def edit_payment_method():
        """Edits the selected payment method."""

        method_id = get_selected_payment_method_id()

        if method_id is not None:
            open_payment_method_form(method_id)

    # Delete payment method

    def remove_payment_method():
        """Deletes the selected payment method."""

        method_id = get_selected_payment_method_id()

        if method_id is None:
            return

        if payment_method_has_reservations(method_id):
            messagebox.showerror(
                "Error",
                "Cannot delete a payment method with reservations."
            )
            return

        if not messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this payment method?",
            parent=parent.winfo_toplevel()
        ):
            return

        try:
            affected_rows = delete_payment_method(method_id)

            if affected_rows:
                load_payment_methods()

                messagebox.showinfo(
                    "Success",
                    "Payment method deleted successfully."
                )

        except Exception as error:
            messagebox.showerror(
                "Error",
                str(error)
            )

    # Export CSV

    def export_csv():
        """Exports all payment methods to a CSV file."""

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile="payment_methods.csv",
            filetypes=[("CSV files", "*.csv")]
        )

        if not file_path:
            return

        try:
            with open(
                file_path,
                "w",
                newline="",
                encoding="utf-8-sig"
            ) as file:

                writer = csv.writer(
                    file,
                    delimiter=";"
                )

                writer.writerow(["ID", "Payment Method"])

                for method in list_payment_methods():
                    writer.writerow([
                        method["id"],
                        method["name"]
                    ])

            messagebox.showinfo(
                "Success",
                "Payment methods exported successfully."
            )

        except Exception as error:
            messagebox.showerror(
                "Error",
                str(error)
            )

    # Action buttons

    buttons = [
        (
            "Add Payment Method",
            lambda: open_payment_method_form(),
            GOLD,
            "#A8873E"
        ),
        (
            "Edit",
            edit_payment_method,
            "#383838",
            "#4A4A4A"
        ),
        (
            "Delete",
            remove_payment_method,
            "#383838",
            "#4A4A4A"
        ),
        (
            "Export CSV",
            export_csv,
            "#383838",
            "#4A4A4A"
        )
    ]

    for text, command, color, hover_color in buttons:
        ctk.CTkButton(
            buttons_frame,
            text=text,
            width=175 if text == "Add Payment Method" else 110,
            height=38,
            fg_color=color,
            hover_color=hover_color,
            text_color=(
                "#171717"
                if text == "Add Payment Method"
                else "#FFFFFF"
            ),
            command=command
        ).pack(side="left", padx=3)

    load_payment_methods()

