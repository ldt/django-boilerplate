# Django REST API Boilerplate

A modern, production-ready Django REST API boilerplate with JWT authentication, user management, and best practices pre-configured.

## ✨ Features

- 🚀 **Django REST Framework** - Powerful and flexible toolkit for building Web APIs
- 🔐 **JWT Authentication** - Secure token-based authentication with djangorestframework-simplejwt
- 👥 **User Management** - Custom user model with email-based authentication
- 🧪 **Testing** - Pytest setup with test factories
- 🐳 **Docker** - Containerized development and production environments
- 📦 **Modern Python** - Type hints, async support, and modern Python features
- 📊 **API Documentation** - Auto-generated API docs with drf-spectacular

## 🚀 Prerequisites

- Python 3.11+
- uv (https://astral.sh/uv)
- Docker (optional, for containerized development)
- PostgreSQL (can be run in Docker)

## ⚡ Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/django-boilerplate.git
cd django-boilerplate
```

### 2. Set up environment variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit the `.env` file with your configuration:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### 3. Install dependencies with uv

```bash
# Install Python dependencies from uv.lock
uv sync

```

### 4. Set up the database

```bash
# Run migrations
python manage.py migrate

# Create a superuser (optional)
python manage.py createsuperuser
```

### 5. Run the development server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`

## 🏗️ Project Structure

```
django-boilerplate/
├── accounts/               # Custom user model and authentication
├── api/                    # Main API app
├── config/                 # Project configuration
├── uv.lock                # Locked Python dependencies
├── tests/                  # Global test configuration
├── .env.example            # Example environment variables
├── manage.py
└── pyproject.toml          # Project metadata and tool configuration
```

## 🧪 Running Tests

```bash
# Run all tests
uv run pytest
```

## 🛠️ Development

### Code Style

This project uses:
- Astral Ruff for code formatting, import sorting, linting

```bash
uvx ruff check
```

### Git Workflow

1. Create a new branch for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit them:
   ```bash
   git add .
   git commit -m "Your commit message"
   ```

3. Push your changes and create a pull request

## 🚀 Deployment

### Docker (Recommended)

```bash
# Build the Docker image
docker-compose -f docker-compose.prod.yml build

# Run migrations
docker-compose -f docker-compose.prod.yml run --rm web python manage.py migrate

# Start the production stack
docker-compose -f docker-compose.prod.yml up -d
```

### Manual Deployment

1. Set up a production-ready web server (Gunicorn, uWSGI, etc.)
2. Configure a reverse proxy (Nginx, Apache)
3. Set up a production database
4. Configure environment variables
5. Run migrations and collect static files

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with ❤️ using Django and Django REST Framework
- Inspired by industry best practices and real-world applications
