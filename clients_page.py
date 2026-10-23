
import csv
import sqlite3
import customtkinter as ctk

from tkinter import ttk, messagebox, filedialog

from models import (
    list_clients,
    find_client,
    create_client,
    update_client,
    delete_client,
    client_has_reservations
)

from table_style import configure_table_style, GOLD


FIELDS = [
    ("name", "Name"),
    ("nif", "NIF"),
    ("email", "Email"),
    ("phone", "Phone"),
    ("address", "Address")
]


def show_clients_page(parent):
    """Displays the client management page."""

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
        text="Clients",
        font=ctk.CTkFont(size=28, weight="bold")
    ).pack(anchor="w")

    ctk.CTkLabel(
        header_frame,
        text="Manage your clients",
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
        placeholder_text="Search clients...",
        width=210,
        height=38
    )
    search_entry.pack(side="left", padx=(0, 10))

    buttons_frame = ctk.CTkFrame(
        toolbar,
        fg_color="transparent"
    )
    buttons_frame.pack(side="left")

    # Table container

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

    columns = (
        "id",
        "name",
        "nif",
        "email",
        "phone",
        "address",
        "created_at"
    )

    headings = {
        "id": "ID",
        "name": "Name",
        "nif": "NIF",
        "email": "Email",
        "phone": "Phone",
        "address": "Address",
        "created_at": "Registration Date"
    }

    widths = {
        "id": 45,
        "name": 160,
        "nif": 100,
        "email": 200,
        "phone": 110,
        "address": 190,
        "created_at": 150
    }

    tree = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings",
        style="Luxury.Treeview",
        selectmode="browse"
    )

    for column in columns:

        tree.heading(
            column,
            text=headings[column],
            anchor="center"
        )

        tree.column(
            column,
            width=widths[column],
            minwidth=40,
            stretch=False,
            anchor="center"
        )

    scrollbar_y = ttk.Scrollbar(
        table_frame,
        orient="vertical",
        command=tree.yview
    )

    scrollbar_x = ttk.Scrollbar(
        table_frame,
        orient="horizontal",
        command=tree.xview
    )

    tree.configure(
        yscrollcommand=scrollbar_y.set,
        xscrollcommand=scrollbar_x.set
    )

    tree.grid(
        row=0,
        column=0,
        sticky="nsew",
        padx=(10, 0),
        pady=(10, 0)
    )

    scrollbar_y.grid(
        row=0,
        column=1,
        sticky="ns",
        pady=(10, 0),
        padx=(0, 10)
    )

    scrollbar_x.grid(
        row=1,
        column=0,
        sticky="ew",
        padx=(10, 0),
        pady=(0, 10)
    )

    # Client count

    count_label = ctk.CTkLabel(
        parent,
        text="0 clients",
        text_color="#AFAFAF",
        font=ctk.CTkFont(size=12)
    )
    count_label.pack(
        anchor="w",
        padx=25,
        pady=(3, 10)
    )

    # Load clients

    def load_clients():
        """Refreshes and filters the clients table."""

        search_text = search_entry.get().strip().lower()

        for item in tree.get_children():
            tree.delete(item)

        clients = list_clients()

        if search_text:
            clients = [
                client
                for client in clients
                if any(
                    search_text in str(client[field] or "").lower()
                    for field in (
                        "name",
                        "nif",
                        "email",
                        "phone",
                        "address"
                    )
                )
            ]

        for client in clients:
            tree.insert(
                "",
                "end",
                values=(
                    client["id"],
                    client["name"],
                    client["nif"],
                    client["email"],
                    client["phone"],
                    client["address"],
                    client["created_at"]
                )
            )

        count_label.configure(
            text=f"{len(clients)} clients"
        )

    search_entry.bind(
        "<KeyRelease>",
        lambda event: load_clients()
    )

    # Selected client

    def get_selected_client_id():
        """Returns the selected client ID."""

        selection = tree.selection()

        if not selection:
            messagebox.showwarning(
                "Warning",
                "Please select a client.",
                parent=parent.winfo_toplevel()
            )
            return None

        return int(
            tree.item(selection[0], "values")[0]
        )

    # Client form

    def open_client_form(client_id=None):
        """Opens the client form."""

        client = (
            find_client(client_id)
            if client_id is not None
            else None
        )

        if client_id is not None and client is None:
            messagebox.showerror(
                "Error",
                "Client not found."
            )
            return

        window = ctk.CTkToplevel(parent)

        window.title(
            "Edit Client" if client else "Add Client"
        )

        window.geometry("650x480")
        window.minsize(600, 450)
        window.transient(parent.winfo_toplevel())

        form = ctk.CTkFrame(
            window,
            fg_color="transparent"
        )
        form.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=25
        )

        form.grid_columnconfigure(0, weight=1)
        form.grid_columnconfigure(1, weight=1)

        entries = {}

        for index, (field, label) in enumerate(FIELDS):

            row = index // 2
            column = index % 2

            field_frame = ctk.CTkFrame(
                form,
                fg_color="transparent"
            )

            field_frame.grid(
                row=row,
                column=column,
                sticky="ew",
                padx=10,
                pady=12
            )

            ctk.CTkLabel(
                field_frame,
                text=label
            ).pack(
                anchor="w",
                pady=(0, 5)
            )

            entry = ctk.CTkEntry(
                field_frame,
                height=35
            )
            entry.pack(fill="x")

            if client and client[field] is not None:
                entry.insert(
                    0,
                    str(client[field])
                )

            entries[field] = entry

        def save_client():
            """Creates or updates a client."""

            values = {
                field: entry.get().strip()
                for field, entry in entries.items()
            }

            if any(not value for value in values.values()):
                messagebox.showerror(
                    "Error",
                    "Please fill in all fields.",
                    parent=window
                )
                return

            if (
                not values["nif"].isdigit()
                or len(values["nif"]) != 9
            ):
                messagebox.showerror(
                    "Error",
                    "NIF must contain exactly 9 digits.",
                    parent=window
                )
                return

            if "@" not in values["email"]:
                messagebox.showerror(
                    "Error",
                    "Please enter a valid email address.",
                    parent=window
                )
                return

            arguments = [
                values[field]
                for field, label in FIELDS
            ]

            try:
                if client_id is not None:

                    affected_rows = update_client(
                        client_id,
                        *arguments
                    )

                    if not affected_rows:
                        messagebox.showerror(
                            "Error",
                            "Client not found.",
                            parent=window
                        )
                        return

                    success_message = (
                        "Client updated successfully."
                    )

                else:
                    create_client(*arguments)

                    success_message = (
                        "Client created successfully."
                    )

                window.destroy()
                load_clients()

                messagebox.showinfo(
                    "Success",
                    success_message
                )

            except sqlite3.IntegrityError:
                messagebox.showerror(
                    "Error",
                    "A client with this NIF already exists.",
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
            text="Save Client",
            fg_color=GOLD,
            hover_color="#A8873E",
            text_color="#171717",
            width=200,
            height=40,
            command=save_client
        ).grid(
            row=3,
            column=0,
            columnspan=2,
            pady=25
        )

        window.after(100, window.grab_set)

    # Edit client

    def edit_client():
        """Edits the selected client."""

        client_id = get_selected_client_id()

        if client_id is not None:
            open_client_form(client_id)

    # Delete client

    def remove_client():
        """Deletes the selected client."""

        client_id = get_selected_client_id()

        if client_id is None:
            return

        if client_has_reservations(client_id):
            messagebox.showerror(
                "Error",
                "Cannot delete a client with reservations."
            )
            return

        if not messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this client?"
        ):
            return

        try:
            affected_rows = delete_client(client_id)

            if affected_rows:
                load_clients()

                messagebox.showinfo(
                    "Success",
                    "Client deleted successfully."
                )

        except Exception as error:
            messagebox.showerror(
                "Error",
                str(error)
            )

    # Export CSV

    def export_csv():
        """Exports all clients to a CSV file."""

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile="clients.csv",
            filetypes=[
                ("CSV files", "*.csv")
            ]
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

                writer.writerow(
                    ["ID"]
                    + [
                        label
                        for field, label in FIELDS
                    ]
                    + ["Registration Date"]
                )

                for client in list_clients():
                    writer.writerow(
                        [client["id"]]
                        + [
                            client[field]
                            for field, label in FIELDS
                        ]
                        + [client["created_at"]]
                    )

            messagebox.showinfo(
                "Success",
                "Clients exported successfully."
            )

        except Exception as error:
            messagebox.showerror(
                "Error",
                str(error)
            )

    # Action buttons

    buttons = [
        (
            "Add Client",
            lambda: open_client_form(),
            GOLD,
            "#A8873E"
        ),
        (
            "Edit",
            edit_client,
            "#383838",
            "#4A4A4A"
        ),
        (
            "Delete",
            remove_client,
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
            width=110 if text != "Add Client" else 130,
            height=38,
            fg_color=color,
            hover_color=hover_color,
            text_color=(
                "#171717"
                if text == "Add Client"
                else "#FFFFFF"
            ),
            command=command
        ).pack(
            side="left",
            padx=3
        )

    # Initial table load

    load_clients()

