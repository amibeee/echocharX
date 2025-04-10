from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import (
    User, Supplier, Client, RawMaterial, Product, Inventory,
    Supply, Negotiation, NegotiationMessage, Production, Order
)
import json
from datetime import datetime, timedelta
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.before_request
def check_admin():
    if not current_user.is_authenticated or not current_user.is_admin():
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('auth.login'))

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    # Get counts for dashboard
    suppliers_count = Supplier.query.count()
    clients_count = Client.query.count()
    raw_materials_count = RawMaterial.query.count()
    products_count = Product.query.count()
    orders_count = Order.query.count()
    pending_negotiations = Negotiation.query.filter_by(status='in_progress').count()
    
    # Get recent orders
    recent_orders = Order.query.order_by(Order.order_date.desc()).limit(5).all()
    
    # Get inventory levels
    inventory = Inventory.query.first()
    if not inventory:
        inventory = Inventory()
        db.session.add(inventory)
        db.session.commit()
    
    # Get raw material levels
    raw_materials = RawMaterial.query.all()
    
    # Get product stock levels
    products = Product.query.all()
    
    # Get pending supplies
    pending_supplies = Supply.query.filter_by(status='pending').all()
    
    # Get sales data for chart
    orders = Order.query.filter(
        Order.order_date >= datetime.utcnow().replace(day=1)
    ).all()
    
    # Prepare sales data by day
    sales_data = {}
    for order in orders:
        day = order.order_date.day
        if day not in sales_data:
            sales_data[day] = 0
        sales_data[day] += order.total_amount
    
    # Convert to list for chart
    sales_chart_data = [{"day": day, "amount": amount} for day, amount in sales_data.items()]
    
    return render_template(
        'admin/dashboard.html',
        suppliers_count=suppliers_count,
        clients_count=clients_count,
        raw_materials_count=raw_materials_count,
        products_count=products_count,
        orders_count=orders_count,
        pending_negotiations=pending_negotiations,
        recent_orders=recent_orders,
        raw_materials=raw_materials,
        products=products,
        pending_supplies=pending_supplies,
        sales_chart_data=json.dumps(sales_chart_data)
    )

@admin_bp.route('/inventory')
@login_required
def inventory():
    inventory = Inventory.query.first()
    if not inventory:
        inventory = Inventory()
        db.session.add(inventory)
        db.session.commit()
    
    raw_materials = RawMaterial.query.all()
    products = Product.query.all()
    
    return render_template(
        'admin/inventory.html',
        inventory=inventory,
        raw_materials=raw_materials,
        products=products
    )

@admin_bp.route('/raw-material/add', methods=['POST'])
@login_required
def add_raw_material():
    name = request.form.get('name')
    material_type = request.form.get('type')
    description = request.form.get('description')
    
    inventory = Inventory.query.first()
    if not inventory:
        inventory = Inventory()
        db.session.add(inventory)
        db.session.commit()
    
    raw_material = RawMaterial(
        name=name,
        type=material_type,
        description=description,
        inventory_id=inventory.id
    )
    
    db.session.add(raw_material)
    db.session.commit()
    
    flash('Raw material added successfully!', 'success')
    return redirect(url_for('admin.inventory'))

@admin_bp.route('/product/add', methods=['POST'])
@login_required
def add_product():
    name = request.form.get('name')
    product_type = request.form.get('type')
    filter_type = request.form.get('filter_type') if product_type == 'filter' else None
    description = request.form.get('description')
    price = request.form.get('price')
    stock = request.form.get('stock', 0)
    image_url = request.form.get('image_url')
    
    inventory = Inventory.query.first()
    if not inventory:
        inventory = Inventory()
        db.session.add(inventory)
        db.session.commit()
    
    product = Product(
        name=name,
        type=product_type,
        filter_type=filter_type,
        description=description,
        price=float(price),
        stock=int(stock),
        image_url=image_url,
        inventory_id=inventory.id
    )
    
    db.session.add(product)
    db.session.commit()
    
    flash('Product added successfully!', 'success')
    return redirect(url_for('admin.inventory'))

@admin_bp.route('/suppliers')
@login_required
def suppliers():
    suppliers = Supplier.query.all()
    raw_materials = RawMaterial.query.all()
    
    return render_template(
        'admin/suppliers.html',
        suppliers=suppliers,
        raw_materials=raw_materials
    )

@admin_bp.route('/supplier/<int:supplier_id>')
@login_required
def supplier_detail(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)
    supplies = Supply.query.filter_by(supplier_id=supplier_id).order_by(Supply.created_at.desc()).all()
    negotiations = Negotiation.query.filter_by(supplier_id=supplier_id).order_by(Negotiation.created_at.desc()).all()
    raw_materials = RawMaterial.query.all()
    
    return render_template(
        'admin/supplier_detail.html',
        supplier=supplier,
        supplies=supplies,
        negotiations=negotiations,
        raw_materials=raw_materials
    )

@admin_bp.route('/negotiation/start', methods=['POST'])
@login_required
def start_negotiation():
    supplier_id = request.form.get('supplier_id')
    raw_material_id = request.form.get('raw_material_id')
    initial_price = request.form.get('initial_price')
    target_price = request.form.get('target_price')
    
    negotiation = Negotiation(
        supplier_id=supplier_id,
        raw_material_id=raw_material_id,
        initial_price=float(initial_price),
        current_price=float(initial_price),
        target_price=float(target_price),
        status='in_progress'
    )
    
    db.session.add(negotiation)
    db.session.commit()
    
    message = NegotiationMessage(
        negotiation_id=negotiation.id,
        sender_id=current_user.id,
        message=f"Starting negotiation for raw material. Our target price is ${target_price} per unit."
    )
    
    db.session.add(message)
    db.session.commit()
    
    flash('Negotiation started successfully!', 'success')
    return redirect(url_for('admin.supplier_detail', supplier_id=supplier_id))

@admin_bp.route('/negotiation/<int:negotiation_id>/message', methods=['POST'])
@login_required
def add_negotiation_message(negotiation_id):
    negotiation = Negotiation.query.get_or_404(negotiation_id)
    message_text = request.form.get('message')
    
    message = NegotiationMessage(
        negotiation_id=negotiation_id,
        sender_id=current_user.id,
        message=message_text
    )
    
    db.session.add(message)
    db.session.commit()
    
    return redirect(url_for('admin.supplier_detail', supplier_id=negotiation.supplier_id))

@admin_bp.route('/negotiation/<int:negotiation_id>/complete', methods=['POST'])
@login_required
def complete_negotiation(negotiation_id):
    negotiation = Negotiation.query.get_or_404(negotiation_id)
    status = request.form.get('status')
    
    negotiation.status = status
    negotiation.completed_at = datetime.utcnow()
    
    db.session.commit()
    
    message = NegotiationMessage(
        negotiation_id=negotiation_id,
        sender_id=current_user.id,
        message=f"Negotiation {status}. Final price: ${negotiation.current_price}"
    )
    
    db.session.add(message)
    db.session.commit()
    
    flash(f'Negotiation marked as {status}!', 'success')
    return redirect(url_for('admin.supplier_detail', supplier_id=negotiation.supplier_id))

@admin_bp.route('/supply/confirm/<int:supply_id>', methods=['POST'])
@login_required
def confirm_supply(supply_id):
    supply = Supply.query.get_or_404(supply_id)
    supply.status = 'confirmed'
    
    db.session.commit()
    
    flash('Supply confirmed successfully!', 'success')
    return redirect(url_for('admin.supplier_detail', supplier_id=supply.supplier_id))

@admin_bp.route('/supply/receive/<int:supply_id>', methods=['POST'])
@login_required
def receive_supply(supply_id):
    supply = Supply.query.get_or_404(supply_id)
    supply.status = 'delivered'
    supply.delivered_at = datetime.utcnow()
    
    # Update inventory
    raw_material = RawMaterial.query.get(supply.raw_material_id)
    if raw_material:
        # Add to inventory here (assuming we have a quantity field for raw materials)
        # For simplicity, we're just marking it as delivered
        pass
    
    db.session.commit()
    
    flash('Supply marked as delivered!', 'success')
    return redirect(url_for('admin.supplier_detail', supplier_id=supply.supplier_id))

@admin_bp.route('/production')
@login_required
def production():
    productions = Production.query.order_by(Production.start_date.desc()).all()
    products = Product.query.all()
    raw_materials = RawMaterial.query.filter_by(type='date_kernel').all()
    
    return render_template(
        'admin/production.html',
        productions=productions,
        products=products,
        raw_materials=raw_materials
    )

@admin_bp.route('/production/add', methods=['POST'])
@login_required
def add_production():
    product_id = request.form.get('product_id')
    quantity = request.form.get('quantity')
    raw_material_used = request.form.get('raw_material_used')
    notes = request.form.get('notes')
    
    production = Production(
        product_id=product_id,
        quantity=int(quantity),
        raw_material_used=float(raw_material_used),
        status='planned',
        notes=notes
    )
    
    db.session.add(production)
    db.session.commit()
    
    flash('Production plan added successfully!', 'success')
    return redirect(url_for('admin.production'))

@admin_bp.route('/production/<int:production_id>/start', methods=['POST'])
@login_required
def start_production(production_id):
    production = Production.query.get_or_404(production_id)
    production.status = 'in_progress'
    production.start_date = datetime.utcnow()
    
    db.session.commit()
    
    flash('Production started successfully!', 'success')
    return redirect(url_for('admin.production'))

@admin_bp.route('/production/<int:production_id>/complete', methods=['POST'])
@login_required
def complete_production(production_id):
    production = Production.query.get_or_404(production_id)
    production.status = 'completed'
    production.end_date = datetime.utcnow()
    
    # Update product stock
    product = Product.query.get(production.product_id)
    if product:
        product.stock += production.quantity
    
    db.session.commit()
    
    flash('Production completed successfully!', 'success')
    return redirect(url_for('admin.production'))

@admin_bp.route('/orders')
@login_required
def orders():
    orders = Order.query.order_by(Order.order_date.desc()).all()
    
    return render_template(
        'admin/orders.html',
        orders=orders
    )

@admin_bp.route('/order/<int:order_id>')
@login_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    
    return render_template(
        'admin/order_detail.html',
        order=order
    )

@admin_bp.route('/order/<int:order_id>/update-status', methods=['POST'])
@login_required
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    status = request.form.get('status')
    tracking_number = request.form.get('tracking_number', '')
    
    order.status = status
    if tracking_number:
        order.tracking_number = tracking_number
    
    db.session.commit()
    
    flash('Order status updated successfully!', 'success')
    return redirect(url_for('admin.order_detail', order_id=order_id))

@admin_bp.route('/api/chart/sales')
@login_required
def api_sales_chart():
    # Get sales data for the last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    orders = Order.query.filter(Order.order_date >= thirty_days_ago).all()
    
    # Prepare sales data by day
    sales_data = {}
    for order in orders:
        day = order.order_date.strftime('%Y-%m-%d')
        if day not in sales_data:
            sales_data[day] = 0
        sales_data[day] += order.total_amount
    
    # Convert to list for chart
    sales_chart_data = [{"date": day, "amount": amount} for day, amount in sales_data.items()]
    sales_chart_data.sort(key=lambda x: x['date'])
    
    return jsonify(sales_chart_data)

@admin_bp.route('/api/chart/inventory')
@login_required
def api_inventory_chart():
    # Get raw materials inventory
    raw_materials = RawMaterial.query.all()
    raw_material_data = [{"name": rm.name, "type": rm.type} for rm in raw_materials]
    
    # Get product inventory
    products = Product.query.all()
    product_data = [{"name": p.name, "stock": p.stock} for p in products]
    
    return jsonify({
        "raw_materials": raw_material_data,
        "products": product_data
    })

@admin_bp.route('/api/chart/production')
@login_required
def api_production_chart():
    # Get production data for the last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    productions = Production.query.filter(
        Production.end_date >= thirty_days_ago,
        Production.status == 'completed'
    ).all()
    
    # Group by product type
    production_data = {}
    for prod in productions:
        product_name = prod.product.name
        if product_name not in production_data:
            production_data[product_name] = 0
        production_data[product_name] += prod.quantity
    
    # Convert to list for chart
    production_chart_data = [{"product": name, "quantity": qty} for name, qty in production_data.items()]
    
    return jsonify(production_chart_data)