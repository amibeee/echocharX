from flask import Blueprint, render_template, redirect, session, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import User, Client, Product, Order, OrderItem
from datetime import datetime

client_bp = Blueprint('client', __name__, url_prefix='/client')

@client_bp.before_request
def check_client():
    if not current_user.is_authenticated or not current_user.is_client():
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('auth.login'))

@client_bp.route('/dashboard')
@login_required
def dashboard():
    # Get client profile
    client = Client.query.filter_by(user_id=current_user.id).first()
    
    if not client:
        flash('Client profile not found!', 'danger')
        return redirect(url_for('auth.logout'))
    
    # Get recent orders
    recent_orders = Order.query.filter_by(client_id=client.id).order_by(Order.order_date.desc()).limit(5).all()
    
    return render_template(
        'client/dashboard.html',
        client=client,
        recent_orders=recent_orders
    )

@client_bp.route('/products')
@login_required
def products():
    client = Client.query.filter_by(user_id=current_user.id).first()
    
    if not client:
        flash('Client profile not found!', 'danger')
        return redirect(url_for('auth.logout'))
    
    # Get all products
    echo_coal_products = Product.query.filter_by(type='echo_coal').all()
    air_filter_products = Product.query.filter_by(type='filter', filter_type='air').all()
    water_filter_products = Product.query.filter_by(type='filter', filter_type='water').all()
    
    return render_template(
        'client/products.html',
        client=client,
        echo_coal_products=echo_coal_products,
        air_filter_products=air_filter_products,
        water_filter_products=water_filter_products
    )

@client_bp.route('/cart')
@login_required
def cart():
    client = Client.query.filter_by(user_id=current_user.id).first()
    
    if not client:
        flash('Client profile not found!', 'danger')
        return redirect(url_for('auth.logout'))
    
    # For simplicity, we'll use a session-based cart
    cart_items = session.get('cart', [])
    cart_products = []
    total = 0
    
    for item in cart_items:
        product = Product.query.get(item['product_id'])
        if product:
            subtotal = product.price * item['quantity']
            cart_products.append({
                'product': product,
                'quantity': item['quantity'],
                'subtotal': subtotal
            })
            total += subtotal
    
    return render_template(
        'client/cart.html',
        client=client,
        cart_products=cart_products,
        total=total
    )

@client_bp.route('/cart/add', methods=['POST'])
@login_required
def add_to_cart():
    client = Client.query.filter_by(user_id=current_user.id).first()
    
    if not client:
        flash('Client profile not found!', 'danger')
        return redirect(url_for('auth.logout'))
    
    product_id = int(request.form.get('product_id'))
    quantity = int(request.form.get('quantity', 1))
    
    # Check if product exists and has enough stock
    product = Product.query.get_or_404(product_id)
    if product.stock < quantity:
        flash(f'Sorry, only {product.stock} items available!', 'danger')
        return redirect(url_for('client.products'))
    
    # Initialize cart if it doesn't exist
    if 'cart' not in session:
        session['cart'] = []
    
    # Check if product already in cart
    cart = session['cart']
    found = False
    for item in cart:
        if item['product_id'] == product_id:
            item['quantity'] += quantity
            found = True
            break
    
    if not found:
        cart.append({
            'product_id': product_id,
            'quantity': quantity
        })
    
    session['cart'] = cart
    
    flash(f'{quantity} {product.name} added to cart!', 'success')
    return redirect(url_for('client.products'))

@client_bp.route('/cart/update', methods=['POST'])
@login_required
def update_cart():
    client = Client.query.filter_by(user_id=current_user.id).first()
    
    if not client:
        flash('Client profile not found!', 'danger')
        return redirect(url_for('auth.logout'))
    
    product_id = int(request.form.get('product_id'))
    quantity = int(request.form.get('quantity'))
    
    # Update cart
    cart = session.get('cart', [])
    for item in cart:
        if item['product_id'] == product_id:
            item['quantity'] = quantity
            break
    
    session['cart'] = cart
    
    flash('Cart updated!', 'success')
    return redirect(url_for('client.cart'))

@client_bp.route('/cart/remove', methods=['POST'])
@login_required
def remove_from_cart():
    client = Client.query.filter_by(user_id=current_user.id).first()
    
    if not client:
        flash('Client profile not found!', 'danger')
        return redirect(url_for('auth.logout'))
    
    product_id = int(request.form.get('product_id'))
    
    # Remove from cart
    cart = session.get('cart', [])
    cart = [item for item in cart if item['product_id'] != product_id]
    session['cart'] = cart
    
    flash('Item removed from cart!', 'success')
    return redirect(url_for('client.cart'))

@client_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    client = Client.query.filter_by(user_id=current_user.id).first()
    
    if not client:
        flash('Client profile not found!', 'danger')
        return redirect(url_for('auth.logout'))
    
    if request.method == 'POST':
        # Get cart items
        cart_items = session.get('cart', [])
        if not cart_items:
            flash('Your cart is empty!', 'danger')
            return redirect(url_for('client.products'))
        
        # Create order
        shipping_address = request.form.get('shipping_address')
        if not shipping_address:
            shipping_address = client.address
        
        order = Order(
            client_id=client.id,
            shipping_address=shipping_address,
            status='pending',
            total_amount=0  # We'll calculate this below
        )
        
        db.session.add(order)
        db.session.commit()
        
        # Add order items
        total_amount = 0
        for item in cart_items:
            product = Product.query.get(item['product_id'])
            if product and product.stock >= item['quantity']:
                subtotal = product.price * item['quantity']
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=item['quantity'],
                    unit_price=product.price,
                    subtotal=subtotal
                )
                
                # Update product stock
                product.stock -= item['quantity']
                
                db.session.add(order_item)
                total_amount += subtotal
            else:
                flash(f'Not enough stock for {product.name}!', 'danger')
                return redirect(url_for('client.cart'))
        
        # Update order total
        order.total_amount = total_amount
        db.session.commit()
        
        # Clear cart
        session['cart'] = []
        
        flash('Order placed successfully!', 'success')
        return redirect(url_for('client.orders'))
    
    # GET request - show checkout form
    cart_items = session.get('cart', [])
    cart_products = []
    total = 0
    
    for item in cart_items:
        product = Product.query.get(item['product_id'])
        if product:
            subtotal = product.price * item['quantity']
            cart_products.append({
                'product': product,
                'quantity': item['quantity'],
                'subtotal': subtotal
            })
            total += subtotal
    
    return render_template(
        'client/checkout.html',
        client=client,
        cart_products=cart_products,
        total=total
    )

@client_bp.route('/orders')
@login_required
def orders():
    client = Client.query.filter_by(user_id=current_user.id).first()
    
    if not client:
        flash('Client profile not found!', 'danger')
        return redirect(url_for('auth.logout'))
    
    # Get all orders for this client
    orders = Order.query.filter_by(client_id=client.id).order_by(Order.order_date.desc()).all()
    
    return render_template(
        'client/orders.html',
        client=client,
        orders=orders
    )

@client_bp.route('/order/<int:order_id>')
@login_required
def order_detail(order_id):
    client = Client.query.filter_by(user_id=current_user.id).first()
    
    if not client:
        flash('Client profile not found!', 'danger')
        return redirect(url_for('auth.logout'))
    
    # Get order
    order = Order.query.get_or_404(order_id)
    
    # Check if this order belongs to the client
    if order.client_id != client.id:
        flash('You do not have permission to view this order!', 'danger')
        return redirect(url_for('client.orders'))
    
    return render_template(
        'client/order_detail.html',
        client=client,
        order=order
    )