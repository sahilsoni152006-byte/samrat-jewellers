from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key'
app.config['UPLOAD_FOLDER'] = 'static/images/products'

def init_db():
    conn = sqlite3.connect('samrat_jewellers.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'user'
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        sku TEXT UNIQUE NOT NULL,
        category TEXT NOT NULL,
        description TEXT,
        price_type TEXT DEFAULT 'fixed',
        weight_in_grams REAL DEFAULT 0,
        base_price REAL NOT NULL,
        metal_type TEXT DEFAULT 'gold',
        purity TEXT DEFAULT '22K',
        image TEXT DEFAULT 'default.jpg',
        image_url TEXT,
        weight REAL DEFAULT 0,
        making_charges REAL DEFAULT 0,
        making_charges_type TEXT DEFAULT 'rupees',
        is_hidden INTEGER DEFAULT 0
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS metal_rates (
        id INTEGER PRIMARY KEY,
        metal TEXT UNIQUE NOT NULL,
        rate_per_gram REAL NOT NULL,
        source TEXT DEFAULT 'Manual',
        fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS settings (
        id INTEGER PRIMARY KEY,
        setting_key TEXT UNIQUE NOT NULL,
        setting_value TEXT
    )''')
    
    # Insert admin user
    admin_hash = generate_password_hash('admin123')
    c.execute('INSERT OR IGNORE INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)',
              ('Admin', 'admin@samratjewellers.com', admin_hash, 'admin'))
    
    # Insert metal rates
    c.execute('INSERT OR REPLACE INTO metal_rates (metal, rate_per_gram) VALUES (?, ?)',
              ('gold', 6500.0))
    c.execute('INSERT OR REPLACE INTO metal_rates (metal, rate_per_gram) VALUES (?, ?)',
              ('silver', 85.0))
    
    # Insert settings
    c.execute('INSERT OR REPLACE INTO settings (setting_key, setting_value) VALUES (?, ?)',
              ('whatsapp_number', '919999999999'))
    
    # Insert sample products
    products = [
        ('Gold Chain Necklace', 'GC001', 'Necklaces', 'Beautiful 22K gold chain', 'per_gram', 15.5, 0, 'gold', '22K', 'gold-chain.jpg', '', 15.5, 500, 'rupees', 0),
        ('Silver Earrings', 'SE001', 'Earrings', 'Elegant silver earrings', 'per_gram', 8.2, 0, 'silver', 'Silver', 'silver-earrings.jpg', '', 8.2, 10, 'percent', 0),
        ('Diamond Ring', 'DR001', 'Rings', 'Stunning diamond ring', 'fixed', 0, 45000, 'gold', '18K', 'diamond-ring.jpg', '', 5.0, 2000, 'rupees', 0)
    ]
    
    for product in products:
        c.execute('INSERT OR IGNORE INTO products (name, sku, category, description, price_type, weight_in_grams, base_price, metal_type, purity, image, image_url, weight, making_charges, making_charges_type, is_hidden) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', product)
    
    conn.commit()
    conn.close()

def get_db():
    return sqlite3.connect('samrat_jewellers.db')

def get_metal_rates():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM metal_rates')
    rates = c.fetchall()
    conn.close()
    
    rate_dict = {}
    for rate in rates:
        rate_dict[rate[1]] = {
            'rate_per_gram': rate[2],
            'source': rate[3],
            'fetched_at': rate[4]
        }
    return rate_dict

def calculate_price(product, rates):
    if product[5] == 'fixed':
        base_price = product[7]
        if product[14] == 'percent':
            making_cost = base_price * (product[13] / 100)
        else:
            making_cost = product[13]
        return round(base_price + making_cost, 2)
    elif product[5] == 'per_gram':
        metal = product[8]
        if metal in rates:
            base_rate = rates[metal]['rate_per_gram']
            metal_cost = base_rate * product[12]  # rate * weight
            if product[14] == 'percent':
                making_cost = metal_cost * (product[13] / 100)
            else:
                making_cost = product[13]
            return round(metal_cost + making_cost, 2)
    return product[7]

@app.route('/')
def home():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM products WHERE is_hidden = 0 ORDER BY id DESC LIMIT 10')
    products = c.fetchall()
    conn.close()
    
    rates = get_metal_rates()
    
    # Calculate prices
    product_list = []
    for product in products:
        product_dict = {
            'id': product[0], 'name': product[1], 'sku': product[2], 'category': product[3],
            'description': product[4], 'price_type': product[5], 'weight_in_grams': product[6],
            'base_price': product[7], 'metal_type': product[8], 'purity': product[9], 'image': product[10], 
            'image_url': product[11], 'weight': product[12], 'making_charges': product[13],
            'making_charges_type': product[14], 'calculated_price': calculate_price(product, rates)
        }
        product_list.append(product_dict)
    
    return render_template('home.html', products=product_list, rates=rates)

@app.route('/shop')
def shop():
    category = request.args.get('category', '')
    search = request.args.get('search', '')
    conn = get_db()
    c = conn.cursor()
    
    if search:
        c.execute('SELECT * FROM products WHERE name LIKE ? AND is_hidden = 0', (f'%{search}%',))
    elif category:
        c.execute('SELECT * FROM products WHERE category = ? AND is_hidden = 0', (category,))
    else:
        c.execute('SELECT * FROM products WHERE is_hidden = 0')
    
    products = c.fetchall()
    conn.close()
    
    rates = get_metal_rates()
    
    product_list = []
    for product in products:
        product_dict = {
            'id': product[0], 'name': product[1], 'sku': product[2], 'category': product[3],
            'description': product[4], 'price_type': product[5], 'weight_in_grams': product[6],
            'base_price': product[7], 'metal_type': product[8], 'purity': product[9], 'image': product[10],
            'image_url': product[11], 'weight': product[12], 'making_charges': product[13],
            'making_charges_type': product[14], 'calculated_price': calculate_price(product, rates)
        }
        product_list.append(product_dict)
    
    return render_template('shop.html', products=product_list, rates=rates, current_category=category)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM products WHERE id = ?', (product_id,))
    product = c.fetchone()
    c.execute('SELECT setting_value FROM settings WHERE setting_key = ?', ('whatsapp_number',))
    whatsapp = c.fetchone()
    conn.close()
    
    if not product:
        return redirect(url_for('shop'))
    
    rates = get_metal_rates()
    
    product_dict = {
        'id': product[0], 'name': product[1], 'sku': product[2], 'category': product[3],
        'description': product[4], 'price_type': product[5], 'weight_in_grams': product[6],
        'base_price': product[7], 'metal_type': product[8], 'purity': product[9], 'image': product[10],
        'image_url': product[11], 'weight': product[12], 'making_charges': product[13],
        'making_charges_type': product[14], 'calculated_price': calculate_price(product, rates)
    }
    
    whatsapp_number = whatsapp[0] if whatsapp else '919999999999'
    
    return render_template('product_detail.html', product=product_dict, rates=rates, whatsapp_number=whatsapp_number)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/wishlist')
def wishlist():
    return render_template('wishlist.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE email = ? AND role = ?', (email, 'admin'))
        user = c.fetchone()
        conn.close()
        
        if user and check_password_hash(user[3], password):
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('admin/login.html')

@app.route('/admin')
@app.route('/admin/')
def admin_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))
    
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM products')
    product_count = c.fetchone()[0]
    c.execute('SELECT * FROM products ORDER BY id DESC LIMIT 5')
    recent_products = c.fetchall()
    conn.close()
    
    rates = get_metal_rates()
    
    return render_template('admin/dashboard.html', product_count=product_count, recent_products=recent_products, rates=rates)

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/admin/products')
def admin_products():
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))
    
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM products ORDER BY id DESC')
    products = c.fetchall()
    conn.close()
    
    return render_template('admin/products.html', products=products)

@app.route('/admin/products/add', methods=['GET', 'POST'])
def admin_add_product():
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        name = request.form['name']
        sku = request.form['sku']
        category = request.form['category']
        description = request.form['description']
        price_type = request.form['price_type']
        weight_in_grams = float(request.form.get('weight_in_grams', 0))
        base_price = float(request.form.get('base_price', 0))
        metal_type = request.form['metal_type']
        image_url = request.form.get('image_url', '')
        weight = float(request.form.get('weight', 0))
        making_charges = float(request.form.get('making_charges', 0))
        is_hidden = 1 if request.form.get('is_hidden') else 0
        
        image = 'default.jpg'
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image = filename
        
        purity = request.form['purity']
        making_charges_type = request.form.get('making_charges_type', 'rupees')
        
        conn = get_db()
        c = conn.cursor()
        
        try:
            c.execute('''INSERT INTO products 
                        (name, sku, category, description, price_type, weight_in_grams, base_price, metal_type, purity, image, image_url, weight, making_charges, making_charges_type, is_hidden) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                     (name, sku, category, description, price_type, weight_in_grams, base_price, metal_type, purity, image, image_url, weight, making_charges, making_charges_type, is_hidden))
            conn.commit()
            flash('Product added successfully!', 'success')
        except sqlite3.IntegrityError:
            flash('SKU already exists!', 'error')
        
        conn.close()
        return redirect(url_for('admin_products'))
    
    return render_template('admin/add_product.html')

@app.route('/admin/products/edit/<int:product_id>', methods=['GET', 'POST'])
def admin_edit_product(product_id):
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))
    
    conn = get_db()
    c = conn.cursor()
    
    if request.method == 'POST':
        name = request.form['name']
        sku = request.form['sku']
        category = request.form['category']
        description = request.form['description']
        price_type = request.form['price_type']
        weight_in_grams = float(request.form.get('weight_in_grams', 0))
        base_price = float(request.form.get('base_price', 0))
        metal_type = request.form['metal_type']
        image_url = request.form.get('image_url', '')
        weight = float(request.form.get('weight', 0))
        making_charges = float(request.form.get('making_charges', 0))
        is_hidden = 1 if request.form.get('is_hidden') else 0
        
        c.execute('SELECT image FROM products WHERE id = ?', (product_id,))
        current_image = c.fetchone()[0]
        image = current_image
        
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image = filename
        
        purity = request.form['purity']
        making_charges_type = request.form.get('making_charges_type', 'rupees')
        
        c.execute('''UPDATE products SET 
                    name=?, sku=?, category=?, description=?, price_type=?, 
                    weight_in_grams=?, base_price=?, metal_type=?, purity=?, image=?, image_url=?, weight=?, making_charges=?, making_charges_type=?, is_hidden=? 
                    WHERE id=?''',
                 (name, sku, category, description, price_type, weight_in_grams, base_price, metal_type, purity, image, image_url, weight, making_charges, making_charges_type, is_hidden, product_id))
        conn.commit()
        conn.close()
        
        flash('Product updated successfully!', 'success')
        return redirect(url_for('admin_products'))
    
    c.execute('SELECT * FROM products WHERE id = ?', (product_id,))
    product = c.fetchone()
    conn.close()
    
    if not product:
        flash('Product not found!', 'error')
        return redirect(url_for('admin_products'))
    
    return render_template('admin/edit_product.html', product=product)

@app.route('/admin/products/delete/<int:product_id>')
def admin_delete_product(product_id):
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))
    
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM products WHERE id = ?', (product_id,))
    conn.commit()
    conn.close()
    
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('admin_products'))

@app.route('/admin/rates')
def admin_rates():
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))
    
    rates = get_metal_rates()
    return render_template('admin/rates.html', rates=rates)

@app.route('/admin/rates/update', methods=['POST'])
def admin_update_rates():
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))
    
    gold_rate = float(request.form['gold_rate'])
    silver_rate = float(request.form['silver_rate'])
    
    conn = get_db()
    c = conn.cursor()
    
    c.execute('UPDATE metal_rates SET rate_per_gram = ? WHERE metal = ?', 
              (gold_rate, 'gold'))
    c.execute('UPDATE metal_rates SET rate_per_gram = ? WHERE metal = ?', 
              (silver_rate, 'silver'))
    
    conn.commit()
    conn.close()
    
    flash('Metal rates updated successfully!', 'success')
    return redirect(url_for('admin_rates'))

@app.route('/admin/settings')
def admin_settings():
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))
    
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM settings')
    settings = c.fetchall()
    conn.close()
    
    settings_dict = {setting[1]: setting[2] for setting in settings}
    
    return render_template('admin/settings.html', settings=settings_dict)

@app.route('/admin/settings/update', methods=['POST'])
def admin_update_settings():
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))
    
    whatsapp_number = request.form['whatsapp_number']
    
    conn = get_db()
    c = conn.cursor()
    
    c.execute('UPDATE settings SET setting_value = ? WHERE setting_key = ?', 
              (whatsapp_number, 'whatsapp_number'))
    
    conn.commit()
    conn.close()
    
    flash('Settings updated successfully!', 'success')
    return redirect(url_for('admin_settings'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True,port=5001)