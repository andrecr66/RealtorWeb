import json
from datetime import datetime, date
from app import app, db
from app.models.models import AdminUser, Agent, Property, Testimonial, ContactInquiry

def seed_data():
    print("Clearing old data...")
    # Delete in reverse order of dependencies
    ContactInquiry.query.delete()
    Testimonial.query.delete()
    Property.query.delete()
    Agent.query.delete()
    AdminUser.query.delete()
    db.session.commit()
    print("Old data cleared.")

    # Seed Admin User
    print("Seeding admin users...")
    admin1 = AdminUser(username='admin')
    admin1.set_password('password123')
    db.session.add(admin1)
    db.session.commit() # Commit to ensure admin user is created before other potential dependencies if any
    print(f"Admin user '{admin1.username}' created.")

    # Seed Agent Information
    print("Seeding agents...")
    agent_maria = Agent(
        name="Maria Elena Rodríguez",
        bio="Con más de 15 años de experiencia en el sector inmobiliario, Maria Elena se ha consolidado como una de las agentes más confiables y conocedoras del mercado local. Su pasión por ayudar a las personas a encontrar la propiedad de sus sueños, combinada con una ética de trabajo intachable, la convierten en la aliada perfecta.",
        email="maria.elena@example.com",
        phone="+34 123 456 789",
        profile_picture_url="default_agent.png", # Placeholder image filename
        contact_info="Oficina Central, Calle Principal 123, Ciudad. L-V 9am-6pm"
    )
    db.session.add(agent_maria)
    db.session.commit() # Commit to get agent_maria.id for properties
    print(f"Agent '{agent_maria.name}' created with ID: {agent_maria.id}.")

    # Seed Properties
    print("Seeding properties...")
    property1 = Property(
        title="Moderna Casa con Piscina y Amplio Jardín",
        description="Esta impresionante casa moderna ofrece un estilo de vida lujoso y confortable. Con cuatro amplios dormitorios, cada uno con abundante luz natural, y tres baños elegantemente diseñados. La cocina gourmet está equipada con electrodomésticos de última generación. El salón de concepto abierto se extiende a una hermosa terraza con vistas al jardín paisajístico y a la piscina privada.",
        price=450000.00,
        property_type="Casa",
        address="Calle Ficus 12, Urbanización Los Girasoles, Ciudad Sol",
        size_sqm=250,
        bedrooms=4,
        bathrooms=3,
        features="Piscina privada, Jardín paisajístico, Cocina gourmet, Garaje para dos coches, Aire acondicionado central, Sistema de seguridad",
        images=json.dumps(["property_images/modern_house_pool.jpg", "property_images/modern_house_living.jpg", "property_images/modern_house_garden.jpg"]),
        status="For Sale",
        date_listed=datetime.utcnow(),
        agent_id=agent_maria.id
    )
    db.session.add(property1)

    property2 = Property(
        title="Apartamento Céntrico con Vistas Panorámicas",
        description="Luminoso apartamento en el corazón de la ciudad, ideal para profesionales o parejas. Cuenta con dos dormitorios, dos baños completos, y una cocina americana integrada al salón. Grandes ventanales ofrecen vistas espectaculares. Edificio con portero y ascensor.",
        price=280000.00,
        property_type="Apartamento",
        address="Avenida Libertad 5, Piso 8, Centro Urbano",
        size_sqm=120,
        bedrooms=2,
        bathrooms=2,
        features="Vistas panorámicas, Cocina americana, Portero, Ascensor, Calefacción central",
        images=json.dumps(["property_images/apartment_city_view.jpg", "property_images/apartment_interior.jpg"]),
        status="For Sale",
        date_listed=datetime.utcnow(),
        agent_id=agent_maria.id
    )
    db.session.add(property2)

    property3 = Property(
        title="Villa de Lujo con Vistas al Mar en Costa Serena",
        description="Espectacular villa de diseño contemporáneo ubicada en la prestigiosa zona de Costa Serena. Ofrece 5 dormitorios en suite, amplias terrazas con vistas directas al mar, piscina infinita, y acceso privado a una cala. Materiales de primera calidad y domótica.",
        price=1250000.00,
        property_type="Villa",
        address="Camino de la Costa 77, Costa Serena, Paraíso Azul",
        size_sqm=450,
        bedrooms=5,
        bathrooms=5,
        features="Vistas al mar, Piscina infinita, Acceso privado a cala, Domótica, Garaje para 3 coches, Bodega",
        images=json.dumps(["property_images/luxury_villa_sea.jpg", "property_images/luxury_villa_pool.jpg", "property_images/luxury_villa_terrace.jpg"]),
        status="For Sale",
        date_listed=datetime.utcnow(),
        agent_id=agent_maria.id
    )
    db.session.add(property3)
    
    property4 = Property(
        title="Acogedor Chalet en Zona Residencial Tranquila",
        description="Encantador chalet adosado perfecto para familias. Dispone de 3 dormitorios, 2 baños, un aseo, jardín privado con barbacoa y acceso a piscina comunitaria. Ubicado en una urbanización consolidada con todos los servicios cerca.",
        price=320000.00,
        property_type="Chalet",
        address="Calle de los Pinos 45, Residencial El Robledal",
        size_sqm=180,
        bedrooms=3,
        bathrooms=2,
        features="Jardín privado, Barbacoa, Piscina comunitaria, Garaje, Trastero",
        images=json.dumps(["property_images/cozy_chalet_exterior.jpg", "property_images/cozy_chalet_garden.jpg"]),
        status="Sold", # Example of a sold property
        date_listed=datetime(2023, 10, 15), # Older date
        agent_id=agent_maria.id
    )
    db.session.add(property4)
    db.session.commit() # Commit properties to get their IDs for testimonials
    print(f"Properties seeded: {property1.title}, {property2.title}, {property3.title}, {property4.title}")

    # Seed Testimonials
    print("Seeding testimonials...")
    testimonial1 = Testimonial(
        client_name="Familia Gómez",
        date=date(2023, 11, 20),
        rating=5,
        comment="Maria Elena fue increíblemente profesional y nos ayudó a encontrar la casa de nuestros sueños en tiempo récord. ¡Totalmente recomendada!",
        property_id=property4.id # Linked to the sold property
    )
    db.session.add(testimonial1)

    testimonial2 = Testimonial(
        client_name="Carlos López",
        date=date(2024, 1, 10),
        rating=4,
        comment="El proceso de venta de mi apartamento fue fluido y sin estrés gracias al equipo. Muy contento con el resultado y la comunicación constante.",
        property_id=None # General testimonial, or could be linked to another property if more are added
    )
    db.session.add(testimonial2)

    testimonial3 = Testimonial(
        client_name="Laura Vargas",
        date=date(2024, 3, 5),
        rating=5,
        comment="Comprar mi primera propiedad fue una gran decisión, y Maria Elena me guio en cada paso del camino con paciencia y experiencia. ¡Muy agradecida!",
        property_id=property1.id # Linked to property1
    )
    db.session.add(testimonial3)
    print("Testimonials seeded.")

    # Seed Contact Inquiries
    print("Seeding contact inquiries...")
    inquiry1 = ContactInquiry(
        name="Juan Pérez",
        email="juan.perez@example.com",
        message="Estoy muy interesado en la propiedad 'Moderna Casa con Piscina y Amplio Jardín'. ¿Podríamos concertar una visita esta semana? Gracias.",
        property_id=property1.id,
        date_received=datetime.utcnow()
    )
    db.session.add(inquiry1)

    inquiry2 = ContactInquiry(
        name="Ana Martín",
        email="ana.martin@example.com",
        message="Quisiera más información general sobre el proceso de compra y los tipos de propiedades que manejan en la zona de Costa Serena. Saludos.",
        property_id=None, # General inquiry
        date_received=datetime.utcnow()
    )
    db.session.add(inquiry2)
    print("Contact inquiries seeded.")

    db.session.commit()
    print("Database seeded successfully!")

if __name__ == '__main__':
    with app.app_context():
        seed_data()
