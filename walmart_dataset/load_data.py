import psycopg2
import os
from pathlib import Path

conn_string = os.environ.get("POSTGRES_CONN")
if not conn_string:
    raise RuntimeError("POSTGRES_CONN is not set")

# CSV files mapping to tables
csv_files = {
    "customers.csv": "raw.customers",
    "stores.csv": "raw.stores",
    "products.csv": "raw.products",
    "employees.csv": "raw.employees",
    "orders.csv": "raw.orders",
    "order_items.csv": "raw.order_items",
}

data_dir = Path(__file__).resolve().parent / "data"
conn = None

try:
    # Connect to the database
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    
    # Load each CSV file into its corresponding table
    for csv_file, table_name in csv_files.items():
        csv_path = data_dir / csv_file
        
        if os.path.exists(csv_path):
            print(f"Loading {csv_file} into {table_name}...")
            
            with csv_path.open("r", newline="") as f:
                cursor.copy_expert(f"COPY {table_name} FROM STDIN WITH (FORMAT CSV, HEADER TRUE)", f)
            
            conn.commit()
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            print(f"Successfully loaded {csv_file}: {cursor.fetchone()[0]} rows in {table_name}")
        else:
            print(f"✗ File not found: {csv_path}")
    
    cursor.close()
    conn.close()
    print("\nAll data loaded successfully!")
    
except Exception as e:
    print(f"Error: {e}")
    if conn:
        conn.rollback()
        conn.close()
