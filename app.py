from flask import Flask, render_template, request, redirect, url_for, flash, session
import firebase_admin
from firebase_admin import credentials, db
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import uuid

app = Flask(__name__)
app.secret_key = 'your-secret-key'
app.config['UPLOAD_FOLDER'] = 'static/images/products'

# Initialize Firebase
cred = credentials.Certificate('firebase_config.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://samrat-4d6b3-default-rtdb.firebaseio.com/'
})

def init_firebase():
    # Check if database is already initialized
    existing_users = db.reference('users').get()
    if existing_users:
        print("Database already initialized, skipping setup...")
        return
    
    print("Initializing Firebase database...")
    
    # Initialize admin user
    admin_hash = generate_password_hash('samrat@2024')
    admin_data = {
        'name': 'Samrat Admin',
        'email': 'samrat@samratjewellers.com',
        'password_hash': admin_hash,
        'role': 'admin'
    }
    db.reference('users').child('samrat_admin').set(admin_data)
    
    # Initialize metal rates
    rates_data = {
        'gold': {'rate_per_gram': 6500.0, 'source': 'Manual', 'fetched_at': datetime.now().isoformat()},
        'silver': {'rate_per_gram': 85.0, 'source': 'Manual', 'fetched_at': datetime.now().isoformat()}
    }
    db.reference('metal_rates').set(rates_data)
    
    # Initialize settings
    settings_data = {'whatsapp_number': '919999999999'}
    db.reference('settings').set(settings_data)
    
    print("Firebase database initialized successfully!")

def get_metal_rates():
    rates_ref = db.reference('metal_rates')
    rates = rates_ref.get() or {}
    return rates

def convert_google_drive_url(url):
    """Convert Google Drive share URL to direct image URL"""
    if not url:
        return url
    
    # Handle different Google Drive URL formats
    if 'drive.google.com' in url:
        if '/file/d/' in url:
            # Extract file ID from sharing URL
            file_id = url.split('/file/d/')[1].split('/')[0]
            return f'https://lh3.googleusercontent.com/d/{file_id}'
        elif 'id=' in url:
            # Already in direct format, return as is
            return url
    
    return url

def calculate_price(product, rates):
    if product['price_type'] == 'fixed':
        base_price = product['base_price']
        if product['making_charges_type'] == 'percent':
            making_cost = base_price * (product['making_charges'] / 100)
        else:
            making_cost = product['making_charges']
        return round(base_price + making_cost, 2)
    elif product['price_type'] == 'per_gram':
        metal = product['metal_type']
        if metal in rates:
            base_rate = rates[metal]['rate_per_gram']
            metal_cost = base_rate * product['weight']
            if product['making_charges_type'] == 'percent':
                making_cost = metal_cost * (product['making_charges'] / 100)
            else:
                making_cost = product['making_charges']
            return round(metal_cost + making_cost, 2)
    return product['base_price']

@app.route('/')
def home():
    products_ref = db.reference('products')
    all_products = products_ref.get() or {}
    
    # Filter visible products and get latest 10
    products = []
    for key, product in all_products.items():
        if not product.get('is_hidden', False):
            product['id'] = key
            products.append(product)
    
    products = sorted(products, key=lambda x: x.get('name', ''), reverse=True)[:10]
    rates = get_metal_rates()
    
    # Calculate prices and convert Google Drive URLs
    for product in products:
        product['calculated_price'] = calculate_price(product, rates)
        if product.get('image_url'):
            product['image_url'] = convert_google_drive_url(product['image_url'])
    
    # Get only specific categories
    categories_ref = db.reference('categories')
    categories_data = categories_ref.get() or {}
    
    # Only show these 4 categories
    allowed_categories = ['earrings', 'chains', 'rings', 'necklaces']
    categories = []
    
    for cat_id in allowed_categories:
        if cat_id in categories_data and not categories_data[cat_id].get('is_hidden', False):
            category = {
                'id': cat_id,
                'name': categories_data[cat_id]['name'],
                'image_url': convert_google_drive_url(categories_data[cat_id].get('image_url', ''))
            }
            categories.append(category)
        else:
            # Fallback for missing categories
            category = {
                'id': cat_id,
                'name': cat_id.title(),
                'image_url': ''
            }
            categories.append(category)
    
    return render_template('home.html', products=products, rates=rates, categories=categories)

@app.route('/shop')
def shop():
    category = request.args.get('category', '')
    search = request.args.get('search', '')
    metal = request.args.get('metal', '')
    price_range = request.args.get('price', '')
    sort_by = request.args.get('sort', '')
    
    products_ref = db.reference('products')
    all_products = products_ref.get() or {}
    
    products = []
    for key, product in all_products.items():
        if not product.get('is_hidden', False):
            product['id'] = key
            
            # Enhanced search - name, sku, category, description
            if search:
                search_lower = search.lower()
                searchable_text = f"{product.get('name', '')} {product.get('sku', '')} {product.get('category', '')} {product.get('description', '')}".lower()
                if search_lower not in searchable_text:
                    continue
            
            # Category filter
            if category and product.get('category') != category:
                continue
            
            # Metal filter
            if metal and product.get('metal_type', '').lower() != metal.lower():
                continue
                
            products.append(product)
    
    rates = get_metal_rates()
    
    # Calculate prices and convert Google Drive URLs
    for product in products:
        product['calculated_price'] = calculate_price(product, rates)
        if product.get('image_url'):
            product['image_url'] = convert_google_drive_url(product['image_url'])
    
    # Price range filter (after price calculation)
    if price_range and '-' in price_range:
        min_price, max_price = map(float, price_range.split('-'))
        products = [p for p in products if min_price <= p['calculated_price'] <= max_price]
    
    # Sorting
    if sort_by == 'name':
        products.sort(key=lambda x: x.get('name', ''))
    elif sort_by == 'price-low':
        products.sort(key=lambda x: x['calculated_price'])
    elif sort_by == 'price-high':
        products.sort(key=lambda x: x['calculated_price'], reverse=True)
    elif sort_by == 'category':
        products.sort(key=lambda x: x.get('category', ''))
    
    # Get categories from Firebase
    categories_ref = db.reference('categories')
    categories_data = categories_ref.get() or {}
    
    categories = []
    for cat_id, cat_data in categories_data.items():
        if not cat_data.get('is_hidden', False):
            categories.append({'name': cat_data['name']})
    
    return render_template('shop.html', products=products, rates=rates, categories=categories, current_category=category, current_search=search, current_metal=metal, current_price=price_range)

@app.route('/product/<product_id>')
def product_detail(product_id):
    product_ref = db.reference(f'products/{product_id}')
    product = product_ref.get()
    
    if not product:
        return redirect(url_for('shop'))
    
    product['id'] = product_id
    rates = get_metal_rates()
    product['calculated_price'] = calculate_price(product, rates)
    
    # Convert Google Drive URL if present
    if product.get('image_url'):
        product['image_url'] = convert_google_drive_url(product['image_url'])
    
    settings_ref = db.reference('settings')
    settings = settings_ref.get() or {}
    whatsapp_number = settings.get('whatsapp_number', '919999999999')
    
    return render_template('product_detail.html', product=product, rates=rates, whatsapp_number=whatsapp_number)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/wishlist')
def wishlist():
    if 'user_mobile' not in session:
        return redirect(url_for('profile'))
    
    user_mobile = session['user_mobile']
    wishlist_ref = db.reference(f'wishlists/{user_mobile}')
    wishlist_items = wishlist_ref.get() or {}
    
    products = []
    rates = get_metal_rates()
    
    for product_id in wishlist_items.keys():
        product_ref = db.reference(f'products/{product_id}')
        product = product_ref.get()
        if product and not product.get('is_hidden', False):
            product['id'] = product_id
            product['calculated_price'] = calculate_price(product, rates)
            if product.get('image_url'):
                product['image_url'] = convert_google_drive_url(product['image_url'])
            products.append(product)
    
    return render_template('wishlist.html', products=products)

@app.route('/wishlist/add/<product_id>', methods=['POST'])
def add_to_wishlist(product_id):
    if 'user_mobile' not in session:
        return {'success': False, 'message': 'Please login first'}
    
    user_mobile = session['user_mobile']
    wishlist_ref = db.reference(f'wishlists/{user_mobile}/{product_id}')
    wishlist_ref.set({'added_at': datetime.now().isoformat()})
    
    return {'success': True}

@app.route('/wishlist/remove/<product_id>', methods=['POST'])
def remove_from_wishlist(product_id):
    if 'user_mobile' not in session:
        return {'success': False, 'message': 'Please login first'}
    
    user_mobile = session['user_mobile']
    wishlist_ref = db.reference(f'wishlists/{user_mobile}/{product_id}')
    wishlist_ref.delete()
    
    return {'success': True}

@app.route('/wishlist/check/<product_id>')
def check_wishlist(product_id):
    if 'user_mobile' not in session:
        return {'in_wishlist': False}
    
    user_mobile = session['user_mobile']
    wishlist_ref = db.reference(f'wishlists/{user_mobile}/{product_id}')
    exists = wishlist_ref.get() is not None
    
    return {'in_wishlist': exists}

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/check-user', methods=['POST'])
def check_user():
    data = request.get_json()
    mobile = data.get('mobile')
    
    users_ref = db.reference('customers')
    users = users_ref.get() or {}
    
    exists = any(user.get('mobile') == mobile for user in users.values())
    return {'exists': exists}

@app.route('/user-login', methods=['POST'])
def user_login():
    mobile = request.form['mobile']
    name = request.form.get('name', '')
    
    users_ref = db.reference('customers')
    users = users_ref.get() or {}
    
    # Find existing user
    user = None
    user_id = None
    for uid, user_data in users.items():
        if user_data.get('mobile') == mobile:
            user = user_data
            user_id = uid
            break
    
    if user:
        # Login existing user
        session['user_mobile'] = mobile
        session['user_name'] = user['name']
        session['user_registered'] = user['registered_date']
        flash('Welcome back!', 'success')
    else:
        # Register new user
        if not name:
            flash('Name is required for new registration', 'error')
            return redirect(url_for('profile'))
        
        user_id = mobile
        user_data = {
            'name': name,
            'mobile': mobile,
            'registered_date': datetime.now().strftime('%Y-%m-%d'),
            'registered_at': datetime.now().isoformat()
        }
        
        users_ref.child(user_id).set(user_data)
        
        session['user_mobile'] = mobile
        session['user_name'] = name
        session['user_registered'] = user_data['registered_date']
        flash('Registration successful!', 'success')
    
    return redirect(url_for('profile'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('home'))

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        users_ref = db.reference('users')
        users = users_ref.get() or {}
        
        user = None
        for key, user_data in users.items():
            if user_data.get('email') == email and user_data.get('role') == 'admin':
                user = user_data
                user['id'] = key
                break
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('admin/login.html')

@app.route('/admin')
@app.route('/admin/')
def admin_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))
    
    products_ref = db.reference('products')
    all_products = products_ref.get() or {}
    
    product_count = len(all_products)
    recent_products = []
    for key, product in list(all_products.items())[-5:]:
        product['sku'] = key
        recent_products.append(product)
    
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
    
    products_ref = db.reference('products')
    all_products = products_ref.get() or {}
    
    products = []
    for key, product in all_products.items():
        product['id'] = key
        products.append(product)
    
    return render_template('admin/products_firebase.html', products=products)

@app.route('/admin/products/add', methods=['GET', 'POST'])
def admin_add_product():
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        weight_value = float(request.form.get('weight', 0))
        product_data = {
            'name': request.form['name'],
            'sku': request.form['sku'],
            'category': request.form['category'],
            'description': request.form['description'],
            'price_type': request.form['price_type'],
            'weight_in_grams': weight_value,
            'base_price': float(request.form.get('base_price', 0)),
            'metal_type': request.form['metal_type'],
            'purity': request.form['purity'],
            'image_url': request.form.get('image_url', ''),
            'weight': weight_value,
            'making_charges': float(request.form.get('making_charges', 0)),
            'making_charges_type': request.form.get('making_charges_type', 'rupees'),
            'is_hidden': bool(request.form.get('is_hidden'))
        }
        
        # Handle image upload
        image = 'default.jpg'
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image = filename
        
        product_data['image'] = image
        
        # Check if SKU exists
        products_ref = db.reference('products')
        all_products = products_ref.get() or {}
        
        sku_exists = any(p.get('sku') == product_data['sku'] for p in all_products.values())
        
        if sku_exists:
            flash('SKU already exists!', 'error')
        else:
            # Use SKU as key
            products_ref.child(product_data['sku']).set(product_data)
            flash('Product added successfully!', 'success')
        
        return redirect(url_for('admin_products'))
    
    return render_template('admin/add_product.html')

@app.route('/admin/products/edit/<product_id>', methods=['GET', 'POST'])
def admin_edit_product(product_id):
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))
    
    product_ref = db.reference(f'products/{product_id}')
    product = product_ref.get()
    
    if not product:
        flash('Product not found!', 'error')
        return redirect(url_for('admin_products'))
    
    if request.method == 'POST':
        weight_value = float(request.form.get('weight', 0))
        product_data = {
            'name': request.form['name'],
            'sku': request.form['sku'],
            'category': request.form['category'],
            'description': request.form['description'],
            'price_type': request.form['price_type'],
            'weight_in_grams': weight_value,
            'base_price': float(request.form.get('base_price', 0)),
            'metal_type': request.form['metal_type'],
            'purity': request.form['purity'],
            'image_url': request.form.get('image_url', ''),
            'weight': weight_value,
            'making_charges': float(request.form.get('making_charges', 0)),
            'making_charges_type': request.form.get('making_charges_type', 'rupees'),
            'is_hidden': bool(request.form.get('is_hidden'))
        }
        
        # Handle image upload
        image = product.get('image', 'default.jpg')
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image = filename
        
        product_data['image'] = image
        
        # Update product
        product_ref.update(product_data)
        flash('Product updated successfully!', 'success')
        return redirect(url_for('admin_products'))
    
    product['id'] = product_id
    return render_template('admin/edit_product_firebase.html', product=product)

@app.route('/admin/products/delete/<product_id>')
def admin_delete_product(product_id):
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))
    
    product_ref = db.reference(f'products/{product_id}')
    product_ref.delete()
    
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
    
    rates_ref = db.reference('metal_rates')
    current_time = datetime.now().isoformat()
    
    # Update rates with proper structure
    rates_ref.set({
        'gold': {
            'rate_per_gram': gold_rate,
            'fetched_at': current_time,
            'source': 'Manual'
        },
        'silver': {
            'rate_per_gram': silver_rate,
            'fetched_at': current_time,
            'source': 'Manual'
        }
    })
    
    flash('Metal rates updated successfully!', 'success')
    return redirect(url_for('admin_rates'))

@app.route('/admin/settings')
def admin_settings():
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))
    
    settings_ref = db.reference('settings')
    settings = settings_ref.get() or {}
    
    return render_template('admin/settings.html', settings=settings)

@app.route('/admin/settings/update', methods=['POST'])
def admin_update_settings():
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))
    
    whatsapp_number = request.form['whatsapp_number']
    
    settings_ref = db.reference('settings')
    settings_ref.update({'whatsapp_number': whatsapp_number})
    
    flash('Settings updated successfully!', 'success')
    return redirect(url_for('admin_settings'))

@app.route('/admin/users')
def admin_users():
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))
    
    users_ref = db.reference('customers')
    users = users_ref.get() or {}
    
    return render_template('admin/users.html', users=users)

@app.route('/admin/categories')
def admin_categories():
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))
    
    categories_ref = db.reference('categories')
    categories_data = categories_ref.get() or {}
    
    # Default categories if none exist
    if not categories_data:
        default_categories = {
            'necklaces': {'name': 'Necklaces', 'is_hidden': False},
            'rings': {'name': 'Rings', 'is_hidden': False},
            'earrings': {'name': 'Earrings', 'is_hidden': False},
            'bracelets': {'name': 'Bracelets', 'is_hidden': False},
            'pendants': {'name': 'Pendants', 'is_hidden': False},
            'chains': {'name': 'Chains', 'is_hidden': False}
        }
        categories_ref.set(default_categories)
        categories_data = default_categories
    
    # Convert to list format
    categories = []
    for cat_id, cat_data in categories_data.items():
        category = {
            'id': cat_id,
            'name': cat_data['name'],
            'is_hidden': cat_data.get('is_hidden', False),
            'image_url': convert_google_drive_url(cat_data.get('image_url', '')),
            'product_count': 0
        }
        categories.append(category)
    
    return render_template('admin/categories.html', categories=categories)

@app.route('/admin/categories/toggle/<category_id>', methods=['POST'])
def admin_toggle_category(category_id):
    if 'user_id' not in session:
        return {'success': False}, 401
    
    category_ref = db.reference(f'categories/{category_id}')
    category = category_ref.get()
    
    if category:
        new_status = not category.get('is_hidden', False)
        category_ref.update({'is_hidden': new_status})
        return {'success': True}
    
    return {'success': False}

@app.route('/admin/categories/add', methods=['POST'])
def admin_add_category():
    if 'user_id' not in session:
        return {'success': False}, 401
    
    data = request.get_json()
    name = data.get('name', '').strip()
    image_url = data.get('image_url', '').strip()
    
    if not name:
        return {'success': False, 'message': 'Category name is required'}
    
    category_id = name.lower().replace(' ', '_')
    category_ref = db.reference(f'categories/{category_id}')
    
    if category_ref.get():
        return {'success': False, 'message': 'Category already exists'}
    
    category_ref.set({'name': name, 'is_hidden': False, 'image_url': image_url})
    return {'success': True}

@app.route('/admin/categories/edit/<category_id>', methods=['POST'])
def admin_edit_category(category_id):
    if 'user_id' not in session:
        return {'success': False}, 401
    
    data = request.get_json()
    name = data.get('name', '').strip()
    image_url = data.get('image_url', '').strip()
    
    if not name:
        return {'success': False, 'message': 'Category name is required'}
    
    category_ref = db.reference(f'categories/{category_id}')
    category_ref.update({'name': name, 'image_url': image_url})
    return {'success': True}

@app.route('/admin/categories/delete/<category_id>', methods=['POST'])
def admin_delete_category(category_id):
    if 'user_id' not in session:
        return {'success': False}, 401
    
    category_ref = db.reference(f'categories/{category_id}')
    category_ref.delete()
    return {'success': True}

@app.route('/admin/products/toggle/<product_id>', methods=['POST'])
def admin_toggle_product(product_id):
    if 'user_id' not in session:
        return {'success': False}, 401
    
    product_ref = db.reference(f'products/{product_id}')
    product = product_ref.get()
    
    if product:
        new_status = not product.get('is_hidden', False)
        product_ref.update({'is_hidden': new_status})
        return {'success': True}
    
    return {'success': False}

if __name__ == '__main__':
    init_firebase()
    app.run(debug=True, port=5001)