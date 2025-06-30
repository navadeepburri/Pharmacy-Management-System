import mysql.connector
from config import DB_CONFIG

def setup_database():
    # Connect without specifying a database
    conn = mysql.connector.connect(
        host=DB_CONFIG['host'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password']
    )
    cursor = conn.cursor()
    
    # Create database
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
    
    # Connect to the new database
    conn.database = DB_CONFIG['database']
    
    # Create tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS drugs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        description TEXT,
        quantity INT NOT NULL,
        price DECIMAL(10, 2) NOT NULL,
        expiry_date DATE,
        company_id INT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        id INT AUTO_INCREMENT PRIMARY KEY,
        drug_id INT NOT NULL,
        quantity INT NOT NULL,
        unit_price DECIMAL(10, 2) NOT NULL,
        total_amount DECIMAL(10, 2) NOT NULL,
        sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (drug_id) REFERENCES drugs(id)
    )
    """)
    
    # Add more tables as needed (users, companies, etc.)
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Database setup completed successfully!")

if __name__ == '__main__':
    setup_database()