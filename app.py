# Ticket Support and Order Management System
import streamlit as st
import sqlite3
import uuid

# Initialize the database
def init_db():
    conn = sqlite3.connect('ticket_support.db')
    return conn

def create_user(conn, name, phno, mail_id, password, dob, gender):
    try:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (name, phno, mail_id, password, dob, gender) VALUES (?, ?, ?, ?, ?, ?)', 
                       (name, phno, mail_id, password, dob, gender))
        conn.commit()
        st.success("Account created successfully!")
    except sqlite3.IntegrityError:
        st.error(f"User with email ID '{mail_id}' or phone number '{phno}' already exists.")

def login_user(conn, name, mail_id, password):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE name = ? AND mail_id = ? AND password = ?', (name, mail_id, password))
    user = cursor.fetchone()
    if user:
        st.success("LOGIN Successfully")
        return user
    else:
        st.error("Incorrect name, email, or password")
        return None

def view_details(conn, phno):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE phno = ?', (phno,))
    user = cursor.fetchone()
    if user:
        st.write("===== Customer Details =====")
        st.write(f"Name: {user[1]}\nPhno: {user[2]}\nMailId: {user[3]}\nDob: {user[5]}\nGender: {user[6]}")
    else:
        st.error("Phone number not found!")

def update_details(conn, phno):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE phno = ?', (phno,))
    user = cursor.fetchone()
    if user:
        st.write("\nSelect the field you want to update:")
        options = ["Name", "Phone number", "Email ID", "Password", "Date of Birth", "Gender"]
        choice = st.selectbox("Select the field to update:", options)

        if choice == 'Name':
            new_value = st.text_input("Enter your new name:")
            if st.button("Update"):
                cursor.execute('UPDATE users SET name = ? WHERE phno = ?', (new_value, phno))
        elif choice == 'Phone number':
            new_value = st.text_input("Enter your new phone number:")
            if st.button("Update"):
                cursor.execute('UPDATE users SET phno = ? WHERE phno = ?', (new_value, phno))
        elif choice == 'Email ID':
            new_value = st.text_input("Enter your new email ID:")
            if st.button("Update"):
                cursor.execute('UPDATE users SET mail_id = ? WHERE phno = ?', (new_value, phno))
        elif choice == 'Password':
            new_password = st.text_input("Enter the new password", type="password")
            confirm_password = st.text_input("Confirm the password", type="password")
            if new_password == confirm_password:
                if st.button("Update"):
                    cursor.execute('UPDATE users SET password = ? WHERE phno = ?', (new_password, phno))
            else:
                st.error("Passwords do not match")
        elif choice == 'Date of Birth':
            new_value = st.text_input("Enter your new date of birth:")
            if st.button("Update"):
                cursor.execute('UPDATE users SET dob = ? WHERE phno = ?', (new_value, phno))
        elif choice == 'Gender':
            new_value = st.text_input("Enter your new gender:")
            if st.button("Update"):
                cursor.execute('UPDATE users SET gender = ? WHERE phno = ?', (new_value, phno))
        
        conn.commit()
        st.success("Details updated successfully!")
    else:
        st.error("Phone number not found!")

def order_product(conn, phno):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE phno = ?', (phno,))
    user = cursor.fetchone()
    if user:
        product_list = {'Ear rings': 149, 'Watch': 220, 'Shoes': 600, 'Nail Polish': 60, 'Bag': 250}
        orders = []

        order_date = st.date_input("Enter the date of the order (YYYY-MM-DD):").strftime("%Y-%m-%d")

        while True:
            st.write("\nAvailable Products:")
            for product, price in product_list.items():
                st.write(f"{product}: {price}/-")

            selected_product = st.selectbox("Select the product to order:", list(product_list.keys()))
            quantity = st.number_input("Enter the quantity:", min_value=1, step=1)

            if st.button("Add to Order"):
                total_price = product_list[selected_product] * quantity
                st.write(f"\n===== Order Details =====\nProduct: {selected_product}\nQuantity: {quantity}\nTotal Price: {total_price}/-")

                orders.append({'product': selected_product, 'quantity': quantity, 'total_price': total_price, 'order_date': order_date})
                break

        if orders:
            for order in orders:
                cursor.execute('INSERT INTO orders (user_id, product, quantity, total_price, order_date) VALUES (?, ?, ?, ?, ?)', 
                               (user[0], order['product'], order['quantity'], order['total_price'], order['order_date']))
            conn.commit()
            st.success("Order placed successfully!")
        else:
            st.error("No orders placed.")
    else:
        st.error("Phone number not found!")

def generate_bill(conn, phno):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE phno = ?', (phno,))
    user = cursor.fetchone()
    if user:
        cursor.execute('SELECT * FROM orders WHERE user_id = ?', (user[0],))
        orders = cursor.fetchall()
        if orders:
            bill_id = str(uuid.uuid4())
            st.write("\n===== Customer Details =====")
            st.write(f"Name: {user[1]}\nPhno: {user[2]}\nMailId: {user[3]}\nDob: {user[5]}\nGender: {user[6]}")
            st.write("\n===== Bill =====")
            total_bill = 0
            for order in orders:
                total_bill += order[4]
                st.write(f"Product: {order[2]}\nQuantity: {order[3]}\nTotal Price: {order[4]}/-")
                st.write(f"Order Date: {order[5]}")

            extra_amount = 500
            e_bill = total_bill + extra_amount

            st.write(f"Total Bill: {e_bill}/-\n")
            return bill_id
        else:
            st.error("No orders found. Please place an order first.")
    else:
        st.error("Phone number not found!")

def raise_a_ticket(conn, bill_id):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM orders WHERE id = ?', (bill_id,))
    order = cursor.fetchone()
    if order:
        st.write("\n===== Raising a Ticket =====")
        ticket_description = st.text_area("Enter the description for the ticket:")
        reported_total_price = st.number_input("Enter the correct total bill amount:")

        if st.button("Raise Ticket"):
            cursor.execute('INSERT INTO tickets (order_id, description, status) VALUES (?, ?, ?)', 
                           (order[0], ticket_description, 'Open'))
            conn.commit()
            st.success(f"Ticket raised successfully with ID: {bill_id}")
            st.write("Issue reported successfully. The total bill amount in the order has been updated.\n")

            st.write("Generating bill...")
            st.write("\n===== Customer Details =====")
            st.write(f"Name: {order[1]}\nPhno: {order[2]}\nMailId: {order[3]}\nDob: {order[5]}\nGender: {order[6]}")
            st.write("\n===== Bill =====")
            st.write(f"Product: {order[2]}\nQuantity: {order[3]}\nTotal Price: {reported_total_price}/-")
            st.write(f"Order Date: {order[5]}")
            st.write(f"Total Bill: {reported_total_price}/-\n")
            st.write("Bill generated successfully")
            st.write("Ticket Status: Closed")
    else:
        st.error("No orders found with the provided Bill ID.")

def total_orders(conn, target_month):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE order_date LIKE ?", (f"{target_month}%",))
    orders = cursor.fetchall()
    if orders:
        st.write(f"Orders for {target_month}:\n")
        total_products = {}
        unique_products = set()

        for order in orders:
            product = order[2]
            quantity = order[3]
            total_products[product] = total_products.get(product, 0) + quantity
            unique_products.add(product)

            st.write(f"Product: {order[2]}\nQuantity: {order[3]}\nTotal Price: {order[4]}/-")
            st.write(f"Order Date: {order[5]}\n{'=' * 20}")

        st.write("\nTotal number of products ordered in specified month:")
        for product, total_quantity in total_products.items():
            st.write(f"{product}: {total_quantity}")

        st.write(f"\nTotal number of unique products ordered in {target_month}: {len(unique_products)}\n")
    else:
        st.error("No orders found for the specified month.")

# Streamlit interface
st.title("Ticket Support Portal")

conn = init_db()

menu = ["Signup", "Login", "View Details", "Update Details", "Order Product", "Generate Bill", "Raise a Ticket", "Total Orders"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Signup":
    st.subheader("Create an Account")
    name = st.text_input("Name")
    phno = st.text_input("Phone number")
    mail_id = st.text_input("Email ID")
    password = st.text_input("Password", type='password')
    dob = st.text_input("Date of Birth")
    gender = st.text_input("Gender")
    if st.button("Signup"):
        create_user(conn, name, phno, mail_id, password, dob, gender)

elif choice == "Login":
    st.subheader("Login")
    name = st.text_input("Name")
    mail_id = st.text_input("Email ID")
    password = st.text_input("Password", type='password')
    if st.button("Login"):
        login_user(conn, name, mail_id, password)

elif choice == "View Details":
    st.subheader("View Details")
    phno = st.text_input("Enter phone number")
    if st.button("View"):
        view_details(conn, phno)

elif choice == "Update Details":
    st.subheader("Update Details")
    phno = st.text_input("Enter phone number")
    if st.button("Update"):
        update_details(conn, phno)

elif choice == "Order Product":
    st.subheader("Order Product")
    phno = st.text_input("Enter phone number")
    if st.button("Order"):
        order_product(conn, phno)

elif choice == "Generate Bill":
    st.subheader("Generate Bill")
    phno = st.text_input("Enter phone number")
    if st.button("Generate"):
        generate_bill(conn, phno)

elif choice == "Raise a Ticket":
    st.subheader("Raise a Ticket")
    bill_id = st.text_input("Enter Bill ID")
    if st.button("Raise Ticket"):
        raise_a_ticket(conn, bill_id)

elif choice == "Total Orders":
    st.subheader("Total Orders")
    target_month = st.text_input("Enter month (YYYY-MM)")
    if st.button("Show Orders"):
        total_orders(conn, target_month)


