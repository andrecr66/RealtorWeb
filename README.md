# Maria Elena Bienes Raíces - Realtor Website

## Description
Maria Elena Bienes Raíces is a Flask-based web application designed for a real estate agency. It features a public-facing website for users to browse property listings, view agent details, and make contact. It also includes a comprehensive admin panel for managing site content, including properties, agent information, client testimonials, and contact inquiries.

## Features
*   **Public Website:**
    *   Homepage with featured properties and quick contact form.
    *   Property listings page with advanced search and filtering (by keyword, type, price, bedrooms, bathrooms, size, features) and sorting.
    *   Detailed property view page with image gallery, description, features, map (placeholder), and agent contact.
    *   Agent profile page displaying bio, contact information, and related testimonials.
    *   Sales history page showcasing sold properties and client testimonials.
    *   Contact form for general inquiries.
*   **Admin Panel (`/admin`):**
    *   Secure login for administrators.
    *   Dashboard with overview and links to management sections.
    *   **CRUD Operations for Properties:** Create, read, update, and delete property listings, including multi-image uploads and management.
    *   **Agent Profile Management:** Update agent's bio, contact details, and profile picture.
    *   **CRUD Operations for Testimonials:** Add, review, edit, and delete client testimonials, with optional linking to properties.
    *   **Contact Inquiry Management:** View and delete contact inquiries submitted through the website.

## Tech Stack
*   **Backend:** Python, Flask
*   **Database:** PostgreSQL
*   **ORM:** Flask-SQLAlchemy, Alembic (for migrations)
*   **Authentication:** Flask-Login (for admin panel)
*   **Frontend:** HTML, Tailwind CSS (via CDN)
*   **Environment Management:** python-dotenv

## Prerequisites
To set up and run this project locally, you will need:
*   Python 3.7+
*   PostgreSQL server (ensure it's running and you have privileges to create databases and users)
*   Git (for cloning the repository)

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url> 
    # Replace <repository_url> with the actual URL of the repository
    ```

2.  **Navigate to the project directory:**
    ```bash
    cd RealtorWeb 
    # Or your chosen project directory name
    ```

3.  **Create a Python virtual environment:**
    ```bash
    python -m venv .venv 
    # You can use 'venv' or any other name for your virtual environment directory
    ```

4.  **Activate the virtual environment:**
    *   On macOS and Linux:
        ```bash
        source .venv/bin/activate
        ```
    *   On Windows:
        ```bash
        .venv\Scripts\activate
        ```

5.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

6.  **Database Setup (PostgreSQL):**
    *   Connect to your PostgreSQL server (e.g., using `psql` or a GUI tool like pgAdmin).
    *   Create a new database for the project. For example:
        ```sql
        CREATE DATABASE maria_elena_realty;
        ```
    *   (Optional but recommended) Create a dedicated database user and grant privileges:
        ```sql
        CREATE USER me_realty_user WITH PASSWORD 'your_strong_password_here';
        GRANT ALL PRIVILEGES ON DATABASE maria_elena_realty TO me_realty_user;
        ALTER DATABASE maria_elena_realty OWNER TO me_realty_user; 
        ```
        *Note: If you create a new user, ensure your `.env` file reflects these credentials.*

7.  **Environment Configuration:**
    *   The `.env` file is used to store environment-specific configurations like database credentials and secret keys. This file is not committed to version control for security reasons.
    *   Copy the example environment file:
        ```bash
        cp .env.example .env
        ```
    *   Open the `.env` file in a text editor and set the following variables:
        *   `FLASK_APP=run.py` (Usually pre-set)
        *   `FLASK_ENV=development` (For development mode)
        *   `SECRET_KEY`: **Generate a strong, random secret key.** You can use Python to generate one:
            ```python
            import secrets
            secrets.token_hex(24) 
            # Copy the output of this into your .env file
            ```
        *   `DB_USER`: Your PostgreSQL username (e.g., `me_realty_user` if created, or your default superuser like `postgres`).
        *   `DB_PASSWORD`: Your PostgreSQL user's password.
        *   `DB_HOST`: Usually `localhost` for local development.
        *   `DB_PORT`: Default is `5432`.
        *   `DB_NAME`: The name of the database you created (e.g., `maria_elena_realty`).

8.  **Database Migrations:**
    *   Ensure your `.env` file is correctly configured and the PostgreSQL server is running.
    *   Apply database migrations to create the schema:
        ```bash
        flask db upgrade
        ```
        *(If you encounter issues, ensure `flask db init` has been run once in the project's history to set up the migration environment - this should already be done for this project).*

9.  **Data Seeding (Optional but Recommended for Initial Setup):**
    *   Populate the database with initial sample data:
        ```bash
        python seed.py
        ```

## Running the Application

1.  **Start the Flask development server:**
    ```bash
    flask run
    ```
    Alternatively, you can run `python run.py`.

2.  Open your web browser and navigate to:
    [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

## Admin Access

*   **Admin Panel URL:** [http://127.0.0.1:5000/admin/login](http://127.0.0.1:5000/admin/login)
*   **Default Admin Credentials (from `seed.py`):**
    *   Username: `admin`
    *   Password: `password123`

## Notes on Image Uploads
*   Property images uploaded via the admin panel are stored in `app/static/uploads/properties/`.
*   Agent profile pictures are stored in `app/static/uploads/agent_profile/`.
*   Ensure these directories are writable by the Flask application process if running in a production-like environment. For development, this is typically not an issue.

---
Happy developing!
