"""
Run this ONCE before starting the app:
    python init_db.py

This script:
  1. Connects to MySQL
  2. Creates the 'propflow' database if it doesn't exist
  3. Creates the 'properties' table
  4. Seeds 5 demo properties
"""

import pymysql
from config import DB_CONFIG

def setup():
    # Step 1: Connect WITHOUT specifying a database (to create it first)
    conn = pymysql.connect(
        host     = DB_CONFIG['host'],
        port     = DB_CONFIG['port'],
        user     = DB_CONFIG['user'],
        password = DB_CONFIG['password'],
        cursorclass = pymysql.cursors.DictCursor
    )
    cur = conn.cursor()

    # Step 2: Create database
    cur.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_CONFIG['database']}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    cur.execute(f"USE `{DB_CONFIG['database']}`")
    print(f"✅ Database '{DB_CONFIG['database']}' ready.")

    # Step 3: Create table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS properties (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            title       VARCHAR(120)  NOT NULL,
            type        VARCHAR(50)   NOT NULL,
            city        VARCHAR(80)   NOT NULL,
            address     VARCHAR(200)  NOT NULL,
            price       DECIMAL(15,2) NOT NULL,
            bedrooms    INT           DEFAULT 0,
            bathrooms   INT           DEFAULT 0,
            area_sqft   FLOAT         DEFAULT 0,
            status      VARCHAR(30)   DEFAULT "Available",
            description TEXT,
            created_at  DATETIME      DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    print("✅ Table 'properties' created.")

    # Step 4: Seed only if empty
    cur.execute('SELECT COUNT(*) as cnt FROM properties')
    if cur.fetchone()['cnt'] == 0:
        demo = [
            ('Sunrise Villa',      'House',     'Mumbai',    '12 Marine Drive, Mumbai',       12500000, 4, 3, 2400,  'Available', 'Stunning sea-facing villa with modern interiors.'),
            ('Green Heights Apt',  'Apartment', 'Pune',      '45 Koregaon Park, Pune',         4800000, 2, 2,  950,  'Available', 'Cozy apartment in a prime gated society.'),
            ('Tech Park Studio',   'Apartment', 'Bengaluru', '7 Whitefield Road, Bengaluru',   3200000, 1, 1,  620,  'Rented',    'Perfect studio near IT corridor.'),
            ('Farm Land Plot',     'Land',      'Nashik',    'NH-60, Nashik Rural',            1500000, 0, 0, 10000, 'Available', 'Fertile agricultural land with road access.'),
            ('Alcove Gloria', 'House',     'kolkata',     '76/1 laketown, kolkata',     28000000, 5, 4, 3800,  'Sold',      'Luxury duplex in the heart of Delhi.'),
            ('sunrise apartment', 'House',     'kolkata',     '76/1 laketown, kolkata',     28000000, 5, 4, 3800,  'Sold',      'Luxury duplex in the heart of Delhi.'),
        ]
        cur.executemany(
            'INSERT INTO properties (title,type,city,address,price,bedrooms,bathrooms,area_sqft,status,description) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
            demo
        )
        conn.commit()
        print("✅ Seeded 5 demo properties.")
    else:
        print("ℹ️  Table already has data — skipping seed.")

    conn.close()
    print("\n🚀 All done! Now run:  python app.py")

if __name__ == '__main__':
    setup()
