import flet as ft
from config.database import get_db_connection, get_employee_full_name

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
        # Create a custom modal dialog for logout confirmation (standardized)
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
                            alignment=ft.MainAxisAlignment.CENTER,
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
        page.overlay.append(logout_modal)

        def confirm_logout():
            logout_modal.visible = False
            page.overlay.remove(logout_modal)
            page.update()
            page.clean()
            page.bgcolor = "white"
            from views.login import main
            main(page)
            page.update()

        def close_logout_modal():
            logout_modal.visible = False
            page.overlay.remove(logout_modal)
            page.update()

        logout_modal.visible = True
        page.update()

    # --- FILTER CONTROLS ---
    filter_toggle_row = ft.Row(
        controls=[
            ft.ElevatedButton("Today", style=ft.ButtonStyle(bgcolor="#BB6F19", color="white", shape=ft.RoundedRectangleBorder(radius=8)), disabled=True),
            ft.ElevatedButton("Week", style=ft.ButtonStyle(bgcolor="#F5E9DA", color="#BB6F19", shape=ft.RoundedRectangleBorder(radius=8))),
            ft.ElevatedButton("Month", style=ft.ButtonStyle(bgcolor="#F5E9DA", color="#BB6F19", shape=ft.RoundedRectangleBorder(radius=8))),
        ],
        spacing=10,
        alignment="start",
    )
    filter_date_row = ft.Row(
        controls=[
            ft.TextField(label="From", value="25/03/2025", width=140, prefix_icon=ft.Icons.CALENDAR_MONTH, border=ft.InputBorder.OUTLINE, filled=True, bgcolor="white"),
            ft.TextField(label="To", value="25/03/2025", width=140, prefix_icon=ft.Icons.CALENDAR_MONTH, border=ft.InputBorder.OUTLINE, filled=True, bgcolor="white"),
            ft.ElevatedButton("Apply", style=ft.ButtonStyle(bgcolor="#BB6F19", color="white", shape=ft.RoundedRectangleBorder(radius=8))),
        ],
        spacing=10,
        alignment="start",
    )
    filter_controls = ft.Column([
        filter_toggle_row,
        ft.Container(filter_date_row, margin=ft.margin.only(top=10)),
    ], spacing=8)

    # --- METRIC CARDS ---
    def metric_card(title, value, subtext, icon, icon_color, subtext_color):
        return ft.Container(
            bgcolor="white",
            border_radius=16,
            shadow=ft.BoxShadow(blur_radius=6, color=ft.Colors.with_opacity(0.10, ft.Colors.BLACK)),
            padding=16,
            margin=ft.margin.only(bottom=18),
            content=ft.Column([
                ft.Row([
                    ft.Text(title, size=15, weight="bold", color="#BB6F19"),
                    ft.Icon(icon, color=icon_color, size=22),
                ], alignment="spaceBetween"),
                ft.Container(
                    content=ft.Text(value, size=26, weight="bold", color="#222", font_family="Poppins"),
                    margin=ft.margin.only(top=8, bottom=2),
                ),
                ft.Row([
                    ft.Icon(ft.Icons.ARROW_UPWARD, color=subtext_color, size=16),
                    ft.Text(subtext, size=13, color=subtext_color, weight="bold"),
                ], spacing=4),
            ], spacing=4),
            width=260,
        )
    metrics_column = ft.Column([
        metric_card("Total Revenue", "₱3,865.00", "57.76% from last period", ft.Icons.CHECK_CIRCLE, "#22C55E", "#22C55E"),
        metric_card("Total Profit", "₱1,546.00", "2.2% from last period", ft.Icons.TRENDING_UP, "#3B82F6", "#3B82F6"),
        metric_card("Total Order", "97", "20% from last period", ft.Icons.SHOPPING_BAG, "#F59E42", "#F59E42"),
    ], spacing=0)

    # --- EXPORT BUTTONS ---
    export_buttons = ft.Row([
        ft.OutlinedButton("PDF", style=ft.ButtonStyle(color="#BB6F19", side=ft.border.all(1, "#BB6F19"), shape=ft.RoundedRectangleBorder(radius=8))),
        ft.OutlinedButton("Excel", style=ft.ButtonStyle(color="#BB6F19", side=ft.border.all(1, "#BB6F19"), shape=ft.RoundedRectangleBorder(radius=8))),
        ft.OutlinedButton("Print", style=ft.ButtonStyle(color="#BB6F19", side=ft.border.all(1, "#BB6F19"), shape=ft.RoundedRectangleBorder(radius=8))),
    ], spacing=12, alignment="end")

    # --- CHARTS (PLACEHOLDERS) ---
    sales_trend_chart = ft.Container(
        bgcolor="white",
        border_radius=16,
        padding=20,
        margin=ft.margin.only(bottom=18),
        content=ft.Text("Sales Trend Line Chart", size=18, color="#BB6F19", weight="bold", text_align="center"),
        height=260,
        expand=True,
    )
    bar_chart = ft.Container(
        bgcolor="white",
        border_radius=16,
        padding=20,
        content=ft.Text("Sales by Hour of the Day (Bar Chart)", size=16, color="#BB6F19", text_align="center"),
        height=180,
        expand=True,
    )
    donut_chart = ft.Container(
        bgcolor="white",
        border_radius=16,
        padding=20,
        content=ft.Text("Revenue Category (Donut Chart)", size=16, color="#BB6F19", text_align="center"),
        height=180,
        width=260,
    )
    charts_row = ft.Row([
        bar_chart,
        donut_chart
    ], spacing=18, alignment="start")
    right_charts_column = ft.Column([
        export_buttons,
        sales_trend_chart,
        charts_row
    ], spacing=0, expand=True)

    # --- MAIN CONTENT LAYOUT ---
    main_content = ft.Row([
        ft.Column([
            filter_controls,
            metrics_column
        ], spacing=24, expand=1),
        ft.Container(right_charts_column, expand=2, margin=ft.margin.only(left=28)),
    ], spacing=24, expand=True)

    # User Profile Card
    def user_profile_card():
        user_id = page.session.get("user_id")
        full_name = get_employee_full_name(user_id)
        if not full_name or full_name.lower() == 'none':
            try:
                conn = get_db_connection()
                if conn and conn.is_connected():
                    cursor = conn.cursor()
                    cursor.execute("SELECT full_name FROM admin WHERE id = %s", (user_id,))
                    row = cursor.fetchone()
                    cursor.close()
                    conn.close()
                    if row and row[0]:
                        full_name = row[0]
                    else:
                        full_name = "Admin"
            except Exception:
                full_name = "Admin"
        return ft.Container(
            content=ft.Row([
                ft.CircleAvatar(
                    content=ft.Icon(ft.Icons.PERSON, color=ft.Colors.BLACK),
                    bgcolor="#BB6F19",
                    radius=18
                ),
                ft.Column([
                    ft.Text(full_name, weight="bold", size=16, font_family="Poppins"),
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

    # --- PAGE RETURN ---
    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Column([
                    ft.Text("Sales Report", size=24, weight="bold", color="#BB6F19"),
                    ft.Text("Monday, 25 March 2025", size=14, color="black"),
                ], expand=True),
                user_profile_card()
            ], alignment="spaceBetween", vertical_alignment="center"),
            ft.Divider(height=2, thickness=1, color="#BB6F19"),
            ft.Container(main_content, padding=20, expand=True)
        ], spacing=20),
        padding=20,
        expand=True
    )