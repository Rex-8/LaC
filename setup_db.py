import sqlite3

conn = sqlite3.connect('ecommerce.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    price REAL NOT NULL,
    color TEXT,
    category TEXT,
    image_url TEXT,
    stock INTEGER DEFAULT 0
)''')

c.execute('''CREATE TABLE IF NOT EXISTS cart (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER DEFAULT 1,
    size TEXT,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id)
)''')

c.execute('''CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    total_amount REAL NOT NULL,
    status TEXT DEFAULT 'pending',
    shipping_address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)''')

c.execute('''CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    size TEXT,
    price REAL NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
)''')

products = [
    ('Blue Denim Jacket', 'Classic blue denim jacket', 89.99, 'blue', 'jackets', 'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=400', 15),
    ('Navy Blue Jacket', 'Water-resistant navy jacket', 129.99, 'blue', 'jackets', 'https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=400', 8),
    ('Light Blue Bomber', 'Casual light blue bomber jacket', 99.99, 'blue', 'jackets', 'https://images.unsplash.com/photo-1521223890158-f9f7c3d5d5d504?w=400', 12),
    ('Black Hoodie', 'Comfortable black hoodie', 49.99, 'black', 'hoodies', 'https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=400', 20),
    ('Gray Hoodie', 'Soft gray hoodie with pocket', 54.99, 'gray', 'hoodies', 'https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?w=400', 18),
    ('White T-Shirt', 'Basic white cotton tee', 19.99, 'white', 'tshirts', 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400', 30),
    ('Black T-Shirt', 'Classic black tee', 19.99, 'black', 'tshirts', 'https://images.unsplash.com/photo-1583743814966-8936f5b7be1a?w=400', 25),
    ('Red Jacket', 'Bold red winter jacket', 149.99, 'red', 'jackets', 'https://images.unsplash.com/photo-1548126032-079346d0e327?w=400', 6),
]

c.executemany('INSERT INTO products (name, description, price, color, category, image_url, stock) VALUES (?, ?, ?, ?, ?, ?, ?)', products)

conn.commit()
conn.close()

print("Database setup complete!")