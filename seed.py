# seed.py
from app import create_app, db
from app.models.models import AdminUser, Agent, Property, Testimonial, ContactInquiry
from datetime import datetime, timedelta
import json # To handle the 'images' field for Property if it's a JSON string

# Create an app instance
app = create_app()

# Push an application context
with app.app_context():
    print("Dropping all tables (for clean seed)...")
    db.drop_all() # CAUTION: This deletes all existing data. Only for development/initial seed.
    print("Creating all tables...")
    db.create_all() # Creates tables based on models if they don't exist (or after drop_all)

    print("Seeding database...")

    # 1. Seed AdminUser
    admin_username = 'admin'
    existing_admin = AdminUser.query.filter_by(username=admin_username).first()
    if not existing_admin:
        admin = AdminUser(username=admin_username)
        admin.set_password('password123') # Default password from README
        db.session.add(admin)
        print(f"Admin user '{admin_username}' created.")
    else:
        print(f"Admin user '{admin_username}' already exists.")
    
    db.session.commit() # Commit admin user so it's available if needed

    # 2. Seed Agent
    agent_email = 'maria.elena@example.realty'
    existing_agent = Agent.query.filter_by(email=agent_email).first()
    if not existing_agent:
        agent_maria = Agent(
            name='Maria Elena Rodríguez',
            bio='Con más de 10 años de experiencia en el mercado inmobiliario local, Maria Elena Rodríguez se ha consolidado como una experta en ayudar a sus clientes a encontrar la propiedad perfecta. Su enfoque personalizado y conocimiento profundo del mercado aseguran transacciones exitosas y clientes satisfechos.',
            email=agent_email,
            phone='+34 666 777 888', # Example from your Stitch design
            profile_picture_url='uploads/agent_profile/maria_elena.jpg', # Placeholder
            contact_info='Calle Principal, 123, Ciudad, País' # Example
        )
        db.session.add(agent_maria)
        print("Agent 'Maria Elena Rodríguez' created.")
    else:
        agent_maria = existing_agent # Use existing agent for linking
        print("Agent 'Maria Elena Rodríguez' already exists.")
        
    db.session.commit() # Commit agent to get its ID for properties

    # Ensure agent_maria has an ID
    if not agent_maria or not agent_maria.id:
        print("Critical error: Agent Maria Elena could not be created or found. Aborting property seeding.")
    else:
        # 3. Seed Properties
        properties_data = [
            {
                "title": "Casa de Ensueño en el Campo",
                "description": "Una hermosa casa rústica con amplios jardines y vistas espectaculares, ideal para quienes buscan tranquilidad y contacto con la naturaleza. Completamente renovada con acabados modernos.",
                "price": 450000.00,
                "property_type": "Casa Rural",
                "address": "Camino del Sol, Parcela 12, Afueras de la Ciudad",
                "size_sqm": 220,
                "bedrooms": 3,
                "bathrooms": 2,
                "features": "Jardín grande, Piscina privada, Chimenea, Barbacoa, Garaje para 2 coches",
                "images": json.dumps(['uploads/properties/campo_exterior.jpg', 'uploads/properties/campo_interior1.jpg', 'uploads/properties/campo_piscina.jpg']),
                "status": "For Sale",
                "is_featured": True # From your Stitch homepage design
            },
            {
                "title": "Apartamento Moderno en el Centro",
                "description": "Luminoso y moderno apartamento situado en el corazón de la ciudad, a pasos de tiendas, restaurantes y transporte público. Perfecto para profesionales o parejas.",
                "price": 280000.00,
                "property_type": "Apartamento",
                "address": "Calle Central 45, Piso 3, Centro Urbano",
                "size_sqm": 95,
                "bedrooms": 2,
                "bathrooms": 2,
                "features": "Balcón con vistas, Cocina equipada, Aire acondicionado, Ascensor, Seguridad 24h",
                "images": json.dumps(['uploads/properties/centro_salon.jpg', 'uploads/properties/centro_cocina.jpg', 'uploads/properties/centro_balcon.jpg']),
                "status": "For Sale",
                "is_featured": True # From your Stitch homepage design
            },
            {
                "title": "Villa de Lujo con Vista al Mar",
                "description": "Espectacular villa de lujo con impresionantes vistas panorámicas al mar. Diseño contemporáneo, piscina infinita y acabados de la más alta calidad. Una propiedad exclusiva.",
                "price": 1200000.00,
                "property_type": "Villa",
                "address": "Urbanización Vista Mar, 7, Costa Serena",
                "size_sqm": 450,
                "bedrooms": 5,
                "bathrooms": 4,
                "features": "Piscina infinita, Vistas al mar, Jacuzzi, Cine en casa, Gimnasio, Garaje subterráneo",
                "images": json.dumps(['uploads/properties/villa_exterior.jpg', 'uploads/properties/villa_piscina.jpg', 'uploads/properties/villa_interior.jpg']),
                "status": "For Sale",
                "is_featured": True # From your Stitch homepage design
            },
            {
                "title": "Acogedor Chalet en la Montaña",
                "description": "Encantador chalet con estilo alpino, perfecto para escapadas de fin de semana o para vivir rodeado de naturaleza. Vistas a las montañas y senderos cercanos.",
                "price": 320000.00,
                "property_type": "Chalet",
                "address": "Camino de los Pinos, 23, Sierra Verde",
                "size_sqm": 150,
                "bedrooms": 3,
                "bathrooms": 2,
                "features": "Terraza grande, Vistas a la montaña, Estufa de leña, Jardín",
                "images": json.dumps(['uploads/properties/chalet_montana1.jpg', 'uploads/properties/chalet_montana2.jpg']),
                "status": "For Sale",
                "is_featured": False
            }
        ]

        created_properties = []
        for prop_data in properties_data:
            existing_prop = Property.query.filter_by(title=prop_data["title"]).first()
            if not existing_prop:
                new_prop = Property(agent_id=agent_maria.id, **prop_data)
                db.session.add(new_prop)
                created_properties.append(new_prop)
                print(f"Property '{prop_data['title']}' created.")
            else:
                created_properties.append(existing_prop) # Use existing for testimonial linking
                print(f"Property '{prop_data['title']}' already exists.")
        
        db.session.commit() # Commit properties to get their IDs

        # 4. Seed Testimonials
        testimonials_data = [
            {
                "client_name": "Ana M.",
                "comment": "Maria Elena fue excepcional. Su conocimiento del mercado y su atención a los detalles hicieron que la compra de mi casa fuera una experiencia sin problemas. Siempre estuvo disponible para responder a mis preguntas y me guió en cada paso del camino. ¡La recomiendo encarecidamente!",
                "rating": 5,
                "date": datetime.utcnow() - timedelta(days=90),
                "property_title_to_link": "Apartamento Moderno en el Centro" # Optional: link to a property
            },
            {
                "client_name": "Carlos R.",
                "comment": "Trabajar con Maria Elena fue un placer. Su profesionalismo y dedicación son incomparables. Encontró la propiedad perfecta para mí y negoció un excelente precio. Su experiencia y habilidades de comunicación son de primera clase.",
                "rating": 5,
                "date": datetime.utcnow() - timedelta(days=60)
            },
            {
                "client_name": "Sofía L.",
                "comment": "Maria Elena superó mis expectativas. Su pasión por su trabajo es evidente y su compromiso con sus clientes es inquebrantable. Me sentí apoyada y confiada durante todo el proceso de venta de mi apartamento. ¡Gracias, Maria Elena!",
                "rating": 5,
                "date": datetime.utcnow() - timedelta(days=30),
                "property_title_to_link": "Casa de Ensueño en el Campo" # Optional
            }
        ]

        for test_data in testimonials_data:
            prop_id_to_link = None
            if "property_title_to_link" in test_data:
                linked_prop = Property.query.filter_by(title=test_data["property_title_to_link"]).first()
                if linked_prop:
                    prop_id_to_link = linked_prop.id
                else:
                    print(f"Warning: Could not find property '{test_data['property_title_to_link']}' to link testimonial.")
            
            existing_test = Testimonial.query.filter_by(client_name=test_data["client_name"], comment=test_data["comment"]).first()
            if not existing_test:
                new_test = Testimonial(
                    client_name=test_data["client_name"],
                    comment=test_data["comment"],
                    rating=test_data["rating"],
                    date=test_data["date"],
                    property_id=prop_id_to_link
                )
                db.session.add(new_test)
                print(f"Testimonial from '{test_data['client_name']}' created.")
            else:
                print(f"Testimonial from '{test_data['client_name']}' (similar comment) already exists.")

        # 5. Seed Contact Inquiry (Example)
        existing_inquiry = ContactInquiry.query.filter_by(email="test.inquirer@example.com").first()
        if not existing_inquiry:
            inquiry1 = ContactInquiry(
                name="Test Inquirer",
                email="test.inquirer@example.com",
                message="I am very interested in the 'Villa de Lujo con Vista al Mar'. Can I schedule a viewing?",
                # property_id can be set if you find the property by title as done for testimonials
            )
            villa_prop = Property.query.filter_by(title="Villa de Lujo con Vista al Mar").first()
            if villa_prop:
                inquiry1.property_id = villa_prop.id
            db.session.add(inquiry1)
            print("Contact Inquiry from 'Test Inquirer' created.")
        else:
            print("Contact Inquiry from 'Test Inquirer' already exists.")

        db.session.commit()
        print("Database seeded successfully!")