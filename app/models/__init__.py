# app/models/__init__.py

from app import db # This should now work because 'db' is defined at the top level of app/__init__.py
from .models import AdminUser, Agent, Property, Testimonial, ContactInquiry

# You can optionally define __all__ if you want to control what `from app.models import *` imports
# __all__ = ['AdminUser', 'Agent', 'Property', 'Testimonial', 'ContactInquiry']