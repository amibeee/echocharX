from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import User, Supplier, RawMaterial, Supply, Negotiation, NegotiationMessage
from datetime import datetime

supplier_bp = Blueprint('supplier', __name__, url_prefix='/supplier')

@supplier_bp.before_request
def check_supplier():
    if not current_user.is_authenticated or not current_user.is_supplier():
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('auth.login'))

@supplier_bp.route('/dashboard')
@login_required
def dashboard():
    # Get supplier profile
    supplier = Supplier.query.filter_by(user_id=current_user.id).first()
    
    if not supplier:
        flash('Supplier profile not found!', 'danger')
        return redirect(url_for('auth.logout'))
    
    # Get recent supplies
    recent_supplies = Supply.query.filter_by(supplier_id=supplier.id).order_by(Supply.created_at.desc()).limit(5).all()
    
    # Get active negotiations
    active_negotiations = Negotiation.query.filter_by(
        supplier_id=supplier.id,
        status='in_progress'
    ).all()
    
    # Get raw materials
    raw_materials = RawMaterial.query.all()
    
    return render_template(
        'supplier/dashboard.html',
        supplier=supplier,
        recent_supplies=recent_supplies,
        active_negotiations=active_negotiations,
        raw_materials=raw_materials
    )

@supplier_bp.route('/inventory')
@login_required
def inventory():
    supplier = Supplier.query.filter_by(user_id=current_user.id).first()
    
    if not supplier:
        flash('Supplier profile not found!', 'danger')
        return redirect(url_for('auth.logout'))
    
    # Get all supplies by this supplier
    supplies = Supply.query.filter_by(supplier_id=supplier.id).order_by(Supply.created_at.desc()).all()
    
    # Get raw materials
    raw_materials = RawMaterial.query.all()
    
    return render_template(
        'supplier/inventory.html',
        supplier=supplier,
        supplies=supplies,
        raw_materials=raw_materials
    )

@supplier_bp.route('/supply/add', methods=['POST'])
@login_required
def add_supply():
    supplier = Supplier.query.filter_by(user_id=current_user.id).first()
    
    if not supplier:
        flash('Supplier profile not found!', 'danger')
        return redirect(url_for('auth.logout'))
    
    raw_material_id = request.form.get('raw_material_id')
    quantity = float(request.form.get('quantity'))
    unit_price = float(request.form.get('unit_price'))
    total_price = quantity * unit_price
    
    supply = Supply(
        supplier_id=supplier.id,
        raw_material_id=raw_material_id,
        quantity=quantity,
        unit_price=unit_price,
        total_price=total_price,
        status='pending'
    )
    
    db.session.add(supply)
    db.session.commit()
    
    flash('Supply added successfully!', 'success')
    return redirect(url_for('supplier.inventory'))

@supplier_bp.route('/negotiations')
@login_required
def negotiations():
    supplier = Supplier.query.filter_by(user_id=current_user.id).first()
    
    if not supplier:
        flash('Supplier profile not found!', 'danger')
        return redirect(url_for('auth.logout'))
    
    # Get all negotiations for this supplier
    negotiations = Negotiation.query.filter_by(supplier_id=supplier.id).order_by(Negotiation.created_at.desc()).all()
    
    return render_template(
        'supplier/negotiations.html',
        supplier=supplier,
        negotiations=negotiations
    )

@supplier_bp.route('/negotiation/<int:negotiation_id>')
@login_required
def negotiation_detail(negotiation_id):
    supplier = Supplier.query.filter_by(user_id=current_user.id).first()
    
    if not supplier:
        flash('Supplier profile not found!', 'danger')
        return redirect(url_for('auth.logout'))
    
    # Get negotiation
    negotiation = Negotiation.query.get_or_404(negotiation_id)
    
    # Check if this negotiation belongs to the supplier
    if negotiation.supplier_id != supplier.id:
        flash('You do not have permission to view this negotiation!', 'danger')
        return redirect(url_for('supplier.negotiations'))
    
    # Get messages
    messages = NegotiationMessage.query.filter_by(negotiation_id=negotiation_id).order_by(NegotiationMessage.created_at).all()
    
    # Get raw material
    raw_material = RawMaterial.query.get(negotiation.raw_material_id)
    
    return render_template(
        'supplier/negotiation_detail.html',
        supplier=supplier,
        negotiation=negotiation,
        messages=messages,
        raw_material=raw_material
    )

@supplier_bp.route('/negotiation/<int:negotiation_id>/message', methods=['POST'])
@login_required
def add_negotiation_message(negotiation_id):
    supplier = Supplier.query.filter_by(user_id=current_user.id).first()
    
    if not supplier:
        flash('Supplier profile not found!', 'danger')
        return redirect(url_for('auth.logout'))
    
    # Get negotiation
    negotiation = Negotiation.query.get_or_404(negotiation_id)
    
    # Check if this negotiation belongs to the supplier
    if negotiation.supplier_id != supplier.id:
        flash('You do not have permission to view this negotiation!', 'danger')
        return redirect(url_for('supplier.negotiations'))
    
    message_text = request.form.get('message')
    counter_price = request.form.get('counter_price')
    
    if counter_price:
        counter_price = float(counter_price)
        negotiation.current_price = counter_price
        message_text = f"Counter offer: ${counter_price} per unit. " + message_text
        db.session.commit()
    
    message = NegotiationMessage(
        negotiation_id=negotiation_id,
        sender_id=current_user.id,
        message=message_text
    )
    
    db.session.add(message)
    db.session.commit()
    
    return redirect(url_for('supplier.negotiation_detail', negotiation_id=negotiation_id))

@supplier_bp.route('/negotiation/<int:negotiation_id>/accept', methods=['POST'])
@login_required
def accept_negotiation(negotiation_id):
    supplier = Supplier.query.filter_by(user_id=current_user.id).first()
    
    if not supplier:
        flash('Supplier profile not found!', 'danger')
        return redirect(url_for('auth.logout'))
    
    # Get negotiation
    negotiation = Negotiation.query.get_or_404(negotiation_id)
    
    # Check if this negotiation belongs to the supplier
    if negotiation.supplier_id != supplier.id:
        flash('You do not have permission to update this negotiation!', 'danger')
        return redirect(url_for('supplier.negotiations'))
    
    negotiation.status = 'accepted'
    negotiation.completed_at = datetime.utcnow()
    
    message = NegotiationMessage(
        negotiation_id=negotiation_id,
        sender_id=current_user.id,
        message=f"I accept the offer at ${negotiation.current_price} per unit."
    )
    
    db.session.add(message)
    db.session.commit()
    
    flash('Negotiation accepted successfully!', 'success')
    return redirect(url_for('supplier.negotiation_detail', negotiation_id=negotiation_id))

@supplier_bp.route('/negotiation/<int:negotiation_id>/reject', methods=['POST'])
@login_required
def reject_negotiation(negotiation_id):
    supplier = Supplier.query.filter_by(user_id=current_user.id).first()
    
    if not supplier:
        flash('Supplier profile not found!', 'danger')
        return redirect(url_for('auth.logout'))
    
    # Get negotiation
    negotiation = Negotiation.query.get_or_404(negotiation_id)
    
    # Check if this negotiation belongs to the supplier
    if negotiation.supplier_id != supplier.id:
        flash('You do not have permission to update this negotiation!', 'danger')
        return redirect(url_for('supplier.negotiations'))
    
    negotiation.status = 'rejected'
    negotiation.completed_at = datetime.utcnow()
    
    message = NegotiationMessage(
        negotiation_id=negotiation_id,
        sender_id=current_user.id,
        message="I cannot accept this offer. Negotiation rejected."
    )
    
    db.session.add(message)
    db.session.commit()
    
    flash('Negotiation rejected!', 'success')
    return redirect(url_for('supplier.negotiation_detail', negotiation_id=negotiation_id))