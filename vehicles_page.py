import csv
import sqlite3
from datetime import datetime
from tkinter import ttk, messagebox, filedialog

import customtkinter as ctk
from tkcalendar import Calendar

from models import (
    list_vehicles,
    find_vehicle,
    create_vehicle,
    update_vehicle,
    delete_vehicle,
    vehicle_has_reservations,
)

from table_style import configure_table_style, GOLD

FIELDS = [
    ("brand", "Brand"),
    ("model", "Model"),
    ("license_plate", "License Plate"),
    ("category", "Category"),
    ("transmission", "Transmission"),
    ("vehicle_type", "Vehicle Type"),
    ("capacity", "Capacity"),
    ("image_path", "Image Path"),
    ("daily_price", "Daily Price"),
    ("last_revision_date", "Last Revision Date"),
    ("next_revision_date", "Next Revision Date"),
    ("last_inspection_date", "Last Inspection Date"),
    ("next_inspection_date", "Next Inspection Date"),
    ("last_legalization_date", "Last Legalization Date"),
    ("status", "Status"),
]


def show_vehicles_page(parent):
    """Displays the vehicle management page."""

    for widget in parent.winfo_children():
        widget.destroy()

    configure_table_style()

    # Page header

    header_frame = ctk.CTkFrame(parent, fg_color="transparent")
    header_frame.pack(fill="x", padx=25, pady=(20, 10))

    ctk.CTkLabel(
        header_frame, text="Vehicles", font=ctk.CTkFont(size=28, weight="bold")
    ).pack(anchor="w")

    ctk.CTkLabel(
        header_frame,
        text="Manage your rental fleet",
        font=ctk.CTkFont(size=13),
        text_color="#AFAFAF",
    ).pack(anchor="w", pady=(3, 0))

    # Toolbar

    toolbar = ctk.CTkFrame(parent, fg_color="transparent")
    toolbar.pack(fill="x", padx=25, pady=(5, 12))

    search_entry = ctk.CTkEntry(
        toolbar, placeholder_text="Search vehicles...", width=210, height=38
    )
    search_entry.pack(side="left", padx=(0, 10))

    buttons_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
    buttons_frame.pack(side="left")

    # Table container

    table_frame = ctk.CTkFrame(parent, fg_color="#292929", corner_radius=10)
    table_frame.pack(fill="both", expand=True, padx=25, pady=(0, 5))

    table_frame.grid_rowconfigure(0, weight=1)
    table_frame.grid_columnconfigure(0, weight=1)

    columns = (
        "id",
        "brand",
        "model",
        "license_plate",
        "category",
        "daily_price",
        "status",
    )

    headings = {
        "id": "ID",
        "brand": "Brand",
        "model": "Model",
        "license_plate": "License Plate",
        "category": "Category",
        "daily_price": "Price / Day",
        "status": "Status",
    }

    widths = {
        "id": 45,
        "brand": 120,
        "model": 130,
        "license_plate": 115,
        "category": 100,
        "daily_price": 105,
        "status": 100,
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
            column, width=widths[column], minwidth=40, stretch=False, anchor="center"
        )

    tree.column("id", anchor="center")
    tree.column("daily_price", anchor="e")

    scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)

    scrollbar_x = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)

    tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

    tree.grid(row=0, column=0, sticky="nsew", padx=(10, 0), pady=(10, 0))

    scrollbar_y.grid(row=0, column=1, sticky="ns", pady=(10, 0), padx=(0, 10))

    scrollbar_x.grid(row=1, column=0, sticky="ew", padx=(10, 0), pady=(0, 10))

    # Vehicle count

    count_label = ctk.CTkLabel(
        parent, text="0 vehicles", text_color="#AFAFAF", font=ctk.CTkFont(size=12)
    )
    count_label.pack(anchor="w", padx=25, pady=(3, 10))

    # Load vehicles

    def load_vehicles(search_text=None):
        """Refreshes and filters the vehicles table."""

        if search_text is None:
            search_text = search_entry.get()

        search_text = search_text.strip().lower()

        for item in tree.get_children():
            tree.delete(item)

        vehicles = list_vehicles()

        if search_text:
            vehicles = [
                vehicle
                for vehicle in vehicles
                if any(
                    search_text in str(vehicle[field] or "").lower()
                    for field in (
                        "brand",
                        "model",
                        "license_plate",
                        "category",
                        "status",
                    )
                )
            ]

        for vehicle in vehicles:
            tree.insert(
                "",
                "end",
                values=(
                    vehicle["id"],
                    vehicle["brand"],
                    vehicle["model"],
                    vehicle["license_plate"],
                    vehicle["category"],
                    f"{vehicle['daily_price']:.2f} €",
                    str(vehicle["status"]).capitalize(),
                ),
            )

        count_label.configure(text=f"{len(vehicles)} vehicles")

    search_entry.bind("<KeyRelease>", lambda event: load_vehicles())

    # Selected vehicle

    def get_selected_vehicle_id():
        """Returns the selected vehicle ID."""

        selection = tree.selection()

        if not selection:
            messagebox.showwarning(
                "Warning", "Please select a vehicle.", parent=parent.winfo_toplevel()
            )
            return None

        return int(tree.item(selection[0], "values")[0])

    # Vehicle form

    def open_vehicle_form(vehicle_id=None):
        """Opens the vehicle form."""

        vehicle = find_vehicle(vehicle_id) if vehicle_id is not None else None

        if vehicle_id is not None and vehicle is None:
            messagebox.showerror("Error", "Vehicle not found.")
            return

        window = ctk.CTkToplevel(parent)

        window.title("Edit Vehicle" if vehicle else "Add Vehicle")

        window.geometry("800x770")
        window.minsize(800, 650)
        window.transient(parent.winfo_toplevel())

        form = ctk.CTkScrollableFrame(window)
        form.pack(fill="both", expand=True, padx=20, pady=20)

        entries = {}

        date_fields = {
            "last_revision_date",
            "next_revision_date",
            "last_inspection_date",
            "next_inspection_date",
            "last_legalization_date",
        }

        form.grid_columnconfigure(0, weight=1)
        form.grid_columnconfigure(1, weight=1)

        def open_calendar(date_entry):
            """Opens a calendar to select an optional vehicle date."""

            calendar_window = ctk.CTkToplevel(window)
            calendar_window.title("Select Date")
            calendar_window.geometry("340x360")
            calendar_window.resizable(False, False)
            calendar_window.transient(window)

            calendar_options = {
                "date_pattern": "yyyy-mm-dd",
                "background": "#C9A34E",
                "foreground": "#171717",
                "headersbackground": "#343434",
                "headersforeground": "#FFFFFF",
                "selectbackground": "#C9A34E",
                "selectforeground": "#171717",
                "normalbackground": "#2B2B2B",
                "normalforeground": "#FFFFFF",
                "weekendbackground": "#2B2B2B",
                "weekendforeground": "#FFFFFF",
            }

            current_value = date_entry.get().strip()
            if current_value:
                try:
                    selected_date = datetime.strptime(current_value[:10], "%Y-%m-%d")
                    calendar_options.update(
                        {
                            "year": selected_date.year,
                            "month": selected_date.month,
                            "day": selected_date.day,
                        }
                    )
                except ValueError:
                    pass

            calendar = Calendar(calendar_window, **calendar_options)
            calendar.pack(fill="both", expand=True, padx=15, pady=15)

            def select_date():
                """Copies the selected calendar date to the form."""
                date_entry.configure(state="normal")
                date_entry.delete(0, "end")
                date_entry.insert(0, calendar.selection_get().isoformat())
                date_entry.configure(state="readonly")
                calendar_window.destroy()

            ctk.CTkButton(
                calendar_window,
                text="Select Date",
                fg_color=GOLD,
                hover_color="#A8873E",
                text_color="#171717",
                command=select_date,
            ).pack(pady=(0, 15))

            calendar_window.after(100, calendar_window.grab_set)

        def clear_date(date_entry):
            """Clears an optional date field."""
            date_entry.configure(state="normal")
            date_entry.delete(0, "end")
            date_entry.configure(state="readonly")

        for index, (field, label) in enumerate(FIELDS):
            row = index // 2
            column = index % 2

            field_frame = ctk.CTkFrame(form, fg_color="transparent")
            field_frame.grid(row=row, column=column, sticky="ew", padx=12, pady=8)

            ctk.CTkLabel(field_frame, text=label).pack(anchor="w", pady=(0, 5))

            if field == "status":
                entry = ctk.CTkOptionMenu(
                    field_frame, values=["available", "rented", "maintenance"]
                )
                entry.pack(fill="x")

            elif field == "transmission":
                entry = ctk.CTkOptionMenu(field_frame, values=["Manual", "Automatic"])
                entry.pack(fill="x")

            elif field in date_fields:
                date_row = ctk.CTkFrame(field_frame, fg_color="transparent")
                date_row.pack(fill="x")

                entry = ctk.CTkEntry(
                    date_row, placeholder_text="YYYY-MM-DD", state="normal"
                )
                entry.pack(side="left", fill="x", expand=True)

                ctk.CTkButton(
                    date_row,
                    text="📅",
                    width=40,
                    fg_color=GOLD,
                    hover_color="#A8873E",
                    text_color="#171717",
                    command=lambda e=entry: open_calendar(e),
                ).pack(side="left", padx=(5, 0))

                ctk.CTkButton(
                    date_row,
                    text="×",
                    width=30,
                    fg_color="#383838",
                    hover_color="#4A4A4A",
                    command=lambda e=entry: clear_date(e),
                ).pack(side="left", padx=(5, 0))

            else:
                entry = ctk.CTkEntry(field_frame)
                entry.pack(fill="x")

            if vehicle and vehicle[field] is not None:
                if isinstance(entry, ctk.CTkOptionMenu):
                    entry.set(str(vehicle[field]))
                else:
                    entry.insert(0, str(vehicle[field]))

            if field in date_fields:
                entry.configure(state="readonly")

            entries[field] = entry

        if not vehicle:
            entries["status"].set("available")
            entries["transmission"].set("Manual")

        def save_vehicle():
            """Creates or updates a vehicle."""

            values = {field: entry.get().strip() for field, entry in entries.items()}

            required_fields = [
                "brand",
                "model",
                "license_plate",
                "category",
                "vehicle_type",
                "capacity",
                "daily_price",
                "status",
            ]

            if any(not values[field] for field in required_fields):
                messagebox.showerror(
                    "Error", "Please fill in all required fields.", parent=window
                )
                return

            try:
                values["capacity"] = int(values["capacity"])

                values["daily_price"] = float(values["daily_price"])

                if values["capacity"] <= 0:
                    raise ValueError("Capacity must be greater than zero.")

                if values["daily_price"] <= 0:
                    raise ValueError("Daily price must be greater than zero.")

                date_fields = [
                    "last_revision_date",
                    "next_revision_date",
                    "last_inspection_date",
                    "next_inspection_date",
                    "last_legalization_date",
                ]

                for field in date_fields:
                    if values[field]:
                        datetime.strptime(values[field], "%Y-%m-%d")

                arguments = [values[field] for field, label in FIELDS]

                if vehicle_id is not None:
                    affected_rows = update_vehicle(vehicle_id, *arguments)

                    if not affected_rows:
                        messagebox.showerror(
                            "Error", "Vehicle not found.", parent=window
                        )
                        return

                    success_message = "Vehicle updated successfully."

                else:
                    create_vehicle(*arguments)

                    success_message = "Vehicle created successfully."

                window.destroy()
                load_vehicles()

                messagebox.showinfo("Success", success_message)

            except ValueError as error:
                messagebox.showerror(
                    "Error", f"Invalid value or date: {error}", parent=window
                )

            except sqlite3.IntegrityError as error:
                messagebox.showerror(
                    "Error", f"Database constraint: {error}", parent=window
                )

            except Exception as error:
                messagebox.showerror("Error", str(error), parent=window)

        ctk.CTkButton(
            form,
            text="Save Vehicle",
            fg_color=GOLD,
            hover_color="#A8873E",
            text_color="#171717",
            width=200,
            height=40,
            command=save_vehicle,
        ).grid(row=(len(FIELDS) + 1) // 2, column=0, columnspan=2, pady=25)

    # Edit vehicle
    def edit_vehicle():
        """Edits the selected vehicle."""

        vehicle_id = get_selected_vehicle_id()

        if vehicle_id is not None:
            open_vehicle_form(vehicle_id)

    # Delete vehicle
    def remove_vehicle():
        """Deletes the selected vehicle."""

        vehicle_id = get_selected_vehicle_id()

        if vehicle_id is None:
            return

        if vehicle_has_reservations(vehicle_id):
            messagebox.showerror("Error", "Cannot delete a vehicle with reservations.")
            return

        if not messagebox.askyesno(
            "Confirm Delete", "Are you sure you want to delete this vehicle?"
        ):
            return

        try:
            affected_rows = delete_vehicle(vehicle_id)

            if affected_rows:
                load_vehicles()

                messagebox.showinfo("Success", "Vehicle deleted successfully.")

        except Exception as error:
            messagebox.showerror("Error", str(error))

    # Export CSV
    def export_csv():
        """Exports all vehicles to a CSV file."""

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile="vehicles.csv",
            filetypes=[("CSV files", "*.csv")],
        )

        if not file_path:
            return

        try:
            with open(file_path, "w", newline="", encoding="utf-8-sig") as file:

                writer = csv.writer(file, delimiter=";")

                writer.writerow(["ID"] + [label for field, label in FIELDS])

                for vehicle in list_vehicles():
                    writer.writerow(
                        [vehicle["id"]] + [vehicle[field] for field, label in FIELDS]
                    )

            messagebox.showinfo("Success", "Vehicles exported successfully.")

        except Exception as error:
            messagebox.showerror("Error", str(error))

    # Action buttons
    buttons = [
        ("Add Vehicle", lambda: open_vehicle_form(), GOLD, "#A8873E"),
        ("Edit", edit_vehicle, "#383838", "#4A4A4A"),
        ("Delete", remove_vehicle, "#383838", "#4A4A4A"),
        ("Export CSV", export_csv, "#383838", "#4A4A4A"),
    ]

    for text, command, color, hover_color in buttons:

        ctk.CTkButton(
            buttons_frame,
            text=text,
            width=110 if text != "Add Vehicle" else 130,
            height=38,
            fg_color=color,
            hover_color=hover_color,
            text_color=("#171717" if text == "Add Vehicle" else "#FFFFFF"),
            command=command,
        ).pack(side="left", padx=3)

    # Initial table load

    load_vehicles()
