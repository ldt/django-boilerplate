# Setup Instructions

This guide will help you set up the development environment for the Django Boilerplate project.

## Prerequisites

- Python 3.8+
- pip (Python package manager)
- PostgreSQL (or your preferred database)
- Git

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ldt/django-boilerplate.git
   cd django-boilerplate
   ```

2. **Create and activate a virtual environment**
   ```bash
   # Using venv
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root:
   ```env
   DEBUG=True
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=postgres://user:password@localhost:5432/dbname
   ALLOWED_HOSTS=localhost,127.0.0.1
   ```

5. **Set up the database**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

## Development Workflow

### Running Tests
```bash
pytest
```

### Running with Docker (optional)
```bash
docker-compose up --build
```

### Code Style
This project uses `black` for code formatting and `flake8` for linting.

```bash
# Format code
black .

# Check for style issues
flake8
```

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DEBUG` | Enable debug mode | `False` | No |
| `SECRET_KEY` | Django secret key | - | Yes |
| `DATABASE_URL` | Database connection URL | - | Yes |
| `ALLOWED_HOSTS` | Allowed hostnames | `[]` | No |
| `EMAIL_BACKEND` | Email backend | `console` | No |
| `DEFAULT_FROM_EMAIL` | Default sender email | `webmaster@localhost` | No |

## Project Structure

```
django-boilerplate/
├── accounts/           # User accounts app
├── core/               # Project configuration
├── static/             # Static files
├── templates/          # HTML templates
├── tests/              # Test files
├── .env.example        # Example environment variables
├── manage.py           # Django management script
└── requirements.txt    # Python dependencies
```
