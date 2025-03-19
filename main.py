import sys
import sqlite3
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QTextEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox,
    QTableWidget, QTableWidgetItem, QTabWidget, QHeaderView
)
from PySide6.QtGui import QFont

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
        self.resize(650, 550)

        # --- Form fields ---
        self.name_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.details_input = QTextEdit()
        self.amount_input = QLineEdit()

        # --- Buttons ---
        self.submit_btn = QPushButton("Add Bill")

        # --- Tables ---
        self.customer_table = QTableWidget()
        self.bills_table = QTableWidget()

        # Layout
        self.setup_layout()
        self.apply_styles()

        # Button actions
        self.submit_btn.clicked.connect(self.add_bill)

    def setup_layout(self):
        layout = QVBoxLayout()

        # Title
        title = QLabel("🧾 Billing Management")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title)

        # Form Layout
        layout.addWidget(QLabel("Customer Name:"))
        layout.addWidget(self.name_input)

        layout.addWidget(QLabel("Phone Number:"))
        layout.addWidget(self.phone_input)

        layout.addWidget(QLabel("Bill Details:"))
        layout.addWidget(self.details_input)

        layout.addWidget(QLabel("Amount:"))
        layout.addWidget(self.amount_input)

        layout.addWidget(self.submit_btn)

        # Tabs for Customer and Bills View
        tab_widget = QTabWidget()
        tab_widget.addTab(self.customer_table, "Customers")
        tab_widget.addTab(self.bills_table, "Bills")

        layout.addWidget(tab_widget)

        self.setLayout(layout)

        # Load data on start
        self.show_customers()
        self.show_bills()

    def apply_styles(self):
        # Window background
        self.setStyleSheet("background-color: #f0f0f0;")

        # Input fields
        input_style = """
            QLineEdit, QTextEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 5px;
                font-size: 14px;
            }
        """
        self.name_input.setStyleSheet(input_style)
        self.phone_input.setStyleSheet(input_style)
        self.details_input.setStyleSheet(input_style)
        self.amount_input.setStyleSheet(input_style)

        # Button style
        self.submit_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)

        # Table style
        table_style = """
            QTableWidget {
                background-color: white;
                border: 1px solid #ccc;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                font-weight: bold;
                padding: 4px;
                border: 1px solid #ccc;
            }
        """
        self.customer_table.setStyleSheet(table_style)
        self.bills_table.setStyleSheet(table_style)

    def add_bill(self):
        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()
        details = self.details_input.toPlainText().strip()

        # Validate amount
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

        # Refresh tables
        self.show_customers()
        self.show_bills()

    def show_customers(self):
        conn = sqlite3.connect("billing.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM customers")
        customers = cursor.fetchall()
        conn.close()

        # Configure table
        self.customer_table.clear()
        self.customer_table.setRowCount(len(customers))
        self.customer_table.setColumnCount(3)
        self.customer_table.setHorizontalHeaderLabels(["Customer ID", "Name", "Phone"])

        for row_idx, customer in enumerate(customers):
            for col_idx, item in enumerate(customer):
                table_item = QTableWidgetItem(str(item))
                self.customer_table.setItem(row_idx, col_idx, table_item)

        self.customer_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.customer_table.verticalHeader().setVisible(False)

    def show_bills(self):
        conn = sqlite3.connect("billing.db")
        cursor = conn.cursor()

        cursor.execute('''
            SELECT bills.id, customers.name, bills.details, bills.amount
            FROM bills
            INNER JOIN customers ON bills.customer_id = customers.id
        ''')
        bills = cursor.fetchall()
        conn.close()

        # Configure table
        self.bills_table.clear()
        self.bills_table.setRowCount(len(bills))
        self.bills_table.setColumnCount(4)
        self.bills_table.setHorizontalHeaderLabels(["Bill ID", "Customer Name", "Details", "Amount"])

        for row_idx, bill in enumerate(bills):
            for col_idx, item in enumerate(bill):
                table_item = QTableWidgetItem(str(item))
                self.bills_table.setItem(row_idx, col_idx, table_item)

        self.bills_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.bills_table.verticalHeader().setVisible(False)

if __name__ == "__main__":
    create_tables()

    app = QApplication(sys.argv)

    window = BillingApp()
    window.show()

    sys.exit(app.exec())
