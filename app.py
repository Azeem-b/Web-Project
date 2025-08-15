from flask import Flask, render_template, request, redirect, session, url_for, flash, send_from_directory
from users import users
from products import products  # Your products list/dict with 'id', 'name', 'price', 'image'

app = Flask(__name__)
app.secret_key = 'secret123'  # required for session & flash

# Serve static files
@app.route('/<filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email in users and users[email] == password:
            session['user'] = email
            return redirect('/products')
        else:
            flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        users[email] = password
        flash('Signup successful! Please log in.', 'success')
        return redirect('/login')
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('cart', None)
    return redirect('/')

@app.route('/products')
def show_products():
    if 'user' not in session:
        return redirect('/login')
    return render_template('products.html', products=products)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    if 'user' not in session:
        flash('Please log in first to add products to the cart.', 'warning')
        return redirect('/login')

    if 'cart' not in session:
        session['cart'] = []

    # Check product exists
    if not any(p['id'] == product_id for p in products):
        flash('Product not found.', 'danger')
        return redirect('/products')

    # Check if product already in cart
    exists = False
    for item in session['cart']:
        if item['id'] == product_id:
            exists = True
            break

    if not exists:
        # Add new product with default qty and color
        session['cart'].append({'id': product_id, 'quantity': 1, 'color': 'Default'})
        session.modified = True
        flash('Product added to cart!', 'success')
    else:
        flash('Product already in cart.', 'info')

    return redirect('/products')

@app.route('/cart', methods=['GET', 'POST'])
def cart():
    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':
        # Update quantities and colors
        for item in session.get('cart', []):
            qty_key = f"qty_{item['id']}"
            color_key = f"color_{item['id']}"
            if qty_key in request.form:
                item['quantity'] = int(request.form[qty_key])
            if color_key in request.form:
                item['color'] = request.form[color_key]
        session.modified = True
        flash('Cart updated!', 'success')
        return redirect('/cart')

    cart_products = []
    for item in session.get('cart', []):
        product = next((p for p in products if p['id'] == item['id']), None)
        if product:
            prod_copy = product.copy()
            prod_copy['quantity'] = item['quantity']
            prod_copy['color'] = item['color']
            prod_copy['total_price'] = prod_copy['price'] * prod_copy['quantity']  # Calculate total
            cart_products.append(prod_copy)

    return render_template('cart.html', products=cart_products)


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        phone = request.form['phone']
        # Here: you could save order to DB or process payment
        session.pop('cart', None)  # clear cart after order
        flash(f'Thank you {name}, your order has been placed!', 'success')
        return redirect('/')

    cart_products = []
    for item in session.get('cart', []):
        product = next((p for p in products if p['id'] == item['id']), None)
        if product:
            prod_copy = product.copy()
            prod_copy['quantity'] = item['quantity']
            prod_copy['color'] = item['color']
            cart_products.append(prod_copy)

    return render_template('checkout.html', products=cart_products)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect('/login')
    return render_template('profile.html', user=session['user'])

if __name__ == '__main__':
    app.run(debug=True)
