from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models.models import AdminUser, Property, Agent, Testimonial, ContactInquiry # Import ContactInquiry
from app import db
import os # For file operations
from datetime import datetime # Import datetime
import json # For handling image filenames list
from werkzeug.utils import secure_filename # For securing filenames

# Define the upload folders and allowed extensions
PROPERTY_UPLOAD_FOLDER = 'app/static/uploads/properties'
AGENT_PROFILE_UPLOAD_FOLDER = 'app/static/uploads/agent_profile' # New folder for agent profiles
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Ensure upload folders exist
os.makedirs(PROPERTY_UPLOAD_FOLDER, exist_ok=True)
os.makedirs(AGENT_PROFILE_UPLOAD_FOLDER, exist_ok=True) # Create agent profile upload folder

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated and isinstance(current_user, AdminUser):
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Please enter both username and password.', 'warning')
            return render_template('admin/login.html', title='Admin Login')

        admin_user = AdminUser.query.filter_by(username=username).first()

        if admin_user and admin_user.check_password(password):
            login_user(admin_user)
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin.dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')
    
    return render_template('admin/login.html', title='Admin Login')

@admin_bp.route('/logout')
@login_required
def logout():
    if not isinstance(current_user, AdminUser):
        flash('Permission denied. You must be an admin to access this.', 'danger')
        return redirect(url_for('main.index')) 
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('admin.login'))

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if not isinstance(current_user, AdminUser):
        flash('Permission denied. You must be an admin to access this page.', 'danger')
        logout_user() 
        return redirect(url_for('admin.login'))
    return render_template('admin/dashboard.html', title='Admin Dashboard')

# Placeholder routes for future admin functionalities
@admin_bp.route('/properties')
@login_required
def manage_properties():
    if not isinstance(current_user, AdminUser):
        flash('Permission denied. You must be an admin to access this page.', 'danger')
        logout_user()
        return redirect(url_for('admin.login'))
    
    properties = Property.query.order_by(Property.date_listed.desc()).all()
    return render_template('admin/manage_properties.html', 
                           title='Manage Properties', 
                           properties=properties)

@admin_bp.route('/properties/new', methods=['GET', 'POST'])
@login_required
def add_property():
    if not isinstance(current_user, AdminUser):
        flash('Permission denied. You must be an admin to access this page.', 'danger')
        logout_user()
        return redirect(url_for('admin.login'))

    available_agents = Agent.query.all()
    if not available_agents:
        flash('No agents available. Please add an agent first.', 'warning')
        # Potentially redirect to an add_agent page or handle as appropriate
        # For now, we'll allow the form to render but agent selection will be empty.

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        price = request.form.get('price')
        property_type = request.form.get('property_type')
        address = request.form.get('address')
        size_sqm = request.form.get('size_sqm', type=int, default=None)
        bedrooms = request.form.get('bedrooms', type=int, default=None)
        bathrooms = request.form.get('bathrooms', type=int, default=None)
        features_str = request.form.get('features', '')
        status = request.form.get('status', 'For Sale')
        agent_id = request.form.get('agent_id', type=int)

        # Basic validation
        if not all([title, description, price, property_type, address, agent_id]):
            flash('Please fill in all required fields (Title, Description, Price, Type, Address, Agent).', 'danger')
            return render_template('admin/property_form.html', 
                                   title='Add New Property', 
                                   property=None, 
                                   action_url=url_for('admin.add_property'),
                                   available_agents=available_agents)
        
        image_filenames = []
        uploaded_files = request.files.getlist('images')
        for file in uploaded_files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # To prevent overwriting, prepend a unique ID or timestamp (optional but good)
                # For simplicity, just using the filename for now.
                # Consider adding unique prefix: filename = str(uuid.uuid4()) + "_" + filename
                file.save(os.path.join(PROPERTY_UPLOAD_FOLDER, filename)) # Use PROPERTY_UPLOAD_FOLDER
                image_filenames.append(filename)
            elif file and not allowed_file(file.filename):
                flash(f'File type not allowed for {file.filename}. Allowed types are {ALLOWED_EXTENSIONS}', 'warning')


        new_property = Property(
            title=title,
            description=description,
            price=float(price), # Ensure price is float
            property_type=property_type,
            address=address,
            size_sqm=size_sqm,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            features=features_str,
            images=json.dumps(image_filenames) if image_filenames else None, # Store as JSON string
            status=status,
            agent_id=agent_id
        )
        
        try:
            db.session.add(new_property)
            db.session.commit()
            flash(f'Property "{title}" added successfully!', 'success')
            return redirect(url_for('admin.manage_properties'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding property: {str(e)}', 'danger')

    # GET request or if POST failed validation and re-renders
    return render_template('admin/property_form.html', 
                           title='Add New Property', 
                           property=None, # No existing property for add form
                           action_url=url_for('admin.add_property'),
                           available_agents=available_agents)

@admin_bp.route('/properties/<int:property_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_property(property_id):
    if not isinstance(current_user, AdminUser):
        flash('Permission denied. You must be an admin to access this page.', 'danger')
        logout_user()
        return redirect(url_for('admin.login'))

    property_to_edit = Property.query.get_or_404(property_id)
    available_agents = Agent.query.all()

    if request.method == 'POST':
        property_to_edit.title = request.form.get('title')
        property_to_edit.description = request.form.get('description')
        property_to_edit.price = float(request.form.get('price'))
        property_to_edit.property_type = request.form.get('property_type')
        property_to_edit.address = request.form.get('address')
        property_to_edit.size_sqm = request.form.get('size_sqm', type=int, default=property_to_edit.size_sqm)
        property_to_edit.bedrooms = request.form.get('bedrooms', type=int, default=property_to_edit.bedrooms)
        property_to_edit.bathrooms = request.form.get('bathrooms', type=int, default=property_to_edit.bathrooms)
        property_to_edit.features = request.form.get('features', '')
        property_to_edit.status = request.form.get('status', 'For Sale')
        property_to_edit.agent_id = request.form.get('agent_id', type=int)

        # Basic validation
        if not all([property_to_edit.title, property_to_edit.description, property_to_edit.price, 
                    property_to_edit.property_type, property_to_edit.address, property_to_edit.agent_id]):
            flash('Please fill in all required fields.', 'danger')
            return render_template('admin/property_form.html', 
                                   title='Edit Property', 
                                   property=property_to_edit, 
                                   action_url=url_for('admin.edit_property', property_id=property_id),
                                   available_agents=available_agents)

        # Handle image updates
        current_images = json.loads(property_to_edit.images) if property_to_edit.images else []
        
        # Images to delete
        images_to_delete = request.form.getlist('delete_images')
        if images_to_delete:
            for img_filename in images_to_delete:
                if img_filename in current_images:
                    current_images.remove(img_filename)
                    try:
                        os.remove(os.path.join(PROPERTY_UPLOAD_FOLDER, img_filename)) # Use PROPERTY_UPLOAD_FOLDER
                        flash(f'Image "{img_filename}" deleted.', 'info')
                    except OSError as e:
                        flash(f'Error deleting image file "{img_filename}": {e.strerror}', 'warning')
        
        # New images to add
        uploaded_files = request.files.getlist('images') # 'images' is the name of the file input in the form
        new_image_filenames = []
        for file in uploaded_files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Consider adding unique prefix: filename = str(uuid.uuid4()) + "_" + filename
                file.save(os.path.join(PROPERTY_UPLOAD_FOLDER, filename)) # Use PROPERTY_UPLOAD_FOLDER
                new_image_filenames.append(filename)
            elif file and not allowed_file(file.filename):
                 flash(f'File type not allowed for {file.filename}. Allowed types are {ALLOWED_EXTENSIONS}', 'warning')

        all_image_filenames = current_images + new_image_filenames
        property_to_edit.images = json.dumps(all_image_filenames) if all_image_filenames else None
        
        try:
            db.session.commit()
            flash(f'Property "{property_to_edit.title}" updated successfully!', 'success')
            return redirect(url_for('admin.manage_properties'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating property: {str(e)}', 'danger')

    # GET request
    return render_template('admin/property_form.html', 
                           title='Edit Property', 
                           property=property_to_edit, 
                           action_url=url_for('admin.edit_property', property_id=property_id),
                           available_agents=available_agents)

@admin_bp.route('/properties/<int:property_id>/delete', methods=['POST'])
@login_required
def delete_property(property_id):
    if not isinstance(current_user, AdminUser):
        flash('Permission denied. You must be an admin to access this page.', 'danger')
        logout_user()
        return redirect(url_for('admin.login'))

    property_to_delete = Property.query.get_or_404(property_id)

    # Delete associated images
    if property_to_delete.images:
        try:
            image_filenames = json.loads(property_to_delete.images)
            for filename in image_filenames:
                try:
                    image_path = os.path.join(PROPERTY_UPLOAD_FOLDER, filename) # Use PROPERTY_UPLOAD_FOLDER
                    if os.path.exists(image_path):
                        os.remove(image_path)
                        # flash(f'Deleted image file: {filename}', 'info') # Maybe too verbose for this context
                except Exception as e:
                    flash(f'Error deleting image file {filename}: {str(e)}', 'warning')
        except json.JSONDecodeError:
            flash('Error decoding image filenames JSON.', 'warning')
        except Exception as e: # Catch other potential errors during file ops
            flash(f'An error occurred during image file deletion: {str(e)}', 'warning')


    try:
        db.session.delete(property_to_delete)
        db.session.commit()
        flash(f'Property "{property_to_delete.title}" and its images deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting property: {str(e)}', 'danger')

    return redirect(url_for('admin.manage_properties'))

@admin_bp.route('/agent/edit', methods=['GET', 'POST'])
@login_required
def manage_agent():
    if not isinstance(current_user, AdminUser):
        flash('Permission denied. You must be an admin to access this page.', 'danger')
        logout_user()
        return redirect(url_for('admin.login'))

    agent = Agent.query.first() # Assuming a single agent profile for now
    form_action = 'edit' if agent else 'create'

    if request.method == 'POST':
        name = request.form.get('name')
        bio = request.form.get('bio')
        email = request.form.get('email')
        phone = request.form.get('phone')
        contact_info = request.form.get('contact_info') # Assuming this field exists

        if not name or not email:
            flash('Name and Email are required fields.', 'danger')
            return render_template('admin/agent_form.html', 
                                   title='Manage Agent Information', 
                                   agent=agent, 
                                   form_action=form_action)

        profile_picture_filename = agent.profile_picture_url if agent else None

        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename != '' and allowed_file(file.filename):
                # Delete old picture if it exists and is different
                if agent and agent.profile_picture_url:
                    old_pic_path = os.path.join(AGENT_PROFILE_UPLOAD_FOLDER, agent.profile_picture_url)
                    if os.path.exists(old_pic_path):
                        try:
                            os.remove(old_pic_path)
                        except OSError:
                            flash(f"Error deleting old profile picture file: {agent.profile_picture_url}", "warning")
                
                profile_picture_filename = secure_filename(file.filename)
                # Consider adding unique prefix: profile_picture_filename = str(uuid.uuid4()) + "_" + profile_picture_filename
                file.save(os.path.join(AGENT_PROFILE_UPLOAD_FOLDER, profile_picture_filename))
            elif file and file.filename != '' and not allowed_file(file.filename):
                flash(f'File type not allowed for profile picture. Allowed types are {ALLOWED_EXTENSIONS}', 'warning')


        if agent: # Update existing agent
            agent.name = name
            agent.bio = bio
            agent.email = email
            agent.phone = phone
            agent.contact_info = contact_info
            if profile_picture_filename: # Only update if a new one was successfully uploaded or old one retained
                agent.profile_picture_url = profile_picture_filename
        else: # Create new agent
            agent = Agent(
                name=name,
                bio=bio,
                email=email,
                phone=phone,
                contact_info=contact_info,
                profile_picture_url=profile_picture_filename
            )
            db.session.add(agent)
        
        try:
            db.session.commit()
            flash('Agent information updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating agent information: {str(e)}', 'danger')
        
        return redirect(url_for('admin.manage_agent')) # Redirect back to the same page

    # GET request
    return render_template('admin/agent_form.html', 
                           title='Manage Agent Information', 
                           agent=agent, 
                           form_action=form_action)

@admin_bp.route('/testimonials')
@login_required
def manage_testimonials():
    if not isinstance(current_user, AdminUser):
        flash('Permission denied. You must be an admin to access this page.', 'danger')
        logout_user()
        return redirect(url_for('admin.login'))
    
    testimonials = Testimonial.query.order_by(Testimonial.date.desc()).all()
    return render_template('admin/manage_testimonials.html', 
                           title='Manage Testimonials', 
                           testimonials=testimonials)

@admin_bp.route('/testimonials/new', methods=['GET', 'POST'])
@login_required
def add_testimonial():
    if not isinstance(current_user, AdminUser):
        flash('Permission denied.', 'danger')
        return redirect(url_for('admin.login'))

    properties = Property.query.order_by(Property.title).all()

    if request.method == 'POST':
        client_name = request.form.get('client_name')
        date_str = request.form.get('date')
        rating_str = request.form.get('rating')
        comment = request.form.get('comment')
        property_id_str = request.form.get('property_id')

        if not client_name or not comment or not date_str:
            flash('Client Name, Date, and Comment are required.', 'danger')
        else:
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                rating = int(rating_str) if rating_str else None
                if rating is not None and not (1 <= rating <= 5):
                    flash('Rating must be between 1 and 5.', 'danger')
                    raise ValueError("Invalid rating")

                property_id = int(property_id_str) if property_id_str and property_id_str != 'None' else None
                
                new_testimonial = Testimonial(
                    client_name=client_name,
                    date=date_obj,
                    rating=rating,
                    comment=comment,
                    property_id=property_id
                )
                db.session.add(new_testimonial)
                db.session.commit()
                flash('Testimonial added successfully!', 'success')
                return redirect(url_for('admin.manage_testimonials'))
            except ValueError as e:
                if str(e) != "Invalid rating": # Avoid double flashing for rating
                    flash(f'Invalid data: {e}', 'danger')
            except Exception as e:
                db.session.rollback()
                flash(f'Error adding testimonial: {str(e)}', 'danger')
    
    return render_template('admin/testimonial_form.html', 
                           title='Add New Testimonial', 
                           form_action='create', 
                           testimonial=None, 
                           properties=properties)


@admin_bp.route('/testimonials/<int:testimonial_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_testimonial(testimonial_id):
    if not isinstance(current_user, AdminUser):
        flash('Permission denied.', 'danger')
        return redirect(url_for('admin.login'))

    testimonial = Testimonial.query.get_or_404(testimonial_id)
    properties = Property.query.order_by(Property.title).all()

    if request.method == 'POST':
        testimonial.client_name = request.form.get('client_name')
        date_str = request.form.get('date')
        rating_str = request.form.get('rating')
        testimonial.comment = request.form.get('comment')
        property_id_str = request.form.get('property_id')

        if not testimonial.client_name or not testimonial.comment or not date_str:
            flash('Client Name, Date, and Comment are required.', 'danger')
        else:
            try:
                testimonial.date = datetime.strptime(date_str, '%Y-%m-%d').date()
                rating = int(rating_str) if rating_str else None
                if rating is not None and not (1 <= rating <= 5):
                    flash('Rating must be between 1 and 5.', 'danger')
                    raise ValueError("Invalid rating")
                testimonial.rating = rating
                
                testimonial.property_id = int(property_id_str) if property_id_str and property_id_str != 'None' else None
                
                db.session.commit()
                flash('Testimonial updated successfully!', 'success')
                return redirect(url_for('admin.manage_testimonials'))
            except ValueError as e:
                 if str(e) != "Invalid rating":
                    flash(f'Invalid data: {e}', 'danger')
            except Exception as e:
                db.session.rollback()
                flash(f'Error updating testimonial: {str(e)}', 'danger')

    return render_template('admin/testimonial_form.html', 
                           title='Edit Testimonial', 
                           form_action='edit', 
                           testimonial=testimonial, 
                           properties=properties)

@admin_bp.route('/testimonials/<int:testimonial_id>/delete', methods=['POST'])
@login_required
def delete_testimonial(testimonial_id):
    if not isinstance(current_user, AdminUser):
        flash('Permission denied.', 'danger')
        return redirect(url_for('admin.login'))
        
    testimonial = Testimonial.query.get_or_404(testimonial_id)
    try:
        db.session.delete(testimonial)
        db.session.commit()
        flash('Testimonial deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting testimonial: {str(e)}', 'danger')
    return redirect(url_for('admin.manage_testimonials'))

@admin_bp.route('/inquiries')
@login_required
def view_inquiries():
    if not isinstance(current_user, AdminUser):
        flash('Permission denied. You must be an admin to access this page.', 'danger')
        logout_user()
        return redirect(url_for('admin.login'))
    
    inquiries = ContactInquiry.query.order_by(ContactInquiry.date_received.desc()).all()
    return render_template('admin/manage_inquiries.html', 
                           title='View Contact Inquiries', 
                           inquiries=inquiries)

@admin_bp.route('/inquiries/<int:inquiry_id>')
@login_required
def view_inquiry_detail(inquiry_id):
    if not isinstance(current_user, AdminUser):
        flash('Permission denied.', 'danger')
        return redirect(url_for('admin.login'))
    
    inquiry = ContactInquiry.query.get_or_404(inquiry_id)
    return render_template('admin/view_inquiry_detail.html', 
                           title='Inquiry Details', 
                           inquiry=inquiry)

@admin_bp.route('/inquiries/<int:inquiry_id>/delete', methods=['POST'])
@login_required
def delete_inquiry(inquiry_id):
    if not isinstance(current_user, AdminUser):
        flash('Permission denied.', 'danger')
        return redirect(url_for('admin.login'))
        
    inquiry = ContactInquiry.query.get_or_404(inquiry_id)
    try:
        db.session.delete(inquiry)
        db.session.commit()
        flash('Inquiry deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting inquiry: {str(e)}', 'danger')
    return redirect(url_for('admin.view_inquiries'))
