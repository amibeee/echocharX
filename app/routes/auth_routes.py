from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Role, Supplier, Client
from werkzeug.security import generate_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('admin.dashboard'))
        elif current_user.is_supplier():
            return redirect(url_for('supplier.dashboard'))
        elif current_user.is_client():
            return redirect(url_for('client.dashboard'))
    return render_template('index.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('auth.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            flash('Please check your login details and try again.', 'danger')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=remember)
        
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            if user.is_admin():
                next_page = url_for('admin.dashboard')
            elif user.is_supplier():
                next_page = url_for('supplier.dashboard')
            elif user.is_client():
                next_page = url_for('client.dashboard')
        
        return redirect(next_page)
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('auth.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        role_name = request.form.get('role')
        
        # Check if email already exists
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email address already exists', 'danger')
            return redirect(url_for('auth.register'))
        
        # Get role
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            flash('Invalid role', 'danger')
            return redirect(url_for('auth.register'))
        
        # Create new user
        new_user = User(
            email=email,
            name=name,
            role_id=role.id
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        # Create supplier or client profile if applicable
        if role_name == 'supplier':
            company_name = request.form.get('company_name')
            contact_number = request.form.get('contact_number')
            address = request.form.get('address')
            
            supplier = Supplier(
                user_id=new_user.id,
                company_name=company_name,
                contact_number=contact_number,
                address=address
            )
            
            db.session.add(supplier)
            db.session.commit()
        
        elif role_name == 'client':
            company_name = request.form.get('company_name')
            contact_number = request.form.get('contact_number')
            address = request.form.get('address')
            
            client = Client(
                user_id=new_user.id,
                company_name=company_name,
                contact_number=contact_number,
                address=address
            )
            
            db.session.add(client)
            db.session.commit()
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.index'))