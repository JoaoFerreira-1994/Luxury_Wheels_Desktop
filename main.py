
import customtkinter as ctk
from models import authenticate_user
from PIL import Image
from pathlib import Path

from vehicles_page import show_vehicles_page
from clients_page import show_clients_page
from reservations_page import show_reservations_page
from payment_methods_page import show_payment_methods_page

from models import (
    list_reservations,
    get_monthly_reservations_summary,
    get_rented_vehicles,
    get_latest_clients,
    get_available_vehicles_by_category,
    get_upcoming_revisions,
    get_upcoming_inspections,
    get_revision_alerts
)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def clear_window():
    """Removes all widgets from the main window."""

    for widget in app.winfo_children():
        widget.destroy()


def login():
    """Authenticates the user."""

    email = email_entry.get().strip()
    password = password_entry.get()

    user = authenticate_user(email, password)

    if user:
        show_dashboard(user)
    else:
        error_label.configure(
            text="Invalid email or password."
        )


def show_login():
    """Displays the login screen."""

    global email_entry, password_entry, error_label

    clear_window()

    login_frame = ctk.CTkFrame(
        app,
        width=400,
        height=420
    )
    login_frame.pack(expand=True)
    login_frame.pack_propagate(False)

    title_label = ctk.CTkLabel(
        login_frame,
        text="Luxury Wheels",
        font=ctk.CTkFont(size=30, weight="bold")
    )
    title_label.pack(pady=(40, 10))

    subtitle_label = ctk.CTkLabel(
        login_frame,
        text="Car Rental Management System",
        font=ctk.CTkFont(size=14)
    )
    subtitle_label.pack(pady=(0, 30))

    email_entry = ctk.CTkEntry(
        login_frame,
        width=300,
        placeholder_text="Email"
    )
    email_entry.pack(pady=10)

    password_entry = ctk.CTkEntry(
        login_frame,
        width=300,
        placeholder_text="Password",
        show="*"
    )
    password_entry.pack(pady=10)

    login_button = ctk.CTkButton(
        login_frame,
        text="Login",
        width=300,
        command=login
    )
    login_button.pack(pady=20)

    error_label = ctk.CTkLabel(
        login_frame,
        text="",
        text_color="red"
    )
    error_label.pack()


def show_dashboard_content(user):
    """Displays dashboard indicators, tables, and maintenance alerts."""

    summary = get_monthly_reservations_summary()
    rented_vehicles = get_rented_vehicles()
    reservations = list_reservations()
    latest_clients = get_latest_clients()
    available_vehicles = get_available_vehicles_by_category()
    upcoming_revisions = get_upcoming_revisions()
    upcoming_inspections = get_upcoming_inspections()
    revision_alerts = get_revision_alerts()

    gold = "#C9A34E"
    card_color = "#292929"
    heading_color = "#343434"
    muted = "#AFAFAF"

    dashboard = ctk.CTkScrollableFrame(
        content_frame,
        fg_color="transparent",
        corner_radius=0
    )
    dashboard.pack(fill="both", expand=True, padx=25, pady=20)

    ctk.CTkLabel(
        dashboard,
        text="Dashboard",
        font=ctk.CTkFont(size=28, weight="bold")
    ).pack(anchor="w")

    ctk.CTkLabel(
        dashboard,
        text=f"Welcome, {user['name']}!",
        font=ctk.CTkFont(size=13),
        text_color=muted
    ).pack(anchor="w", pady=(3, 18))

    summary_frame = ctk.CTkFrame(dashboard, fg_color="transparent")
    summary_frame.pack(fill="x", pady=(0, 10))
    summary_frame.grid_columnconfigure((0, 1), weight=1, uniform="cards")

    cards = [
        ("Monthly Reservations", str(summary["total_reservations"] or 0)),
        ("Monthly Revenue", f"{float(summary['total_revenue'] or 0):.2f} €")
    ]

    for column, (label, value) in enumerate(cards):
        card = ctk.CTkFrame(
            summary_frame,
            fg_color=card_color,
            corner_radius=10
        )
        card.grid(row=0, column=column, sticky="ew", padx=5, pady=5)

        ctk.CTkLabel(
            card,
            text=label,
            text_color=muted,
            font=ctk.CTkFont(size=13)
        ).pack(pady=(18, 7))

        ctk.CTkLabel(
            card,
            text=value,
            text_color=gold,
            font=ctk.CTkFont(size=28, weight="bold")
        ).pack(pady=(0, 18))

    def add_section(title, columns, rows):
        """Displays a section with a centered header and data grid."""

        ctk.CTkLabel(
            dashboard,
            text=title,
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", pady=(20, 10))

        container = ctk.CTkFrame(
            dashboard,
            fg_color=card_color,
            corner_radius=10
        )
        container.pack(fill="x")

        table = ctk.CTkFrame(container, fg_color="transparent")
        table.pack(fill="x", padx=10, pady=10)

        for column_index, heading in enumerate(columns):
            table.grid_columnconfigure(column_index, weight=1, uniform="table")
            ctk.CTkLabel(
                table,
                text=heading,
                fg_color=heading_color,
                text_color=gold,
                corner_radius=5,
                font=ctk.CTkFont(size=12, weight="bold"),
                anchor="center",
                height=38
            ).grid(
                row=0,
                column=column_index,
                sticky="ew",
                padx=2,
                pady=(0, 5)
            )

        if not rows:
            ctk.CTkLabel(
                table,
                text="No records found.",
                text_color=muted,
                height=40
            ).grid(row=1, column=0, columnspan=len(columns), sticky="ew")
            return

        for row_index, values in enumerate(rows, start=1):
            for column_index, value in enumerate(values):
                ctk.CTkLabel(
                    table,
                    text=str(value) if value is not None else "",
                    font=ctk.CTkFont(size=12),
                    anchor="center",
                    height=34,
                    wraplength=155
                ).grid(
                    row=row_index,
                    column=column_index,
                    sticky="ew",
                    padx=3,
                    pady=2
                )

    add_section(
        "Rented Vehicles",
        ["Vehicle", "Client", "Start", "End", "Remaining Days"],
        [
            (
                vehicle["vehicle"],
                vehicle["client"],
                vehicle["start_date"],
                vehicle["end_date"],
                vehicle["remaining_days"]
            )
            for vehicle in rented_vehicles
        ]
    )

    # All reservations, including future and completed bookings.
    add_section(
        "Reservations",
        ["Client", "Vehicle", "Start", "End", "Total Price", "Status"],
        [
            (
                reservation.get("client_name", reservation.get("client", "")),
                reservation.get("vehicle_name", reservation.get("vehicle", "")),
                reservation.get("start_date", ""),
                reservation.get("end_date", ""),
                f"{float(reservation.get('total_price') or 0):.2f} €",
                str(reservation.get("status") or "").capitalize()
            )
            for reservation in reservations
        ]
    )

    add_section(
        "Latest Clients",
        ["Name", "Email", "Phone", "Registration Date"],
        [
            (
                client["name"],
                client["email"],
                client["phone"],
                client["created_at"]
            )
            for client in latest_clients
        ]
    )

    add_section(
        "Available Vehicles by Category and Type",
        ["Category", "Type", "Available"],
        [
            (
                vehicle["category"],
                vehicle["vehicle_type"],
                vehicle["total"]
            )
            for vehicle in available_vehicles
        ]
    )

    add_section(
        "Upcoming Revisions",
        ["Vehicle", "License Plate", "Next Revision"],
        [
            (
                f"{vehicle['brand']} {vehicle['model']}",
                vehicle["license_plate"],
                vehicle["next_revision_date"]
            )
            for vehicle in upcoming_revisions
        ]
    )

    add_section(
        "Upcoming Inspections",
        ["Vehicle", "License Plate", "Next Inspection"],
        [
            (
                f"{vehicle['brand']} {vehicle['model']}",
                vehicle["license_plate"],
                vehicle["next_inspection_date"]
            )
            for vehicle in upcoming_inspections
        ]
    )

    if revision_alerts:
        ctk.CTkLabel(
            dashboard,
            text="Revision Alerts",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=gold
        ).pack(anchor="w", pady=(22, 10))

        alert_frame = ctk.CTkFrame(
            dashboard,
            fg_color="#393125",
            corner_radius=10
        )
        alert_frame.pack(fill="x", pady=(0, 15))

        for vehicle in revision_alerts:
            ctk.CTkLabel(
                alert_frame,
                text=(
                    f"{vehicle['brand']} {vehicle['model']} "
                    f"({vehicle['license_plate']}) - "
                    f"{vehicle['next_revision_date']}"
                ),
                anchor="w",
                font=ctk.CTkFont(size=12)
            ).pack(fill="x", padx=15, pady=8)



def show_page(page_name, user):
    """Displays the selected page."""

    for widget in content_frame.winfo_children():
        widget.destroy()

    if page_name == "Dashboard":
        show_dashboard_content(user)

    elif page_name == "Vehicles":
        show_vehicles_page(content_frame)

    elif page_name == "Clients":
        show_clients_page(content_frame)

    elif page_name == "Reservations":
        show_reservations_page(content_frame)

    elif page_name == "Payment Methods":
        show_payment_methods_page(content_frame)

    else:
        ctk.CTkLabel(
            content_frame,
            text=page_name,
            font=ctk.CTkFont(size=28, weight="bold")
        ).pack(anchor="w", padx=30, pady=(30, 10))

        ctk.CTkLabel(
            content_frame,
            text=f"{page_name} management",
            font=ctk.CTkFont(size=16)
        ).pack(anchor="w", padx=30)




def show_dashboard(user):
    """Displays the main application layout."""

    global content_frame

    clear_window()

    sidebar = ctk.CTkFrame(
        app,
        width=230,
        corner_radius=0
    )
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    logo_path = Path(__file__).resolve().parent / "images" / "logo.png"

    try:
        with Image.open(logo_path) as image:
            logo_image = image.copy()
        logo_image.thumbnail((180, 100))

        logo = ctk.CTkImage(
            light_image=logo_image,
            dark_image=logo_image,
            size=logo_image.size
        )
        logo_label = ctk.CTkLabel(sidebar, text="", image=logo)
    except (FileNotFoundError, OSError):
        logo_label = ctk.CTkLabel(
            sidebar,
            text="Luxury Wheels",
            font=ctk.CTkFont(size=22, weight="bold")
        )

    logo_label.pack(pady=(25, 30))

    pages = [
        "Dashboard",
        "Vehicles",
        "Clients",
        "Reservations",
        "Payment Methods"
    ]

    for page in pages:

        button = ctk.CTkButton(
            sidebar,
            text=page,
            width=190,
            height=40,
            anchor="w",
            command=lambda p=page: show_page(p, user)
        )
        button.pack(pady=8, padx=20)

    logout_button = ctk.CTkButton(
        sidebar,
        text="Logout",
        width=190,
        height=40,
        fg_color="#A83232",
        hover_color="#842626",
        command=show_login
    )
    logout_button.pack(side="bottom", pady=30)

    content_frame = ctk.CTkFrame(
        app,
        corner_radius=0,
        fg_color="transparent"
    )
    content_frame.pack(
        side="right",
        fill="both",
        expand=True
    )

    show_page("Dashboard", user)


app = ctk.CTk()
app.title("Luxury Wheels")
app.geometry("1100x700")
app.minsize(900, 600)

show_login()

app.mainloop()