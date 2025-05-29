import flet as ft
from flet import (
    Page, Row, Column, Container, Text, TextField, IconButton, Icons, Icon, alignment, padding, Colors, Stack, CircleAvatar, BoxShadow
)
from config.database import get_db_connection

selected_index = 0

def main(page: Page):
    global selected_index
    page.title = "ORDER WINDOW"
    page.bgcolor = "#EDEDED"
    page.window_width = 1200
    page.window_height = 900

    # Hardcoded categories and their images
    def fetch_category_counts():
        try:
            conn = get_db_connection()
            if conn and conn.is_connected():
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT type, COUNT(*) 
                    FROM products 
                    GROUP BY type
                """)
                counts = cursor.fetchall()
                cursor.close()
                conn.close()
                return {row[0]: row[1] for row in counts}
            else:
                print("Error: Unable to connect to the database.")
                return {}
        except Exception as e:
            print(f"Error fetching category counts: {str(e)}")
            return {}

    def fetch_review_order_count():
        try:
            conn = get_db_connection()
            if conn and conn.is_connected():
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM orders 
                    WHERE status = 'Pending'
                """)
                count = cursor.fetchone()[0]
                cursor.close()
                conn.close()
                return count
            else:
                print("Error: Unable to connect to the database.")
                return 0
        except Exception as e:
            print(f"Error fetching review order count: {str(e)}")
            return 0

    category_counts = fetch_category_counts()

    categories = [
        ("Milk Tea", f"{category_counts.get('Milk Tea', 0)} items", ["assets/menu/milk_tea/okinawa.png"]),
        ("Iced Coffee", f"{category_counts.get('Iced Coffee', 0)} items", ["assets/menu/ice_coffee/kape_brusko.png"]),
        ("Fruit Tea", f"{category_counts.get('Fruit Tea', 0)} items", ["assets/menu/fruit_tea/blueberry.png"]),
        ("Hot Brew", f"{category_counts.get('Hot Brew', 0)} items", ["assets/menu/hot_brew/hot_brew.png"]),
        ("Review Order", f"{fetch_review_order_count()} items", []),
    ]

    category_row_ref = ft.Ref[ft.Row]()

    # Reference for the white container
    white_container_ref = ft.Ref[ft.Container]()

    def select_category(idx):
        global selected_index
        selected_index = idx
        category_row_ref.current.controls.clear()
        category_row_ref.current.controls.extend(build_category_row())
        category_row_ref.current.update()
        # Update content in the white container based on the selected category
        if selected_index == len(categories) - 1:  # "Review Order" category
            white_container_ref.current.content = build_review_order_container()
        else:
            product_grid.controls.clear()
            product_grid.controls.extend(build_grid_items())
            white_container_ref.current.content = product_grid
        white_container_ref.current.update()
        page.update()

    def build_category_row():
        rows = []
        for i, (name, items, img) in enumerate(categories):
            rows.append(
                Container(
                    content=Stack([
                        # For Review Order, show the icon and dynamic count
                        *( [
                            Container(
                                content=Icon(name="add_circle", size=60, color="#BB6F19"),
                                alignment=alignment.center_right
                            ),
                            Container(
                                content=Column([
                                    Text(name, size=20, weight="bold", color="white" if selected_index == i else "black"),
                                    Text(items, size=12, color="white" if selected_index == i else "#7B6B63")
                                ], alignment="start", spacing=0),
                                alignment=alignment.bottom_left,
                                left=0, bottom=15
                            )
                        ] if name == "Review Order" else [
                            # Available at the top
                            Container(
                                content=Text("Available", size=10, color="white" if selected_index == i else "black"),
                                bgcolor="#BB6F19" if selected_index == i else "#E0E0E0",
                                border_radius=10,
                                padding=padding.symmetric(horizontal=20, vertical=2),
                                alignment=alignment.top_left,
                                left=0, top=0
                            ),
                            # Image at center, slightly lower
                            Container(
                                content=ft.Image(
                                    src=img[0] if img else "",
                                    width=100,
                                    height=100,
                                    fit=ft.ImageFit.CONTAIN,
                                    error_content=Icon(name="image_not_supported", color="red", size=40)
                                ),
                                alignment=alignment.center,
                                right=0,
                                bottom=0
                            ),
                            # Name and items at the bottom left
                            Container(
                                content=Column([
                                    Text(name, size=20, weight="bold", color="white" if selected_index == i else "black"),
                                    Text(items, size=12, color="white" if selected_index == i else "#7B6B63")
                                ], alignment="start", spacing=0),
                                alignment=alignment.bottom_left,
                                left=0, bottom=0
                            )
                        ] ),
                    ], expand=True),
                    bgcolor="#A9A9A9" if selected_index == i else "white",
                    border_radius=20,
                    padding=padding.all(10),
                    border=ft.border.all(3, "black") if selected_index == i else None,
                    height=150,
                    margin=padding.only(right=10),
                    expand=True,
                    on_click=lambda e, idx=i: select_category(idx)
                )
            )
        return rows

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

    # Top bar: Coffee Menu, Search, Navigation, User
    top_bar = Row([
        Row([
            ft.Image(src="assets/images/bigbrew_logo_black.png", width=80, height=80),
            Text("Coffee Menu", size=28, weight="bold", color="black"),
            Container(width=30),
            TextField(
                hint_text="Search menu",
                width=500,
                height=40,
                border_radius=20,
                prefix_icon="search",
                bgcolor="#F7F7F7",
                border_color="#E0E0E0"
            ),
        ], spacing=10),
        Container(
            content=Row([
                CircleAvatar(
                    content=Icon(Icons.PERSON, color=Colors.BLACK),
                    bgcolor="#BB6F19",
                    radius=18
                ),
                Column([
                    Text(user_name, weight="bold", size=16, font_family="Poppins"),
                    Text("Barista", size=12, color=Colors.GREY, font_family="Poppins")
                ], spacing=0),
                IconButton(
                    icon=Icons.LOGOUT,
                    icon_color="black",
                    tooltip="Logout",
                    on_click=lambda e: handle_logout(page)
                )
            ], alignment="center", spacing=10),
            padding=10,
            border_radius=25,
            bgcolor=Colors.WHITE,
            shadow=BoxShadow(blur_radius=4, color=Colors.with_opacity(0.1, Colors.BLACK)),
        )
    ], alignment="spaceBetween", vertical_alignment="center", expand=True)

    # Category bar
    category_row = Row(ref=category_row_ref, controls=build_category_row(), alignment="start", vertical_alignment="center", expand=True)

    # Fetch products from the database
    def fetch_products():
        try:
            conn = get_db_connection()
            if conn and conn.is_connected():
                cursor = conn.cursor()
                cursor.execute("SELECT name, image_path, type, price FROM products ORDER BY product_id")  # Include price column
                products = cursor.fetchall()
                cursor.close()
                conn.close()
                return products
            else:
                print("Error: Unable to connect to the database.")
                return []
        except Exception as e:
            print(f"Error fetching products: {str(e)}")
            return []

    def product_card(image_path, name, price):
        return Container(
            width=380,
            height=220,
            bgcolor="#FAD7A0",
            border_radius=20,
            padding=5,
            content=ft.Column(
                controls=[
                    # Product image centered at the top
                    ft.Container(
                        content=ft.Image(
                            src=image_path if image_path else "assets/images/placeholder.png",
                            width=90,
                            height=120,
                            fit=ft.ImageFit.CONTAIN,
                            error_content=ft.Icon(name="image_not_supported", color="red", size=40)
                        ),
                        alignment=ft.alignment.top_center,
                        expand=False,
                    ),
                    ft.Row(
                        controls=[
                            ft.Text(name, weight="bold", size=18, color="black", font_family="Poppins"),
                            ft.Container(
                                content=ft.Icon(ft.Icons.ADD, color="white", size=40),
                                bgcolor="black",
                                width=56,
                                height=56,
                                border_radius=20,
                                alignment=ft.alignment.center,
                                on_click=lambda e: show_add_to_order_dialog(name, price, image_path),  # Pass image_path
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.END,
                        expand=True,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                expand=True,
            ),
        )

    # Function to build grid items based on selected category
    def build_grid_items():
        selected_category = categories[selected_index][0] if selected_index < len(categories) else None
        db_products = fetch_products()
        filtered_products = []
        for p in db_products:
            if selected_category and p[2] and p[2].strip().lower() == selected_category.strip().lower():
                filtered_products.append(p)
        if filtered_products:
            return [
                product_card(
                    product[1] if product[1] else 'assets/images/placeholder.png',  # Image path
                    product[0],  # Product name
                    product[3]   # Product price
                )
                for product in filtered_products
            ]
        else:
            return [
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.INFO, color="#BB6F19", size=48),
                        ft.Text("No product available", size=20, weight="bold", color="black", font_family="Poppins")
                    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    alignment=ft.alignment.center,
                    bgcolor="#FAD7A0",
                    border_radius=20,
                    width=380,
                    height=220,
                    expand=True
                )
            ]

    # Initial grid items
    grid_items = build_grid_items()

    # Scrollable grid with 4 columns
    product_grid = ft.GridView(
        controls=grid_items,
        max_extent=380,  # Match card width
        child_aspect_ratio=1.727,  # width/height ratio (380/220 = 1.727) for landscape cards
        spacing=40,
        run_spacing=50,
        expand=True,
        height=420,
    )

    # White container below category boxes (contains only the product grid)
    white_container = Container(
        ref=white_container_ref,
        content=product_grid,
        bgcolor=Colors.WHITE,
        border_radius=20,
        padding=padding.all(30),  # Increased padding
        margin=padding.only(top=20, bottom=20, left=30, right=30),
        width=1700,
        height=500,  # Increased height to accommodate larger cards and spacing
    )

    # Function to build the review order container
    def build_review_order_container():
        return ft.Row(
            controls=[
                # Order Cart Section
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("Order Cart", size=20, weight="bold", color="black"),
                            ft.Divider(height=1, thickness=1, color="black"),
                            ft.Row(
                                controls=[
                                    ft.Text("Order Details", size=14, weight="bold", color="black", width=250),
                                    ft.Text("Sizes", size=14, weight="bold", color="black", width=100),
                                    ft.Text("Add-ons", size=14, weight="bold", color="black", width=200),
                                    ft.Text("Quantity", size=14, weight="bold", color="black", width=150),
                                    ft.Text("Price", size=14, weight="bold", color="black", width=100),
                                    ft.Text("Total", size=14, weight="bold", color="black", width=100),
                                ],
                                alignment="spaceBetween",
                                spacing=20,
                            ),
                            ft.Row(
                                controls=[
                                    ft.Image(
                                        src="assets/menu/milk_tea/okinawa.png",
                                        width=50,
                                        height=50,
                                        fit=ft.ImageFit.CONTAIN,
                                    ),
                                    ft.Column(
                                        controls=[
                                            ft.Text("Milk Tea Okinawa", size=14, color="black"),
                                            ft.Text("Remove", size=12, color="red"),
                                        ],
                                        spacing=2,
                                    ),
                                    ft.Text("Grande", size=14, color="black"),
                                    ft.Text("Pearl, Cream Cheese", size=14, color="black"),
                                    ft.Row(
                                        controls=[
                                            ft.IconButton(icon=ft.Icons.REMOVE, icon_color="black"),
                                            ft.Text("1", size=14, color="black"),
                                            ft.IconButton(icon=ft.Icons.ADD, icon_color="black"),
                                        ],
                                        spacing=5,
                                    ),
                                    ft.Text("₱45", size=14, color="black"),
                                    ft.Text("₱45", size=14, color="black"),
                                ],
                                alignment="spaceBetween",
                                spacing=20,
                            ),
                        ],
                        spacing=10,
                    ),
                    width=1100,  # Updated width
                    height=500,  # Updated height
                    bgcolor="white",
                    border_radius=20,
                    padding=ft.padding.all(20),
                    shadow=ft.BoxShadow(blur_radius=4, color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK)),
                ),
                # Order Summary Section
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("Order Summary", size=20, weight="bold", color="black"),
                            ft.Divider(height=1, thickness=1, color="black"),
                            ft.Row(
                                controls=[
                                    ft.Text("Total Items", size=14, color="black"),
                                    ft.Text("1", size=14, color="black"),
                                ],
                                alignment="spaceBetween",
                            ),
                            ft.Row(
                                controls=[
                                    ft.Text("Subtotal", size=14, color="black"),
                                    ft.Text("₱45", size=14, color="black"),
                                ],
                                alignment="spaceBetween",
                            ),
                            ft.Row(
                                controls=[
                                    ft.Text("Add-ons", size=14, color="black"),
                                    ft.Text("₱18", size=14, color="black"),
                                ],
                                alignment="spaceBetween",
                            ),
                            ft.Divider(height=1, thickness=1, color="black"),
                            ft.Row(
                                controls=[
                                    ft.Text("Grand Total", size=16, weight="bold", color="black"),
                                    ft.Text("₱63", size=16, weight="bold", color="black"),
                                ],
                                alignment="spaceBetween",
                            ),
                            ft.Text("Payment Method", size=14, color="black"),
                            ft.Row(
                                controls=[
                                    ft.ElevatedButton(
                                        "Cash",
                                        style=ft.ButtonStyle(
                                            bgcolor="#FAD7A0",
                                            color="black",
                                            padding=ft.padding.symmetric(horizontal=20, vertical=10),
                                        ),
                                    ),
                                    ft.ElevatedButton(
                                        "GCash",
                                        style=ft.ButtonStyle(
                                            bgcolor="#FAD7A0",
                                            color="black",
                                            padding=ft.padding.symmetric(horizontal=20, vertical=10),
                                        ),
                                    ),
                                ],
                                spacing=10,
                            ),
                            ft.Text("Estimated Prep Time", size=14, color="black"),
                            ft.Text("5-7 mins", size=14, color="black"),
                            ft.ElevatedButton(
                                "Confirm Order",
                                style=ft.ButtonStyle(
                                    bgcolor="black",
                                    color="white",
                                    padding=ft.padding.symmetric(horizontal=20, vertical=10),
                                ),
                            ),
                            ft.ElevatedButton(
                                "Modify",
                                style=ft.ButtonStyle(
                                    bgcolor="#E0E0E0",
                                    color="black",
                                    padding=ft.padding.symmetric(horizontal=20, vertical=10),
                                ),
                            ),
                        ],
                        spacing=10,
                    ),
                    width=300,  # Updated width
                    height=500,  # Updated height
                    bgcolor="#FAD7A0",
                    border_radius=20,
                    padding=ft.padding.all(20),
                    shadow=ft.BoxShadow(blur_radius=4, color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK)),
                ),
            ],
            alignment="spaceBetween",
            spacing=20,
        )

    # Dialog for adding items to order
    def show_add_to_order_dialog(product_name, medio_price, product_image):
        grande_price = medio_price + 10  # Calculate Grande price by adding 10 to Medio price
        selected_add_ons = []  # Track selected add-ons

        # Define add_ons_sum to display the total cost of selected add-ons
        add_ons_sum = ft.Text("Total Add-ons: ₱0.00", size=14, color="black")

        def toggle_add_on(add_on):
            if add_on in selected_add_ons:
                selected_add_ons.remove(add_on)
            else:
                selected_add_ons.append(add_on)
            update_add_ons_sum()

        def update_add_ons_sum():
            add_ons_sum.value = f"Total Add-ons: ₱{len(selected_add_ons) * 9:.2f}"
            add_ons_sum.update()

        def update_quantity(change):
            nonlocal quantity
            quantity = max(1, quantity + change)  # Ensure quantity is at least 1
            quantity_text.value = str(quantity)
            quantity_text.update()

        quantity = 1  # Initialize quantity
        quantity_text = ft.Text(str(quantity), size=14, color="black")

        # Create the dialog container
        add_to_order_dialog = ft.Container(
            visible=True,
            alignment=ft.alignment.center,
            bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.BLACK),
            expand=True,
            content=ft.Container(
                width=500,
                height=600,
                bgcolor=ft.Colors.WHITE,
                border_radius=15,
                padding=ft.padding.all(20),
                shadow=ft.BoxShadow(
                    blur_radius=10,
                    spread_radius=1,
                    color=ft.Colors.with_opacity(0.2, ft.Colors.BLACK),
                    offset=ft.Offset(0, 4),
                ),
                content=ft.Column(
                    spacing=20,
                    controls=[
                        # Header Section
                        ft.Row(
                            controls=[
                                ft.Text(product_name, size=24, weight="bold", color="black"),
                                ft.IconButton(
                                    icon=ft.Icons.CLOSE,
                                    icon_color="black",
                                    on_click=lambda e: close_add_to_order_dialog(),
                                ),
                            ],
                            alignment="spaceBetween",
                        ),
                        ft.Divider(height=1, thickness=1, color="black"),
                        # Product Image
                        ft.Container(
                            content=ft.Image(
                                src=product_image,
                                width=130,
                                height=130,
                                fit=ft.ImageFit.CONTAIN,
                                border_radius=8,
                            ),
                            alignment=ft.alignment.center,
                        ),
                        # Size Options
                        ft.Row(
                            controls=[
                                ft.Column(
                                    controls=[
                                        ft.Text("Medio", size=16, weight="bold", color="black"),
                                        ft.Text(f"₱{medio_price:.2f}", size=14, color="black"),
                                    ],
                                    alignment="center",
                                ),
                                ft.Column(
                                    controls=[
                                        ft.Text("Grande", size=16, weight="bold", color="black"),
                                        ft.Text(f"₱{grande_price:.2f}", size=14, color="black"),
                                    ],
                                    alignment="center",
                                ),
                            ],
                            alignment="spaceAround",
                        ),
                        # Quantity Section
                        ft.Row(
                            controls=[
                                ft.Text("Quantity:", size=14, color="black"),
                                ft.Container(
                                    content=ft.Row(
                                        controls=[
                                            ft.IconButton(
                                                icon=ft.Icons.REMOVE,
                                                icon_color="black",
                                                on_click=lambda e: update_quantity(-1),
                                            ),
                                            quantity_text,
                                            ft.IconButton(
                                                icon=ft.Icons.ADD,
                                                icon_color="black",
                                                on_click=lambda e: update_quantity(1),
                                            ),
                                        ],
                                        spacing=5,
                                    ),
                                    bgcolor="#FAD7A0",
                                    border_radius=8,
                                    padding=ft.padding.symmetric(horizontal=10, vertical=5),
                                ),
                            ],
                            alignment="start",
                            spacing=10,
                        ),
                        # Add-ons Section
                        ft.Column(
                            controls=[
                                ft.Text("Add-ons:", size=14, weight="bold", color="black"),
                                ft.Row(
                                    controls=[
                                        ft.ElevatedButton(
                                            "Pearl",
                                            style=ft.ButtonStyle(
                                                bgcolor="#BB6F19",
                                                color="white",
                                                padding=ft.padding.symmetric(horizontal=10, vertical=5),
                                                shape=ft.RoundedRectangleBorder(radius=8),
                                            ),
                                            on_click=lambda e: toggle_add_on("Pearl"),
                                        ),
                                        ft.ElevatedButton(
                                            "Crystal",
                                            style=ft.ButtonStyle(
                                                bgcolor="#BB6F19",
                                                color="white",
                                                padding=ft.padding.symmetric(horizontal=10, vertical=5),
                                                shape=ft.RoundedRectangleBorder(radius=8),
                                            ),
                                            on_click=lambda e: toggle_add_on("Crystal"),
                                        ),
                                    ],
                                    spacing=10,
                                    wrap=True,
                                ),
                                add_ons_sum,
                            ],
                            spacing=10,
                        ),
                        # Action Buttons
                        ft.Row(
                            controls=[
                                ft.ElevatedButton(
                                    "Cancel",
                                    style=ft.ButtonStyle(
                                        bgcolor="#E0E0E0",
                                        color="black",
                                        padding=ft.padding.symmetric(horizontal=20, vertical=10),
                                        shape=ft.RoundedRectangleBorder(radius=8),
                                    ),
                                    on_click=lambda e: close_add_to_order_dialog(),
                                ),
                                ft.ElevatedButton(
                                    "Add to Order",
                                    style=ft.ButtonStyle(
                                        bgcolor="#BB6F19",
                                        color="white",
                                        padding=ft.padding.symmetric(horizontal=20, vertical=10),
                                        shape=ft.RoundedRectangleBorder(radius=8),
                                    ),
                                    on_click=lambda e: add_to_order(),
                                ),
                            ],
                            alignment="end",
                            spacing=10,
                        ),
                    ],
                ),
            ),
        )

        # Add the dialog to the page overlay
        page.overlay.append(add_to_order_dialog)
        page.update()

    def close_add_to_order_dialog():
        # Remove the dialog from the overlay
        for overlay in page.overlay:
            if isinstance(overlay, ft.Container) and overlay.visible:
                page.overlay.remove(overlay)
                break
        page.update()

    def update_quantity(change):
        # Update the quantity text
        quantity_text = page.get_control("quantity_text")
        if quantity_text:
            current_quantity = int(quantity_text.value)
            new_quantity = max(1, current_quantity + change)
            quantity_text.value = str(new_quantity)
            quantity_text.update()

    def add_to_order():
        # Logic to add the product to the order
        print("Product added to order")
        close_add_to_order_dialog()

    # Main layout
    page.add(
        Column([
            Container(
                content=Column([
                    Container(content=top_bar, padding=padding.symmetric(vertical=20, horizontal=30)),
                    Container(content=category_row, padding=padding.symmetric(horizontal=30, vertical=10)),
                    white_container,
                ], spacing=0, expand=True),
                expand=True,
                bgcolor="#EDEDED"
            ),
            # Add the review order container here conditionally
            Container(
                content=build_review_order_container(),
                alignment=alignment.center,
                padding=padding.all(20),
                visible=selected_index == len(categories) - 1,  # Only show for "Review Order" category
                expand=True,
            ),
        ], expand=True)
    )