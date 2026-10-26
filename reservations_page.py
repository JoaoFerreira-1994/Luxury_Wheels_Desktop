from tkinter import ttk, messagebox
from tkinter import filedialog
from tkcalendar import DateEntry
from datetime import datetime

import customtkinter as ctk
import csv

from models import (
    list_reservations,
    find_reservation,
    create_reservation,
    update_reservation,
    delete_reservation,
    list_clients,
    list_vehicles,
    list_payment_methods,
)
from table_style import configure_table_style, GOLD


def show_reservations_page(parent):
    """Displays the reservation management page."""

    for widget in parent.winfo_children():
        widget.destroy()

    configure_table_style()

    header = ctk.CTkFrame(parent, fg_color="transparent")
    header.pack(fill="x", padx=25, pady=(20, 10))

    ctk.CTkLabel(
        header, text="Reservations", font=ctk.CTkFont(size=28, weight="bold")
    ).pack(anchor="w")

    ctk.CTkLabel(
        header,
        text="Manage vehicle reservations",
        font=ctk.CTkFont(size=13),
        text_color="#AFAFAF",
    ).pack(anchor="w", pady=(3, 0))

    toolbar = ctk.CTkFrame(parent, fg_color="transparent")
    toolbar.pack(fill="x", padx=25, pady=(5, 12))

    search_entry = ctk.CTkEntry(
        toolbar, placeholder_text="Search reservations...", width=210, height=38
    )
    search_entry.pack(side="left", padx=(0, 10))

    buttons_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
    buttons_frame.pack(side="left")

    table_frame = ctk.CTkFrame(parent, fg_color="#292929", corner_radius=10)
    table_frame.pack(fill="both", expand=True, padx=25, pady=(0, 5))
    table_frame.grid_rowconfigure(0, weight=1)
    table_frame.grid_columnconfigure(0, weight=1)

    columns = (
        "id",
        "client",
        "vehicle",
        "start_date",
        "end_date",
        "total_price",
        "status",
    )

    headings = {
        "id": "ID",
        "client": "Client",
        "vehicle": "Vehicle",
        "start_date": "Start Date",
        "end_date": "End Date",
        "total_price": "Total Price",
        "status": "Status",
    }

    widths = {
        "id": 50,
        "client": 170,
        "vehicle": 190,
        "start_date": 110,
        "end_date": 110,
        "total_price": 110,
        "status": 110,
    }

    tree = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings",
        style="Luxury.Treeview",
        selectmode="browse",
    )

    for column in columns:
        tree.heading(column, text=headings[column], anchor="center")
        tree.column(
            column, width=widths[column], minwidth=45, stretch=False, anchor="center"
        )

    scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    scrollbar_x = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)

    tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

    tree.grid(row=0, column=0, sticky="nsew", padx=(10, 0), pady=(10, 0))
    scrollbar_y.grid(row=0, column=1, sticky="ns", padx=(0, 10), pady=(10, 0))
    scrollbar_x.grid(row=1, column=0, sticky="ew", padx=(10, 0), pady=(0, 10))

    count_label = ctk.CTkLabel(
        parent, text="0 reservations", text_color="#AFAFAF", font=ctk.CTkFont(size=12)
    )
    count_label.pack(anchor="w", padx=25, pady=(3, 10))

    def get_value(record, *keys, default=""):
        """Returns the first available non-null field."""
        for key in keys:
            if key in record and record[key] is not None:
                return record[key]
        return default

    def load_reservations():
        """Refreshes and filters the reservation table."""

        search_text = search_entry.get().strip().lower()

        for item in tree.get_children():
            tree.delete(item)

        reservations = list_reservations()

        if search_text:
            reservations = [
                reservation
                for reservation in reservations
                if search_text
                in " ".join(
                    str(value).lower()
                    for value in reservation.values()
                    if value is not None
                )
            ]

        for reservation in reservations:
            client_name = get_value(reservation, "client_name", "client")
            vehicle_name = get_value(reservation, "vehicle_name", "vehicle")
            total_price = get_value(reservation, "total_price", default=0)
            status = get_value(reservation, "status", default="confirmed")

            tree.insert(
                "",
                "end",
                values=(
                    reservation["id"],
                    client_name,
                    vehicle_name,
                    get_value(reservation, "start_date"),
                    get_value(reservation, "end_date"),
                    f"{float(total_price):.2f} €",
                    str(status).capitalize(),
                ),
            )

        count_label.configure(text=f"{len(reservations)} reservations")

    search_entry.bind("<KeyRelease>", lambda event: load_reservations())

    def get_selected_reservation_id():
        """Returns the selected reservation ID."""

        selection = tree.selection()

        if not selection:
            messagebox.showwarning(
                "Warning",
                "Please select a reservation.",
                parent=parent.winfo_toplevel(),
            )
            return None

        return int(tree.item(selection[0], "values")[0])

    def open_reservation_form(reservation_id=None):
        """Opens the add or edit reservation form."""

        reservation = (
            find_reservation(reservation_id) if reservation_id is not None else None
        )

        if reservation_id is not None and reservation is None:
            messagebox.showerror("Error", "Reservation not found.")
            return

        clients = list_clients()
        vehicles = list_vehicles()
        payment_methods = list_payment_methods()

        if not clients or not vehicles or not payment_methods:
            messagebox.showwarning(
                "Missing Data",
                "At least one client, vehicle and payment method are required.",
            )
            return

        window = ctk.CTkToplevel(parent)
        window.title("Edit Reservation" if reservation else "Add Reservation")
        window.geometry("800x550")
        window.minsize(700, 500)
        window.transient(parent.winfo_toplevel())

        form = ctk.CTkFrame(window, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=25, pady=25)

        form.grid_columnconfigure(0, weight=1)
        form.grid_columnconfigure(1, weight=1)

        client_options = {
            f"{client['id']} - {client['name']}": client["id"] for client in clients
        }

        vehicle_options = {
            (
                f"{vehicle['id']} - "
                f"{vehicle['brand']} {vehicle['model']} "
                f"({vehicle['license_plate']})"
            ): vehicle["id"]
            for vehicle in vehicles
        }

        payment_options = {
            f"{method['id']} - {method['name']}": method["id"]
            for method in payment_methods
        }

        def add_field(label, row, column, options=None):
            """Creates a labelled form field."""

            field_frame = ctk.CTkFrame(form, fg_color="transparent")
            field_frame.grid(row=row, column=column, sticky="ew", padx=10, pady=12)

            ctk.CTkLabel(field_frame, text=label).pack(anchor="w", pady=(0, 5))

            if options is not None:
                widget = ctk.CTkOptionMenu(
                    field_frame, values=list(options.keys()), height=35
                )
            else:
                widget = ctk.CTkEntry(field_frame, height=35)

            widget.pack(fill="x")
            return widget

        client_entry = add_field("Client", 0, 0, client_options)
        vehicle_entry = add_field("Vehicle", 0, 1, vehicle_options)
        payment_entry = add_field("Payment Method", 1, 0, payment_options)

        def add_date_field(label, row, column):
            """Creates a calendar date field."""

            field_frame = ctk.CTkFrame(form, fg_color="transparent")
            field_frame.grid(row=row, column=column, sticky="ew", padx=10, pady=12)

            ctk.CTkLabel(field_frame, text=label).pack(anchor="w", pady=(0, 5))

            date_entry = DateEntry(
                field_frame,
                date_pattern="yyyy-mm-dd",
                background="#C9A34E",
                foreground="#171717",
                headersbackground="#343434",
                headersforeground="#FFFFFF",
                selectbackground="#C9A34E",
                selectforeground="#171717",
                normalbackground="#2B2B2B",
                normalforeground="#FFFFFF",
                weekendbackground="#2B2B2B",
                weekendforeground="#FFFFFF",
                borderwidth=0,
                font=("Segoe UI", 11),
            )
            date_entry.pack(fill="x", ipady=7)

            return date_entry

        start_entry = add_date_field("Start Date", 1, 1)

        end_entry = add_date_field("End Date", 2, 0)

        if reservation:

            def select_option(widget, options, selected_id):
                """Selects an option using its database ID."""
                for label, option_id in options.items():
                    if str(option_id) == str(selected_id):
                        widget.set(label)
                        break

            select_option(client_entry, client_options, reservation["client_id"])
            select_option(vehicle_entry, vehicle_options, reservation["vehicle_id"])
            select_option(
                payment_entry, payment_options, reservation["payment_method_id"]
            )

            start_entry.set_date(
                datetime.strptime(reservation["start_date"][:10], "%Y-%m-%d")
            )

            end_entry.set_date(
                datetime.strptime(reservation["end_date"][:10], "%Y-%m-%d")
            )

        def save_reservation():
            """Creates or updates a reservation."""

            start_date = start_entry.get_date().isoformat()
            end_date = end_entry.get_date().isoformat()

            if not start_date or not end_date:
                messagebox.showerror(
                    "Error", "Please enter both reservation dates.", parent=window
                )
                return

            client_id = client_options[client_entry.get()]
            vehicle_id = vehicle_options[vehicle_entry.get()]
            payment_method_id = payment_options[payment_entry.get()]

            try:
                if reservation_id is not None:
                    result = update_reservation(
                        reservation_id,
                        client_id,
                        vehicle_id,
                        payment_method_id,
                        start_date,
                        end_date,
                    )
                    success_message = "Reservation updated successfully."
                else:
                    result = create_reservation(
                        client_id, vehicle_id, payment_method_id, start_date, end_date
                    )
                    success_message = "Reservation created successfully."

                if isinstance(result, dict) and result.get("error"):
                    messagebox.showerror("Error", str(result["error"]), parent=window)
                    return

                if (
                    reservation_id is not None
                    and isinstance(result, dict)
                    and result.get("affected_rows") == 0
                ):
                    messagebox.showerror(
                        "Error", "Reservation not found.", parent=window
                    )
                    return

                total_price = (
                    result.get("total_price") if isinstance(result, dict) else None
                )

                window.destroy()
                load_reservations()

                if total_price is not None:
                    success_message += f"\nTotal price: {float(total_price):.2f} €"

                messagebox.showinfo("Success", success_message)

            except Exception as error:
                messagebox.showerror("Error", str(error), parent=window)

        ctk.CTkButton(
            form,
            text="Save Reservation",
            fg_color=GOLD,
            hover_color="#A8873E",
            text_color="#171717",
            width=220,
            height=40,
            command=save_reservation,
        ).grid(row=3, column=0, columnspan=2, pady=30)

        window.after(100, window.grab_set)

    def edit_reservation():
        """Edits the selected reservation."""

        reservation_id = get_selected_reservation_id()

        if reservation_id is not None:
            open_reservation_form(reservation_id)

    def remove_reservation():
        """Deletes the selected reservation."""

        reservation_id = get_selected_reservation_id()

        if reservation_id is None:
            return

        if not messagebox.askyesno(
            "Confirm Delete", "Are you sure you want to delete this reservation?"
        ):
            return

        try:
            result = delete_reservation(reservation_id)

            if isinstance(result, dict) and result.get("error"):
                messagebox.showerror("Error", str(result["error"]))
                return

            load_reservations()
            messagebox.showinfo("Success", "Reservation deleted successfully.")

        except Exception as error:
            messagebox.showerror("Error", str(error))

    def export_csv():
        """Exports all reservations to a CSV file."""

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile="reservations.csv",
            filetypes=[("CSV files", "*.csv")],
        )

        if not file_path:
            return

        try:
            reservations = list_reservations()

            with open(file_path, "w", newline="", encoding="utf-8-sig") as file:

                writer = csv.writer(file, delimiter=";")

                writer.writerow(
                    [
                        "ID",
                        "Client",
                        "Vehicle",
                        "Payment Method",
                        "Start Date",
                        "End Date",
                        "Total Price",
                        "Status",
                    ]
                )

                for reservation in reservations:

                    writer.writerow(
                        [
                            reservation["id"],
                            reservation.get("client_name", ""),
                            reservation.get("vehicle_name", ""),
                            reservation.get(
                                "payment_method_name",
                                reservation.get("payment_method", ""),
                            ),
                            reservation["start_date"],
                            reservation["end_date"],
                            reservation["total_price"],
                            reservation.get("status", ""),
                        ]
                    )

            messagebox.showinfo("Success", "Reservations exported successfully.")

        except Exception as error:
            messagebox.showerror("Error", str(error))

    buttons = [
        ("Add Reservation", lambda: open_reservation_form(), GOLD, "#A8873E"),
        ("Edit", edit_reservation, "#383838", "#4A4A4A"),
        ("Delete", remove_reservation, "#383838", "#4A4A4A"),
        ("Export CSV", export_csv, "#383838", "#4A4A4A"),
    ]

    for text, command, color, hover_color in buttons:
        ctk.CTkButton(
            buttons_frame,
            text=text,
            width=145 if text == "Add Reservation" else 110,
            height=38,
            fg_color=color,
            hover_color=hover_color,
            text_color=("#171717" if text == "Add Reservation" else "#FFFFFF"),
            command=command,
        ).pack(side="left", padx=3)

    load_reservations()
