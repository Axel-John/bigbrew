import flet as ft

def users_view(page: ft.Page):
    # Header Section
    header = ft.Row(
        controls=[
            ft.Column(
                controls=[
                    ft.Text("Manage Users", size=24, weight="bold", color="#BB6F19"),
                    ft.Text("Add and manage employees", size=14, color="black"),
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
                                ft.Text("Admin", weight="bold", size=16, font_family="Poppins"),
                                ft.Text("Administrator", size=12, color="grey", font_family="Poppins")
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
            page.clean()
            from views.login import main
            main(page)
            page.update()

        page.dialog = ft.AlertDialog(
            title=ft.Text("Confirm Logout"),
            content=ft.Text("Are you sure you want to logout?"),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: setattr(page.dialog, "open", False)),
                ft.TextButton("Logout", on_click=confirm_logout),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.dialog.open = True
        page.update()

    # Main Layout
    return ft.Container(
        content=ft.Column(
            controls=[
                header,
                ft.Divider(height=2, thickness=1, color="#BB6F19"),
            ],
            spacing=20
        ),
        padding=20,
        expand=True
    )
