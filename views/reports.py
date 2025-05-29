import flet as ft
from config.database import get_db_connection

def get_admin_full_name():
    try:
        conn = get_db_connection()
        if conn and conn.is_connected():
            cursor = conn.cursor()
            cursor.execute("SELECT full_name FROM admin LIMIT 1")
            admin = cursor.fetchone()
            cursor.close()
            conn.close()
            return admin[0] if admin else "Admin"
    except Exception as e:
        print(f"Error fetching admin name: {e}")
        return "Admin"

admin_full_name = get_admin_full_name()

def reports_view(page: ft.Page):
    # Fetch logged-in user's name
    def get_logged_in_user():
        try:
            conn = get_db_connection()
            if conn and conn.is_connected():
                cursor = conn.cursor()
                cursor.execute("SELECT first_name, last_name FROM employees WHERE id = %s", (page.session.get("user_id"),))
                user = cursor.fetchone()
                cursor.close()
                conn.close()
                return f"{user[0]} {user[1]}" if user else "User"
        except Exception as e:
            print(f"Error fetching user: {e}")
            return "User"

    user_name = get_logged_in_user()

    # Header Section
    header = ft.Row(
        controls=[
            ft.Column(
                controls=[
                    ft.Text("Sales Report", size=24, weight="bold", color="#BB6F19"),
                    ft.Text("Monday, 25 March 2025", size=14, color="black"),  # Example date
                ],
                expand=True
            ),
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.CircleAvatar(
                            content=ft.Icon(ft.Icons.PERSON, color="black"),
                            bgcolor="#BB6F19",
                            radius=18
                        ),
                        ft.Column(
                            controls=[
                                ft.Text(user_name, weight="bold", size=16, font_family="Poppins"),
                                ft.Text("Barista", size=12, color="grey", font_family="Poppins")
                            ],
                            spacing=0
                        ),
                        ft.IconButton(
                            icon=ft.Icons.LOGOUT,
                            icon_color="black",
                            tooltip="Logout",
                            on_click=lambda e: handle_logout(page)
                        )
                    ],
                    spacing=10,
                    alignment="center"
                ),
                padding=10,
                border_radius=25,
                bgcolor="white",
                shadow=ft.BoxShadow(blur_radius=4, color=ft.Colors.with_opacity(0.1, "black")),
            )
        ],
        alignment="spaceBetween",
        vertical_alignment="center"
    )

    def handle_logout(page):
        # Show confirmation dialog
        def confirm_logout(e):
            page.overlay.clear()  # Clear all elements from the overlay
            page.update()  # Update the page to reflect changes
            page.clean()  # Clear all existing UI elements
            from views.login import main
            main(page)  # Redirect to the login window
            page.update()

        def cancel_logout(e):
            page.overlay.clear()  # Clear all elements from the overlay
            page.update()  # Update the page to reflect changes

        logout_dialog = ft.AlertDialog(
            title=ft.Text("Confirm Logout"),
            content=ft.Text("Are you sure you want to logout?"),
            actions=[
                ft.TextButton("Cancel", on_click=cancel_logout),
                ft.TextButton("Logout", on_click=confirm_logout),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.overlay.append(logout_dialog)  # Add the dialog to the overlay
        logout_dialog.open = True
        page.update()

    # Date Range and Filter Section
    date_filter_row = ft.Row(
        controls=[
            ft.Row(
                controls=[
                    ft.ElevatedButton("Today", bgcolor="#BB6F19", color="white"),
                    ft.ElevatedButton("Week", bgcolor="#BB6F19", color="white"),
                    ft.ElevatedButton("Month", bgcolor="#BB6F19", color="white"),
                ],
                spacing=10
            ),
            ft.Row(
                controls=[
                    ft.TextField(
                        hint_text="Start Date",
                        width=150,
                        prefix_icon=ft.Icons.CALENDAR_MONTH,
                        border=ft.InputBorder.OUTLINE,
                        filled=True,
                        bgcolor="white"
                    ),
                    ft.TextField(
                        hint_text="End Date",
                        width=150,
                        prefix_icon=ft.Icons.CALENDAR_MONTH,
                        border=ft.InputBorder.OUTLINE,
                        filled=True,
                        bgcolor="white"
                    ),
                    ft.ElevatedButton(
                        "Apply",
                        style=ft.ButtonStyle(
                            bgcolor="#BB6F19",
                            color="white",
                            padding=ft.padding.symmetric(horizontal=20, vertical=10),
                            shape=ft.RoundedRectangleBorder(radius=8)
                        )
                    )
                ],
                spacing=10
            ),
            ft.Row(
                controls=[
                    ft.ElevatedButton("PDF", bgcolor="#BB6F19", color="white"),
                    ft.ElevatedButton("Excel", bgcolor="#BB6F19", color="white"),
                    ft.ElevatedButton("Print", bgcolor="#BB6F19", color="white"),
                ],
                spacing=10
            )
        ],
        alignment="spaceBetween",
        vertical_alignment="center",
        spacing=20
    )

    # Summary Cards Section
    summary_cards = ft.Row(
        controls=[
            ft.Container(
                width=300,
                height=100,
                bgcolor="white",
                border_radius=10,
                padding=10,
                content=ft.Column(
                    controls=[
                        ft.Text("Total Revenue", size=14, weight="bold", color="#BB6F19"),
                        ft.Text("₱3,865.00", size=20, weight="bold"),
                        ft.Text("+7.75% from last period", size=12, color="green")
                    ],
                    spacing=5
                )
            ),
            ft.Container(
                width=300,
                height=100,
                bgcolor="white",
                border_radius=10,
                padding=10,
                content=ft.Column(
                    controls=[
                        ft.Text("Total Profit", size=14, weight="bold", color="#BB6F19"),
                        ft.Text("₱1,546.00", size=20, weight="bold"),
                        ft.Text("+9.22% from last period", size=12, color="green")
                    ],
                    spacing=5
                )
            ),
            ft.Container(
                width=300,
                height=100,
                bgcolor="white",
                border_radius=10,
                padding=10,
                content=ft.Column(
                    controls=[
                        ft.Text("Total Orders", size=14, weight="bold", color="#BB6F19"),
                        ft.Text("97", size=20, weight="bold"),
                        ft.Text("+20% from last period", size=12, color="green")
                    ],
                    spacing=5
                )
            )
        ],
        spacing=20
    )

    # Graphs Section
    graphs_section = ft.Row(
        controls=[
            ft.Container(
                width=600,
                height=300,
                bgcolor="white",
                border_radius=10,
                padding=10,
                content=ft.Text("Sales Trend Graph Placeholder", size=16, weight="bold", color="grey")
            ),
            ft.Container(
                width=600,
                height=300,
                bgcolor="white",
                border_radius=10,
                padding=10,
                content=ft.Text("Revenue Category Graph Placeholder", size=16, weight="bold", color="grey")
            )
        ],
        spacing=20
    )

    # Additional Graphs Section
    additional_graphs = ft.Row(
        controls=[
            ft.Container(
                width=600,
                height=300,
                bgcolor="white",
                border_radius=10,
                padding=10,
                content=ft.Text("Sales by Hour of the Day Graph Placeholder", size=16, weight="bold", color="grey")
            ),
            ft.Container(
                width=600,
                height=300,
                bgcolor="white",
                border_radius=10,
                padding=10,
                content=ft.Text("Additional Graph Placeholder", size=16, weight="bold", color="grey")
            )
        ],
        spacing=20
    )

    # User Profile Card
    def user_profile_card():
        def handle_logout(page):
            # Create a custom modal dialog for logout confirmation
            logout_modal = ft.Container(
                visible=False,
                alignment=ft.alignment.center,
                bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.BLACK),
                expand=True,
                content=ft.Container(
                    width=400,
                    height=150,
                    bgcolor=ft.Colors.WHITE,
                    border_radius=15,
                    padding=ft.padding.all(20),
                    alignment=ft.alignment.center,
                    content=ft.Column(
                        spacing=20,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Text("Confirm Logout", size=18, weight="bold"),
                            ft.Text("Are you sure you want to logout?", size=14, color=ft.Colors.GREY),
                            ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,  # Center the buttons
                                spacing=10,
                                controls=[
                                    ft.ElevatedButton(
                                        "Cancel",
                                        style=ft.ButtonStyle(
                                            bgcolor=ft.Colors.GREY,
                                            color=ft.Colors.WHITE,
                                            padding=ft.padding.symmetric(horizontal=20, vertical=10),
                                            shape=ft.RoundedRectangleBorder(radius=8),
                                        ),
                                        on_click=lambda e: close_logout_modal(),
                                    ),
                                    ft.ElevatedButton(
                                        "Logout",
                                        style=ft.ButtonStyle(
                                            bgcolor=ft.Colors.RED,
                                            color=ft.Colors.WHITE,
                                            padding=ft.padding.symmetric(horizontal=20, vertical=10),
                                            shape=ft.RoundedRectangleBorder(radius=8),
                                        ),
                                        on_click=lambda e: confirm_logout(),
                                    ),
                                ],
                            ),
                        ],
                    ),
                ),
            )

            # Add the modal to the page overlay
            page.overlay.append(logout_modal)

            def confirm_logout():
                logout_modal.visible = False  # Hide the modal
                page.overlay.remove(logout_modal)  # Remove the modal from the overlay
                page.update()  # Update the page to reflect changes
                page.clean()  # Clear all existing UI elements
                page.bgcolor = "white"  # Reset the background color to white
                from views.login import main
                main(page)  # Redirect to the login window
                page.update()

            def close_logout_modal():
                logout_modal.visible = False  # Hide the modal
                page.overlay.remove(logout_modal)  # Remove the modal from the overlay
                page.update()  # Update the page to reflect changes

            # Show the modal
            logout_modal.visible = True
            page.update()

        return ft.Container(
            content=ft.Row([
                ft.CircleAvatar(
                    content=ft.Icon(ft.Icons.PERSON, color=ft.Colors.BLACK),
                    bgcolor="#BB6F19",
                    radius=18
                ),
                ft.Column([
                    ft.Text(admin_full_name, weight="bold", size=16, font_family="Poppins"),
                    ft.Text("Barista", size=12, color=ft.Colors.GREY, font_family="Poppins")
                ], spacing=0),
                ft.IconButton(
                    icon=ft.Icons.LOGOUT,
                    icon_color="black",
                    tooltip="Logout",
                    on_click=lambda e: handle_logout(page)
                )
            ], alignment="center", spacing=10),
            padding=10,
            border_radius=25,
            bgcolor=ft.Colors.WHITE,
            shadow=ft.BoxShadow(blur_radius=4, color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK)),
        )

    # Main layout
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Column(
                            controls=[
                                ft.Text("Sales Report", size=24, weight="bold", color="#BB6F19"),
                                ft.Text("Monday, 25 March 2025", size=14, color="black"),
                            ],
                            expand=True
                        ),
                        user_profile_card()
                    ],
                    alignment="spaceBetween",
                    vertical_alignment="center"
                ),
                ft.Divider(height=2, thickness=1, color="#BB6F19"),
                date_filter_row,
                summary_cards,
                graphs_section,
                additional_graphs
            ],
            spacing=20
        ),
        padding=20,
        expand=True
    )