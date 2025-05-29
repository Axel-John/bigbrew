import mysql.connector
from mysql.connector import Error
from utils.password import hash_password

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="bigbrew_db"
        )
        if connection.is_connected():
            print("Successfully connected to MariaDB")
            return connection
    except Error as e:
        print(f"Error connecting to MariaDB: {e}")
        return None
    return None

def init_db():
    conn = get_db_connection()
    if conn and conn.is_connected():
        cursor = conn.cursor()
        
        # Create products table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                product_id VARCHAR(20) PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                type VARCHAR(50) NOT NULL,
                price DECIMAL(10,2) NOT NULL,
                availability ENUM('Available', 'Limited', 'Out of Stock') NOT NULL,  # Use ENUM for valid values
                image_path VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create admin table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                full_name VARCHAR(100) NOT NULL,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create employees table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INT AUTO_INCREMENT PRIMARY KEY,
                employee_id VARCHAR(20) UNIQUE NOT NULL,
                first_name VARCHAR(100) NOT NULL,
                last_name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                role VARCHAR(20) NOT NULL,  # Ensure the role column exists
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Alter the table if the role column is missing
        cursor.execute("""
            ALTER TABLE employees
            ADD COLUMN IF NOT EXISTS role VARCHAR(20) NOT NULL
        """)

        # Create default admin employee account if not exists
        from utils.auth import hash_password
        employee_id = "EMP0001"
        first_name = "Admin"
        last_name = "Emp"
        email = "admin.emp@gmail.com"
        password = hash_password("admin123")
        role = "admin"
        cursor.execute("SELECT * FROM employees WHERE employee_id = %s", (employee_id,))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO employees (employee_id, first_name, last_name, email, password, role)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (employee_id, first_name, last_name, email, password, role))
            conn.commit()
            print("Default admin employee account created!")
        else:
            print("Default admin employee account already exists.")

        # Create admin account if not exists
        cursor.execute("SELECT * FROM admin WHERE username = 'BBADMIN'")
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO admin (username, full_name, password)
                VALUES (%s, %s, %s)
            """, ('BBADMIN', 'Big Brew Admin', hash_password('admin123')))

        conn.commit()
        cursor.close()
        conn.close()
        print("Database initialized successfully!")
    else:
        print("Failed to connect to database!")

def create_employee_admin():
    from utils.auth import hash_password
    conn = get_db_connection()
    if conn and conn.is_connected():
        cursor = conn.cursor()
        employee_id = "EMP001"
        first_name = "Admin"
        last_name = "Emp"
        email = "admin.emp@gmail.com"
        password = hash_password("admin123")  # Change password as needed
        role = "admin"
        # Check if employee already exists
        cursor.execute("SELECT * FROM employees WHERE employee_id = %s", (employee_id,))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO employees (employee_id, first_name, last_name, email, password, role)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (employee_id, first_name, last_name, email, password, role))
            conn.commit()
            print("Employee admin account created!")
        else:
            print("Employee admin account already exists.")
        cursor.close()
        conn.close()

init_db()