import sys
import sqlite3
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QTextEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QListWidget
)

# Database Setup
def create_tables():
    conn = sqlite3.connect("billing.db")
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            details TEXT,
            amount REAL,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    ''')

    conn.commit()
    conn.close()

class BillingApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Billing App")

        # --- Form fields ---
        self.name_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.details_input = QTextEdit()
        self.amount_input = QLineEdit()

        # --- Buttons ---
        self.submit_btn = QPushButton("Add Bill")
        self.show_customers_btn = QPushButton("Show Customers")
        self.show_bills_btn = QPushButton("Show Bills")

        # --- List display ---
        self.list_widget = QListWidget()

        # Layout
        self.setup_layout()

        # Button actions
        self.submit_btn.clicked.connect(self.add_bill)
        self.show_customers_btn.clicked.connect(self.show_customers)
        self.show_bills_btn.clicked.connect(self.show_bills)

    def setup_layout(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Customer Name"))
        layout.addWidget(self.name_input)

        layout.addWidget(QLabel("Phone Number"))
        layout.addWidget(self.phone_input)

        layout.addWidget(QLabel("Bill Details"))
        layout.addWidget(self.details_input)

        layout.addWidget(QLabel("Amount"))
        layout.addWidget(self.amount_input)

        layout.addWidget(self.submit_btn)

        # Add list display and buttons
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.show_customers_btn)
        btn_layout.addWidget(self.show_bills_btn)

        layout.addLayout(btn_layout)
        layout.addWidget(self.list_widget)

        self.setLayout(layout)

    def add_bill(self):
        name = self.name_input.text()
        phone = self.phone_input.text()
        details = self.details_input.toPlainText()
        try:
            amount = float(self.amount_input.text())
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter a valid amount.")
            return

        if not name or not phone or not details:
            QMessageBox.warning(self, "Input Error", "Please fill all fields.")
            return

        conn = sqlite3.connect("billing.db")
        cursor = conn.cursor()

        # Check if customer exists
        cursor.execute("SELECT id FROM customers WHERE name=? AND phone=?", (name, phone))
        customer = cursor.fetchone()

        if customer:
            customer_id = customer[0]
        else:
            cursor.execute("INSERT INTO customers (name, phone) VALUES (?, ?)", (name, phone))
            customer_id = cursor.lastrowid

        cursor.execute("INSERT INTO bills (customer_id, details, amount) VALUES (?, ?, ?)",
                       (customer_id, details, amount))

        conn.commit()
        conn.close()

        QMessageBox.information(self, "Success", "Bill added successfully!")

        # Clear inputs
        self.name_input.clear()
        self.phone_input.clear()
        self.details_input.clear()
        self.amount_input.clear()

    def show_customers(self):
        self.list_widget.clear()
        conn = sqlite3.connect("billing.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM customers")
        customers = cursor.fetchall()

        if customers:
            for cust in customers:
                display = f"ID: {cust[0]}, Name: {cust[1]}, Phone: {cust[2]}"
                self.list_widget.addItem(display)
        else:
            self.list_widget.addItem("No customers found.")

        conn.close()

    def show_bills(self):
        self.list_widget.clear()
        conn = sqlite3.connect("billing.db")
        cursor = conn.cursor()

        cursor.execute('''
            SELECT bills.id, customers.name, bills.details, bills.amount
            FROM bills
            INNER JOIN customers ON bills.customer_id = customers.id
        ''')
        bills = cursor.fetchall()

        if bills:
            for bill in bills:
                display = f"Bill ID: {bill[0]}, Customer: {bill[1]}, Details: {bill[2]}, Amount: {bill[3]}"
                self.list_widget.addItem(display)
        else:
            self.list_widget.addItem("No bills found.")

        conn.close()

if __name__ == "__main__":
    create_tables()

    app = QApplication(sys.argv)

    window = BillingApp()
    window.resize(400, 600)
    window.show()
    sys.exit(app.exec())
