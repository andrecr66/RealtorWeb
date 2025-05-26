from flask import Blueprint, render_template, url_for, request, redirect, flash # Added redirect, flash
from app.models.models import Property, ContactInquiry, Agent, Testimonial # Import Testimonial
from app import db # Import db
from sqlalchemy import or_, desc, asc

bp = Blueprint('main', __name__) 

@bp.route('/')
def index():
    featured_properties = Property.query.filter_by(status='For Sale')\
                                        .order_by(Property.date_listed.desc())\
                                        .limit(4).all()
    return render_template('home.html', 
                           title='Welcome to Maria Elena Bienes Raíces', 
                           featured_properties=featured_properties)

@bp.route('/properties')
def properties_list():
    search_query_arg = request.args.get('search_query', '')
    property_type_arg = request.args.get('property_type', '')
    price_min_arg = request.args.get('price_min', '')
    price_max_arg = request.args.get('price_max', '')
    bedrooms_arg = request.args.get('bedrooms', '')
    bathrooms_arg = request.args.get('bathrooms', '')
    size_sqm_min_arg = request.args.get('size_sqm_min', '')
    sort_by_arg = request.args.get('sort_by', 'relevance')

    feature_pool_arg = request.args.get('feature_pool')
    feature_garage_arg = request.args.get('feature_garage')
    feature_garden_arg = request.args.get('feature_garden')
    feature_terrace_arg = request.args.get('feature_terrace')
    feature_ac_arg = request.args.get('feature_ac')
    
    active_features = []
    if feature_pool_arg: active_features.append(feature_pool_arg)
    if feature_garage_arg: active_features.append(feature_garage_arg)
    if feature_garden_arg: active_features.append(feature_garden_arg)
    if feature_terrace_arg: active_features.append(feature_terrace_arg)
    if feature_ac_arg: active_features.append(feature_ac_arg)

    query = Property.query.filter(Property.status == 'For Sale')

    if search_query_arg:
        search_term = f"%{search_query_arg}%"
        query = query.filter(
            or_(
                Property.title.ilike(search_term),
                Property.description.ilike(search_term),
                Property.address.ilike(search_term)
            )
        )

    if property_type_arg:
        query = query.filter(Property.property_type == property_type_arg)

    if price_min_arg:
        try:
            query = query.filter(Property.price >= float(price_min_arg))
        except ValueError: pass
    
    if price_max_arg:
        try:
            query = query.filter(Property.price <= float(price_max_arg))
        except ValueError: pass

    if bedrooms_arg:
        try:
            query = query.filter(Property.bedrooms >= int(bedrooms_arg))
        except ValueError: pass 

    if bathrooms_arg:
        try:
            query = query.filter(Property.bathrooms >= int(bathrooms_arg))
        except ValueError: pass

    if size_sqm_min_arg:
        try:
            query = query.filter(Property.size_sqm >= int(size_sqm_min_arg))
        except ValueError: pass
            
    if active_features:
        for feature_name in active_features:
            query = query.filter(Property.features.ilike(f"%{feature_name}%"))

    if sort_by_arg == 'price_asc':
        query = query.order_by(asc(Property.price))
    elif sort_by_arg == 'price_desc':
        query = query.order_by(desc(Property.price))
    elif sort_by_arg == 'date_desc':
        query = query.order_by(desc(Property.date_listed))
    elif sort_by_arg == 'date_asc':
        query = query.order_by(asc(Property.date_listed))
    else: 
        query = query.order_by(desc(Property.date_listed))

    filtered_properties = query.all()

    return render_template('properties.html', 
                           title='Our Properties', 
                           properties=filtered_properties,
                           request_args=request.args) 

@bp.route('/properties/<int:property_id>')
def property_detail(property_id):
    property_data = Property.query.get_or_404(property_id)
    similar_properties = Property.query.filter(
        Property.property_type == property_data.property_type,
        Property.id != property_id,
        Property.status == 'For Sale'
    ).limit(4).all()
    return render_template('property_detail.html', 
                           title=property_data.title, 
                           property_data=property_data,
                           similar_properties=similar_properties)


@bp.route('/about')
def about_agent():
    # Fetch the first agent from the database. 
    # Assuming there's at least one agent, or this will be None.
    # For a multi-agent site, you might pass an agent_id or have a different logic.
    agent = Agent.query.first() 
    # If no agent is in DB, you might want to pass a default or handle it in template
    if not agent:
        # Fallback to placeholder if no agent in DB, to prevent errors
        # Or, you could create a default agent object here if desired
        flash("No agent information found in the database. Displaying placeholder.", "warning")
        agent = { 
            'name': 'Maria Elena Rodríguez (Demo)', 
            'bio': 'Información del agente no disponible actualmente.', 
            'email': 'info@example.com', 
            'phone': 'N/A',
            'profile_picture_url': None, # So template can use placeholder
            'contact_info': 'Por favor, contacte para más detalles.'
        }

    return render_template('about.html', 
                           title=f'Acerca de {agent.name if hasattr(agent, "name") else "Nosotros"}', 
                           agent=agent)

@bp.route('/sales-history')
def sales_history():
    # Fetch sold properties, ordered by date listed (most recent first)
    sold_properties = Property.query.filter_by(status='Sold')\
                                    .order_by(Property.date_listed.desc())\
                                    .limit(6).all() # Limit to a reasonable number for display

    # Fetch all testimonials, ordered by date (most recent first)
    testimonials = Testimonial.query.order_by(Testimonial.date.desc()).all()
    
    return render_template('sales_history.html', 
                           title='Historial de Ventas y Testimonios', 
                           sold_properties=sold_properties, 
                           testimonials=testimonials)

@bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        # subject = request.form.get('subject') # Subject is in the form, but not in ContactInquiry model

        if not name or not email or not message:
            flash('Por favor, complete todos los campos requeridos.', 'danger')
        elif '@' not in email: # Basic email validation
             flash('Por favor, ingrese una dirección de correo electrónico válida.', 'warning')
        else:
            try:
                new_inquiry = ContactInquiry(name=name, email=email, message=message)
                db.session.add(new_inquiry)
                db.session.commit()
                flash('¡Su mensaje ha sido enviado exitosamente!', 'success')
                return redirect(url_for('main.contact'))
            except Exception as e:
                db.session.rollback()
                flash(f'Hubo un error al enviar su mensaje: {str(e)}', 'danger')
    
    return render_template('contact.html', title='Contact Us')

@bp.route('/contact-property/<int:property_id>', methods=['POST'])
def contact_property(property_id):
    property_data = Property.query.get_or_404(property_id) # Ensure property exists
    
    name = request.form.get('name') # Assuming 'name' from property_detail form
    email = request.form.get('email') # Assuming 'email'
    message = request.form.get('message') # Assuming 'message'
    # phone = request.form.get('phone') # Assuming 'phone' if it exists in form

    if not name or not email or not message:
        flash('Por favor, complete todos los campos requeridos.', 'danger')
    elif '@' not in email: # Basic email validation
        flash('Por favor, ingrese una dirección de correo electrónico válida.', 'warning')
    else:
        try:
            new_inquiry = ContactInquiry(
                name=name, 
                email=email, 
                message=message, 
                property_id=property_id
            )
            db.session.add(new_inquiry)
            db.session.commit()
            flash('Su consulta sobre la propiedad ha sido enviada exitosamente!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Hubo un error al enviar su consulta: {str(e)}', 'danger')
            
    return redirect(url_for('main.property_detail', property_id=property_id))
