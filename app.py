import mysql.connector
from fpdf import FPDF

# Koneksi ke database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="posdb"
)
cursor = db.cursor()

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Nota Transaksi', align='C', ln=True)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Halaman {self.page_no()}', 0, 0, 'C')

def print_transaction(transaction_id):
    query = "SELECT t.transaction_id, p.product_name, t.quantity, t.total_amount " \
            "FROM transactions t " \
            "JOIN products p ON t.product_id = p.product_id " \
            "WHERE t.transaction_id = %s"
    cursor.execute(query, (transaction_id,))
    transaction = cursor.fetchall()

    pdf = PDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 12)

    for row in transaction:
        pdf.cell(50, 10, row[1], 1)
        pdf.cell(30, 10, str(row[2]), 1)
        pdf.cell(40, 10, f"${row[3]:.2f}", 1)
        pdf.ln()

    pdf.output(f'transaction_{transaction_id}.pdf')

# Fungsi untuk menambahkan produk ke database
def add_product(name, price, stock):
    query = "INSERT INTO products (product_name, price, stock) VALUES (%s, %s, %s)"
    values = (name, price, stock)
    cursor.execute(query, values)
    db.commit()
    print("Produk ditambahkan!")

# Fungsi untuk menampilkan daftar produk
def list_products():
    query = "SELECT product_id, product_name, price, stock FROM products"
    cursor.execute(query)
    products = cursor.fetchall()
    for product in products:
        product_id, product_name, price, stock = product
        print(f"{product_id}: {product_name} - Harga: ${price:.2f} - Stok: {stock}")

# Fungsi untuk melakukan transaksi
def make_transaction(product_id, quantity):
    query = "SELECT product_name, price, stock FROM products WHERE product_id = %s"
    cursor.execute(query, (product_id,))
    result = cursor.fetchone()

    if result:
        product_name, price, stock = result
        if stock >= quantity:
            total_amount = price * quantity
            query = "INSERT INTO transactions (product_id, quantity, total_amount) VALUES (%s, %s, %s)"
            cursor.execute(query, (product_id, quantity, total_amount))
            db.commit()
            print(f"Transaksi berhasil! Harga total: ${total_amount:.2f}")
            # Kurangi stok produk
            query = "UPDATE products SET stock = stock - %s WHERE product_id = %s"
            cursor.execute(query, (quantity, product_id))
            db.commit()
            print_transaction(cursor.lastrowid)
        else:
            print("Stok tidak mencukupi.")
    else:
        print("Produk tidak ditemukan.")

# Main program
if __name__ == "__main__":
    while True:
        print("\nMenu:")
        print("1. Tambah Produk")
        print("2. Transaksi")
        print("3. Lihat Daftar Produk")
        print("4. Keluar")
        choice = input("Pilihan: ")

        if choice == "1":
            name = input("Nama Produk: ")
            price = float(input("Harga: "))
            stock = int(input("Stok: "))
            add_product(name, price, stock)

        elif choice == "2":
            list_products()
            product_id = int(input("Masukkan ID Produk: "))
            quantity = int(input("Jumlah: "))
            make_transaction(product_id, quantity)

        elif choice == "3":
            list_products()

        elif choice == "4":
            break
