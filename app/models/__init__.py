from app import db # This line is important
from .models import AdminUser, Agent, Property, Testimonial, ContactInquiry

# You can optionally define __all__ if you want to control what `from app.models import *` imports
# __all__ = ['AdminUser', 'Agent', 'Property', 'Testimonial', 'ContactInquiry']
