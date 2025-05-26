from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class AdminUser(UserMixin, db.Model):
    __tablename__ = 'admin_user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<AdminUser {self.username}>'

class Agent(db.Model):
    __tablename__ = 'agent'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    profile_picture_url = db.Column(db.String(255), nullable=True)
    contact_info = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Agent {self.name}>'

class Property(db.Model):
    __tablename__ = 'property'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    property_type = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    size_sqm = db.Column(db.Integer, nullable=True)
    bedrooms = db.Column(db.Integer, nullable=True)
    bathrooms = db.Column(db.Integer, nullable=True)
    features = db.Column(db.Text, nullable=True)
    images = db.Column(db.Text, nullable=True) # JSON string array
    status = db.Column(db.String(20), nullable=False, default='For Sale')
    date_listed = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'), nullable=False)
    agent = db.relationship('Agent', backref=db.backref('properties', lazy=True))

    def __repr__(self):
        return f'<Property {self.title}>'

class Testimonial(db.Model):
    __tablename__ = 'testimonial'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    client_name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    rating = db.Column(db.Integer, nullable=True)
    comment = db.Column(db.Text, nullable=False)
    
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=True)
    property = db.relationship('Property', backref=db.backref('testimonials', lazy=True))

    def __repr__(self):
        return f'<Testimonial from {self.client_name}>'

class ContactInquiry(db.Model):
    __tablename__ = 'contact_inquiry'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date_received = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=True)
    property = db.relationship('Property', backref=db.backref('inquiries', lazy=True))

    def __repr__(self):
        return f'<ContactInquiry from {self.name}>'
