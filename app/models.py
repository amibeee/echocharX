from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')
    
    def __repr__(self):
        return f'<Role {self.name}>'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    supplier = db.relationship('Supplier', backref='user', uselist=False)
    client = db.relationship('Client', backref='user', uselist=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role.name == 'admin'
    
    def is_supplier(self):
        return self.role.name == 'supplier'
    
    def is_client(self):
        return self.role.name == 'client'
    
    def __repr__(self):
        return f'<User {self.email}>'

class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    company_name = db.Column(db.String(100))
    contact_number = db.Column(db.String(20))
    address = db.Column(db.String(200))
    supplies = db.relationship('Supply', backref='supplier', lazy='dynamic')
    negotiations = db.relationship('Negotiation', backref='supplier', lazy='dynamic')
    
    def __repr__(self):
        return f'<Supplier {self.company_name}>'

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    company_name = db.Column(db.String(100))
    contact_number = db.Column(db.String(20))
    address = db.Column(db.String(200))
    orders = db.relationship('Order', backref='client', lazy='dynamic')
    
    def __repr__(self):
        return f'<Client {self.company_name}>'

class RawMaterial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    type = db.Column(db.String(50))  # 'date_kernel' or 'filter_component'
    description = db.Column(db.Text)
    supplies = db.relationship('Supply', backref='raw_material', lazy='dynamic')
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory.id'))
    
    def __repr__(self):
        return f'<RawMaterial {self.name}>'

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    type = db.Column(db.String(50))  # 'echo_coal' or 'filter'
    filter_type = db.Column(db.String(50), nullable=True)  # 'air' or 'water' if type is 'filter'
    description = db.Column(db.Text)
    price = db.Column(db.Float)
    stock = db.Column(db.Integer, default=0)
    image_url = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    order_items = db.relationship('OrderItem', backref='product', lazy='dynamic')
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory.id'))
    
    def __repr__(self):
        return f'<Product {self.name}>'

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    raw_materials = db.relationship('RawMaterial', backref='inventory')
    products = db.relationship('Product', backref='inventory')
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Inventory {self.id}>'

class Supply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'))
    raw_material_id = db.Column(db.Integer, db.ForeignKey('raw_material.id'))
    quantity = db.Column(db.Float)
    unit_price = db.Column(db.Float)
    total_price = db.Column(db.Float)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, delivered
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    delivered_at = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<Supply {self.id}>'

class Negotiation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'))
    raw_material_id = db.Column(db.Integer, db.ForeignKey('raw_material.id'))
    raw_material = db.relationship('RawMaterial')  # ← cette ligne est nécessaire
    initial_price = db.Column(db.Float)
    current_price = db.Column(db.Float)
    target_price = db.Column(db.Float)
    status = db.Column(db.String(20), default='in_progress')  # in_progress, accepted, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    messages = db.relationship('NegotiationMessage', backref='negotiation', lazy='dynamic')
    
    def __repr__(self):
        return f'<Negotiation {self.id}>'

class NegotiationMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    negotiation_id = db.Column(db.Integer, db.ForeignKey('negotiation.id'))
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sender = db.relationship('User')
    
    def __repr__(self):
        return f'<NegotiationMessage {self.id}>'

class Production(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer)
    raw_material_used = db.Column(db.Float)
    status = db.Column(db.String(20), default='planned')  # planned, in_progress, completed
    start_date = db.Column(db.DateTime, nullable=True)
    end_date = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    product = db.relationship('Product')

    def __repr__(self):
        return f'<Production {self.id}>'

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'))
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    total_amount = db.Column(db.Float, default=0)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, shipped, delivered, cancelled
    shipping_address = db.Column(db.String(200))
    tracking_number = db.Column(db.String(100), nullable=True)
    items = db.relationship('OrderItem', backref='order', lazy='dynamic')
    
    def __repr__(self):
        return f'<Order {self.id}>'

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer)
    unit_price = db.Column(db.Float)
    subtotal = db.Column(db.Float)
    
    def __repr__(self):
        return f'<OrderItem {self.id}>'