import flet as ft
from flet import (
    Page, Row, Column, Container, Text, TextField, IconButton, Icons, Icon, alignment, padding, Colors, Stack, CircleAvatar, BoxShadow
)
from config.database import get_db_connection, insert_order, fetch_pending_orders
from utils.password import hash_password
import datetime

selected_index = 0
selected_payment_method = None  # No default selection

# At the top of main():
cash_btn_ref = ft.Ref[ft.ElevatedButton]()
gcash_btn_ref = ft.Ref[ft.ElevatedButton]()

# At the top-level of main():
void_modal_width = 320
void_modal_height = 180  # You can adjust this value as needed

# Define page globally at the top of the file
page = None  # Placeholder for the Page object, will be set in main()

def main(page_obj: Page):
    global page
    page = page_obj  # Set the global page object

    global selected_index, selected_payment_method
    selected_index = 0
    page.title = "ORDER WINDOW"
    page.bgcolor = "#EDEDED"
    page.window_width = 1200
    page.window_height = 900

    # Declare variables that will be used in the dialog
    selected_add_ons = []
    selected_size = None
    quantity = 1
    add_ons_sum = None
    subtotal_text = None

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
                    p[1] if p[1] else 'assets/images/placeholder.png',  # Image path
                    p[0],  # Product name
                    p[3]   # Product price
                )
                for p in filtered_products
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
        orders = fetch_pending_orders()
        total_items = sum(order[4] for order in orders)  # quantity
        subtotal = sum(order[5] for order in orders)  # price
        add_ons_total = sum(len(order[3].split(", ")) * 9 if order[3] else 0 for order in orders)
        grand_total = subtotal + add_ons_total

        return ft.Row(
            controls=[
                # Order Cart Section
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Text("Order Cart", size=20, weight="bold", color="black", font_family="Poppins"),
                                    ft.ElevatedButton(
                                        content=ft.Text("Void Order", font_family="Poppins", weight="bold"),
                                        style=ft.ButtonStyle(
                                            bgcolor="#E53935",
                                            color="white",
                                            padding=ft.padding.symmetric(horizontal=18, vertical=8),
                                            shape=ft.RoundedRectangleBorder(radius=8),
                                        ),
                                        on_click=lambda e: open_void_password_modal(),
                                    ),
                                ],
                                alignment="spaceBetween",
                            ),
                            ft.Divider(height=1, thickness=1, color="black"),
                            # Header row with adjusted widths and alignment
                            ft.Row(
                                controls=[
                                    ft.Container(
                                        content=ft.Text("Order Details", size=14, weight="bold", color="black"),
                                        width=300,
                                        alignment=ft.alignment.center_left,
                                    ),
                                    ft.Container(
                                        content=ft.Text("Size", size=14, weight="bold", color="black"),
                                        width=80,
                                        alignment=ft.alignment.center,
                                    ),
                                    ft.Container(
                                        content=ft.Text("Add-ons", size=14, weight="bold", color="black"),
                                        width=150,
                                        alignment=ft.alignment.center,
                                    ),
                                    ft.Container(
                                        content=ft.Text("Quantity", size=14, weight="bold", color="black"),
                                        width=80,
                                        alignment=ft.alignment.center,
                                    ),
                                    ft.Container(
                                        content=ft.Text("Price", size=14, weight="bold", color="black"),
                                        width=100,
                                        alignment=ft.alignment.center,
                                    ),
                                    ft.Container(
                                        content=ft.Text("Total", size=14, weight="bold", color="black"),
                                        width=100,
                                        alignment=ft.alignment.center,
                                    ),
                                ],
                                alignment="spaceBetween",
                                spacing=10,
                            ),
                            *[
                                ft.Column([
                            ft.Row(
                                        controls=[
                                            # Product details with image
                                            ft.Container(
                                                content=ft.Row(
                                controls=[
                                    ft.Image(
                                                            src=order[8] if order[8] else "assets/images/placeholder.png",
                                                            width=40,
                                                            height=40,
                                        fit=ft.ImageFit.CONTAIN,
                                                            error_content=ft.Icon(name="image_not_supported", color="red", size=20),
                                    ),
                                    ft.Column(
                                        controls=[
                                                                ft.Text(
                                                                    order[1],  # product_name
                                                                    size=14,
                                                                    color="black",
                                                                    width=250,
                                                                ),
                                                                ft.Text(
                                                                    order[9],  # product type
                                                                    size=12,
                                                                    color="gray",
                                                                    width=250,
                                                                ),
                                        ],
                                        spacing=2,
                                                            alignment=ft.MainAxisAlignment.CENTER,
                                                        ),
                                        ],
                                        spacing=5,
                                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                                ),
                                                width=300,
                                                alignment=ft.alignment.center_left,
                                            ),
                                            # Size
                                            ft.Container(
                                                content=ft.Text(
                                                    order[2],  # size
                                                    size=14,
                                                    color="black",
                                                ),
                                                width=80,
                                                alignment=ft.alignment.center,
                                            ),
                                            # Add-ons
                                            ft.Container(
                                                content=ft.Text(
                                                    order[3] if order[3] else "None",  # add_ons
                                                    size=14,
                                                    color="black",
                                                ),
                                                width=150,
                                                alignment=ft.alignment.center,
                                            ),
                                            # Quantity
                                            ft.Container(
                                                content=ft.Text(
                                                    str(order[4]),  # quantity
                                                    size=14,
                                                    color="black",
                                                ),
                                                width=80,
                                                alignment=ft.alignment.center,
                                            ),
                                            # Price
                                            ft.Container(
                                                content=ft.Text(
                                                    f"₱{order[5]/order[4]:.2f}",  # price per item
                                                    size=14,
                                                    color="black",
                                                ),
                                                width=100,
                                                alignment=ft.alignment.center,
                                            ),
                                            # Total
                                            ft.Container(
                                                content=ft.Text(
                                                    f"₱{order[5]:.2f}",  # total price
                                                    size=14,
                                                    color="black",
                                                ),
                                                width=100,
                                                alignment=ft.alignment.center,
                                            ),
                                ],
                                alignment="spaceBetween",
                                        spacing=10,
                                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                                    ft.Divider(height=1, thickness=1, color="#B87A2A"),  # Add a divider after each row
                                ]) for order in orders
                            ],
                        ],
                        spacing=10,
                    ),
                    width=1100,
                    height=500,
                    bgcolor="white",
                    border_radius=20,
                    padding=ft.padding.all(20),
                    shadow=ft.BoxShadow(blur_radius=4, color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK)),
                ),
                # Order Summary Section
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("Order Summary", size=22, weight="bold", color="black", font_family="Poppins"),
                            ft.Divider(height=1, thickness=1, color="#7B6B63"),
                            ft.Row([
                                ft.Text("Total Items", size=15, weight="bold", font_family="Poppins"),
                                ft.Text(str(total_items), size=15, weight="bold", font_family="Poppins"),
                            ], alignment="spaceBetween"),
                            ft.Container(
                                content=ft.Row([
                                    ft.Column([
                                        ft.Text("Subtotal", size=15, font_family="Poppins"),
                                        ft.Text("Add-ons", size=15, font_family="Poppins"),
                                    ], spacing=2),
                                    ft.Column([
                                        ft.Text(f"₱{subtotal:.0f}", size=15, font_family="Poppins"),
                                        ft.Text(f"₱{add_ons_total:.0f}", size=15, font_family="Poppins"),
                                    ], spacing=2),
                                ], alignment="spaceBetween"),
                                padding=ft.padding.only(bottom=0, top=0),
                            ),
                            ft.Container(
                                content=ft.Divider(height=1, thickness=1, color="#7B6B63"),
                                padding=ft.padding.symmetric(vertical=2),
                            ),
                            ft.Row([
                                ft.Text("Grand Total", size=17, weight="bold", font_family="Poppins"),
                                ft.Text(f"₱{grand_total:.0f}", size=17, weight="bold", font_family="Poppins"),
                            ], alignment="spaceBetween"),
                            ft.Container(
                                content=ft.Divider(height=1, thickness=1, color="#7B6B63"),
                                padding=ft.padding.symmetric(vertical=2),
                            ),
                            ft.Text("Payment Method", size=15, font_family="Poppins"),
                            build_payment_method_row(),
                            ft.Container(
                                content=ft.Row([
                                    ft.Text("Estimated Prep Time: ", size=15, font_family="Poppins"),
                                    ft.Text("5-7 mins", size=15, font_family="Poppins"),
                                ], alignment="spaceBetween"),
                                padding=ft.padding.only(top=8, bottom=8),
                            ),
                                    ft.ElevatedButton(
                                content=ft.Text("Confirm Order", font_family="Poppins", size=15, weight="bold"),
                                style=ft.ButtonStyle(
                                    bgcolor="black",
                                    color="white",
                                    padding=ft.padding.symmetric(horizontal=0, vertical=10),
                                    shape=ft.RoundedRectangleBorder(radius=12),
                                ),
                                width=180,
                                on_click=lambda e: confirm_order(),  # Call confirm_order on click
                            ),
                        ],
                        spacing=10,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    width=300,
                    height=500,
                    bgcolor="#D2A06D",
                    border_radius=20,
                    padding=ft.padding.all(28),
                    shadow=ft.BoxShadow(blur_radius=4, color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK)),
                ),
            ],
            alignment="spaceBetween",
            spacing=20,
        )

    # Dialog for adding items to order
    def show_add_to_order_dialog(product_name, medio_price, product_image):
        nonlocal selected_add_ons, selected_size, quantity, add_ons_sum, subtotal_text
        grande_price = medio_price + 10  # Calculate Grande price by adding 10 to Medio price
        
        # Reset values for new dialog
        selected_add_ons = []  # Track selected add-ons
        selected_size = None  # Track selected size
        quantity = 1  # Initialize quantity

        # Define add_ons_sum to display the total cost of selected add-ons
        add_ons_sum = ft.Text("Total Add-ons: ₱0.00", size=14, weight="bold", color="black")
        subtotal_text = ft.Text("Subtotal: ₱0.00", size=14, weight="bold", color="black")

        # List of all add-ons
        all_add_ons = [
            "Pearl", "Crystal", "Cream Cheese", "Coffee Jelly", "Crushed Oreo", "Cream Puff", "Cheesecake"
        ]
        add_on_buttons = {}
        
        def make_add_on_button(add_on):
            btn = ft.ElevatedButton(
                add_on,
                style=ft.ButtonStyle(
                    bgcolor="#E0E0E0",
                    color="black",
                    padding=ft.padding.symmetric(horizontal=10, vertical=5),
                    shape=ft.RoundedRectangleBorder(radius=8),
                ),
                on_click=lambda e, a=add_on: toggle_add_on(a),
            )
            add_on_buttons[add_on] = btn
            return btn

        add_on_btn_list = [make_add_on_button(a) for a in all_add_ons]

        def toggle_add_on(add_on):
            nonlocal selected_add_ons
            # Allow multiple selections (check-style)
            btn = add_on_buttons[add_on]
            if add_on in selected_add_ons:
                selected_add_ons.remove(add_on)
                btn.style.bgcolor = "#E0E0E0"
            else:
                selected_add_ons.append(add_on)
                btn.style.bgcolor = "#BB6F19"
            btn.update()
            update_add_ons_sum()

        def update_add_ons_sum():
            nonlocal add_ons_sum
            add_ons_sum.value = f"Total Add-ons: ₱{len(selected_add_ons) * 9:.2f}"
            add_ons_sum.update()
            update_subtotal()

        def select_size(size):
            nonlocal selected_size
            selected_size = size
            # Update button styles
            medio_button.style.bgcolor = "#BB6F19" if size == "Medio" else "#E0E0E0"
            grande_button.style.bgcolor = "#BB6F19" if size == "Grande" else "#E0E0E0"
            medio_button.update()
            grande_button.update()
            update_subtotal()

        def update_subtotal():
            nonlocal subtotal_text
            if selected_size:
                base_price = medio_price if selected_size == "Medio" else grande_price
                add_ons_price = len(selected_add_ons) * 9
                total = (base_price + add_ons_price) * quantity
                subtotal_text.value = f"Subtotal: ₱{total:.2f}"
            else:
                subtotal_text.value = "Subtotal: ₱0.00"
            subtotal_text.update()

        def update_quantity(change):
            nonlocal quantity
            quantity = max(1, quantity + change)  # Ensure quantity is at least 1
            quantity_text.value = str(quantity)
            quantity_text.update()
            update_subtotal()

        quantity_text = ft.Text(str(quantity), size=14, color="black")

        # Create size buttons with initial gray style
        medio_button = ft.ElevatedButton(
            "Medio",
            style=ft.ButtonStyle(
                bgcolor="#E0E0E0",  # Default gray color
                color="black",
                padding=ft.padding.symmetric(horizontal=20, vertical=10),
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
            on_click=lambda e: select_size("Medio"),
        )

        grande_button = ft.ElevatedButton(
            "Grande",
            style=ft.ButtonStyle(
                bgcolor="#E0E0E0",  # Default gray color
                color="black",
                padding=ft.padding.symmetric(horizontal=20, vertical=10),
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
            on_click=lambda e: select_size("Grande"),
        )

        def add_to_order():
            nonlocal selected_size, selected_add_ons, quantity, medio_price, grande_price, product_name
            if not selected_size:
                return
            base_price = medio_price if selected_size == "Medio" else grande_price
            add_ons_price = len(selected_add_ons) * 9
            total_price = (base_price + add_ons_price) * quantity
            add_ons_str = ", ".join(selected_add_ons)
            
            # Insert the order into the database
            if insert_order(product_name, selected_size, add_ons_str, quantity, total_price):
                close_add_to_order_dialog()
                # Update the review order display if we're on that tab
                if selected_index == len(categories) - 1:
                    white_container_ref.current.content = build_review_order_container()
                    white_container_ref.current.update()
                    page.update()
            else:
                # Show error message if order insertion failed
                print("Failed to add order to database")

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
                        # Product Image and Size Options in a Row
                        ft.Row(
                            controls=[
                                # Left side - Product Image
                        ft.Container(
                            content=ft.Image(
                                src=product_image,
                                width=130,
                                height=130,
                                fit=ft.ImageFit.CONTAIN,
                                border_radius=8,
                            ),
                            alignment=ft.alignment.center,
                                    expand=True,
                        ),
                                # Right side - Size Options
                                ft.Container(
                                    content=ft.Column(
                            controls=[
                                            ft.Text("Select Size", size=16, weight="bold", color="black"),
                                            ft.Container(
                                                content=ft.Column(
                                    controls=[
                                                        medio_button,
                                                        ft.Text(f"₱{medio_price:.2f}", size=14, color="black", text_align="center"),
                                                        grande_button,
                                                        ft.Text(f"₱{grande_price:.2f}", size=14, color="black", text_align="center"),
                                                    ],
                                                    spacing=5,
                                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                                ),
                                            ),
                                        ],
                                        spacing=10,
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    ),
                                    expand=True,
                                ),
                            ],
                            alignment="spaceBetween",
                            spacing=20,
                        ),
                        # Add-ons Section (second)
                                ft.Column(
                                    controls=[
                                ft.Text("Add-ons:", size=14, weight="bold", color="black"),
                                ft.Container(
                                    content=ft.Row(
                                        controls=add_on_btn_list,
                                        spacing=10,
                                        wrap=True,
                                        alignment=ft.MainAxisAlignment.CENTER,
                                    ),
                                    padding=ft.padding.symmetric(horizontal=20, vertical=10),
                                    alignment=ft.alignment.center,
                                ),
                                add_ons_sum,
                            ],
                            spacing=10,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        # Quantity Section (third)
                        ft.Column([
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
                            subtotal_text,
                        ], spacing=5),
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
                                    on_click=lambda e: add_to_order() if selected_size else None,  # Only allow adding if size is selected
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

    # At the top-level of main():
    manager_password_field = ft.TextField(
        label="Enter Passowrd",
        width=250,
        password=True,
        border=ft.InputBorder.OUTLINE,
    )
    void_error_text = ft.Text("", color="red", size=12)

    # Password modal
    void_password_modal = ft.Container(
        visible=False,
        alignment=ft.alignment.center,
        bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.BLACK),
        expand=True,
        content=ft.Container(
            width=void_modal_width,
            height=void_modal_height,
            bgcolor="white",
            border_radius=12,
            padding=ft.padding.all(20),
            content=ft.Column([
                ft.Text("Manager Approval", size=18, weight="bold", font_family="Poppins"),
                manager_password_field,
                void_error_text,
                ft.Row([
                    ft.ElevatedButton("Cancel", on_click=lambda e: close_void_password_modal()),
                    ft.ElevatedButton("Submit", on_click=lambda e: check_manager_password()),
                ], alignment="end", spacing=10),
            ], spacing=10),
        ),
    )

    # Add modal to page.overlay if not already present
    if void_password_modal not in page.overlay:
        page.overlay.append(void_password_modal)

    # Functions to control modal flow
    def open_void_password_modal():
        manager_password_field.value = ""
        void_error_text.value = ""
        void_password_modal.visible = True
        page.update()

    def close_void_password_modal():
        void_password_modal.visible = False
        void_error_text.value = ""
        page.update()

    def check_manager_password():
        conn = get_db_connection()
        if conn and conn.is_connected():
            cursor = conn.cursor()
            cursor.execute("SELECT password FROM admin WHERE username = 'BBADMIN'")
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            if row:
                db_hashed_pw = row[0]
                entered_hashed_pw = hash_password(manager_password_field.value)
                if entered_hashed_pw == db_hashed_pw:
                    void_password_modal.visible = False
                    page.update()
                    return
        void_error_text.value = "Incorrect manager password."
        page.update()

    # Function to update payment method
    def select_payment_method(method):
        global selected_payment_method
        selected_payment_method = method
        page.update()

    # Update build_payment_method_row to use refs and update styles on click
    def build_payment_method_row():
        def update_payment_buttons():
            if cash_btn_ref.current:
                cash_btn_ref.current.style.bgcolor = "#B87A2A" if selected_payment_method == "Cash" else "#F5E9DA"
                cash_btn_ref.current.style.color = "white" if selected_payment_method == "Cash" else "#B87A2A"
                cash_btn_ref.current.update()
            if gcash_btn_ref.current:
                gcash_btn_ref.current.style.bgcolor = "#1976D2" if selected_payment_method == "GCash" else "white"
                gcash_btn_ref.current.style.color = "white" if selected_payment_method == "GCash" else "#1976D2"
                gcash_btn_ref.current.style.side = ft.border.all(1, "#B87A2A") if selected_payment_method != "GCash" else None
                gcash_btn_ref.current.update()

        def on_cash_click(e):
            global selected_payment_method
            selected_payment_method = "Cash"
            update_payment_buttons()

        def on_gcash_click(e):
            global selected_payment_method
            selected_payment_method = "GCash"
            update_payment_buttons()

        return ft.Row([
            ft.ElevatedButton(
                ref=cash_btn_ref,
                content=ft.Row([
                    ft.Image(src="assets/icons/cash.png", width=22, height=22),
                    ft.Text("Cash", font_family="Poppins", size=15, weight="bold"),
                ], spacing=8),
                style=ft.ButtonStyle(
                    bgcolor="#B87A2A" if selected_payment_method == "Cash" else "#F5E9DA",
                    color="white" if selected_payment_method == "Cash" else "#B87A2A",
                    padding=ft.padding.symmetric(horizontal=18, vertical=8),
                    shape=ft.RoundedRectangleBorder(radius=8),
                ),
                on_click=on_cash_click,
            ),
            ft.ElevatedButton(
                ref=gcash_btn_ref,
                content=ft.Row([
                    ft.Image(src="assets/icons/gcash.png", width=22, height=22),
                    ft.Text("GCash", font_family="Poppins", size=15, weight="bold"),
                ], spacing=8),
                style=ft.ButtonStyle(
                    bgcolor="#1976D2" if selected_payment_method == "GCash" else "white",
                    color="white" if selected_payment_method == "GCash" else "#1976D2",
                    padding=ft.padding.symmetric(horizontal=18, vertical=8),
                    shape=ft.RoundedRectangleBorder(radius=8),
                    side=ft.border.all(1, "#B87A2A") if selected_payment_method != "GCash" else None,
                ),
                on_click=on_gcash_click,
            ),
        ], spacing=10)

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

def confirm_order():
    orders = fetch_pending_orders()
    if not orders:
        print("No orders to confirm.")
        return

    total_items = sum(order[4] for order in orders)  # quantity
    subtotal = sum(order[5] for order in orders)  # price
    add_ons_total = sum(len(order[3].split(", ")) * 9 if order[3] else 0 for order in orders)
    grand_total = subtotal + add_ons_total

    try:
        conn = get_db_connection()
        if conn and conn.is_connected():
            cursor = conn.cursor()

            # Generate a unique order number and order code
            cursor.execute("SELECT MAX(order_number) FROM transactions")
            max_order_number = cursor.fetchone()[0]
            order_number = (max_order_number + 1) if max_order_number else 1
            order_code = f"BBR{order_number:04d}"

            # Save transaction details
            cursor.execute("""
                INSERT INTO transactions (order_number, order_code, payment_method, total_amount, status)
                VALUES (%s, %s, %s, %s, %s)
            """, (order_number, order_code, selected_payment_method or "Cash", grand_total, "Normal"))

            # Update orders to mark them as confirmed
            for order in orders:
                cursor.execute("""
                    UPDATE orders
                    SET status = 'Confirmed'
                    WHERE order_id = %s
                """, (order[0],))

            conn.commit()
            cursor.close()
            conn.close()

            print(f"Order confirmed with Order Code: {order_code}")

            # Generate receipt layout
            from datetime import datetime
            now = datetime.now()
            date_str = now.strftime('%d-%m-%Y')
            time_str = now.strftime('%I:%M %p')

            receipt_container = ft.Container(
                alignment=ft.alignment.center,  # Center the receipt modal
                content=ft.Column(
                    controls=[
                        # Logo and Header
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Image(src="assets/logos/bigbrew_logo_black.png", width=50, height=50),
                                    ft.Text("BIGBREW", size=20, weight="bold", text_align="center"),
                                    ft.Text("San Jose, Jaro, Iloilo City\n5000 Iloilo, Iloilo City\n0919 718 9473",
                                            size=12, text_align="center", color="black"),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=5,
                            ),
                            padding=ft.padding.only(bottom=10),
                        ),
                        ft.Divider(height=1, thickness=1, color="black"),
                        # Date, Time, and Order Info
                        ft.Row(
                            controls=[
                                ft.Text(f"{date_str}\nTime: {time_str}", size=12, color="black"),
                                ft.Text(f"Order Number: {order_number}\nOrder Code: {order_code}", size=12, color="black"),
                            ],
                            alignment="spaceBetween",
                        ),
                        ft.Divider(height=1, thickness=1, color="black"),
                        # Items Section
                        ft.Row(
                            controls=[
                                ft.Text("Name", size=12, weight="bold"),
                                ft.Text("Size", size=12, weight="bold"),
                                ft.Text("Qty", size=12, weight="bold"),
                                ft.Text("Price", size=12, weight="bold"),
                            ],
                            alignment="spaceBetween",
                        ),
                        *[
                            ft.Row(
                                controls=[
                                    ft.Text(order[1], size=12),  # Product name
                                    ft.Text(order[2], size=12),  # Size
                                    ft.Text(str(order[4]), size=12),  # Quantity
                                    ft.Text(f"₱{order[5]:.2f}", size=12),  # Price
                                ],
                                alignment="spaceBetween",
                            )
                            for order in orders
                        ],
                        ft.Divider(height=1, thickness=1, color="black"),
                        # Add-ons Section
                        ft.Row(
                            controls=[
                                ft.Text("Add-ons", size=12, weight="bold"),
                                ft.Text("Price", size=12, weight="bold"),
                            ],
                            alignment="spaceBetween",
                        ),
                        *[
                            ft.Row(
                                controls=[
                                    ft.Text(add_on, size=12),
                                    ft.Text("₱9.00", size=12),
                                ],
                                alignment="spaceBetween",
                            )
                            for order in orders if order[3]
                            for add_on in order[3].split(", ")
                        ],
                        ft.Divider(height=1, thickness=1, color="black"),
                        # Price Summary
                        ft.Row(
                            controls=[
                                ft.Text("Price", size=12, weight="bold"),
                                ft.Text(f"₱{grand_total:.2f}", size=12, weight="bold"),
                            ],
                            alignment="spaceBetween",
                        ),
                        ft.Divider(height=1, thickness=1, color="black"),
                        # Footer
                        ft.Text("Thank You!", size=14, weight="bold", text_align="center"),
                        ft.Text("Michael Escosa", size=12, text_align="center"),
                    ],
                    spacing=10,
                    expand=True,  # Make the ListView scrollable
                ),
                width=350,
                height=600,
                bgcolor="white",
                border_radius=10,
                padding=ft.padding.all(20),
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=15,
                    color=ft.Colors.with_opacity(0.2, ft.Colors.BLACK),
                    offset=ft.Offset(0, 3),
                ),
            )

            # Close button
            close_button = ft.ElevatedButton(
                "Close",
                style=ft.ButtonStyle(
                    bgcolor="#BB6F19",
                    color="white",
                    padding=ft.padding.symmetric(horizontal=20, vertical=10),
                    shape=ft.RoundedRectangleBorder(radius=8),
                ),
                on_click=lambda e: close_receipt_modal(page)
            )

            # Display receipt preview
            receipt_modal = ft.Container(
                visible=True,
                alignment=ft.alignment.center,  # Ensure the modal is centered
                bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.BLACK),
                expand=True,
                content=receipt_container
            )
            page.overlay.append(receipt_modal)
            page.update()

            # Refresh the transactions table
            from views.transactions import transactions_view
            transactions_view(page)
        else:
            print("Error: Unable to connect to the database.")
    except Exception as e:
        print(f"Error confirming order: {str(e)}")

def close_receipt_modal(page):
    page.overlay.clear()  # Clear all elements from the overlay
    page.update()  # Update the page to reflect changes