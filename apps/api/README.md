# Inventory Management Backend

A Django REST Framework backend for inventory management with CRUD operations, one-to-many relationships, and Excel import/export capabilities.

## Project Structure

```
inventory-backend/
├── core/                    # Django project directory
│   ├── config/             # Project settings and configuration
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── inventory/          # Inventory app
│   │   ├── models.py       # Category and Item models
│   │   ├── views.py        # API viewsets
│   │   ├── serializers.py  # DRF serializers
│   │   ├── urls.py         # App-level URL routing
│   │   └── admin.py        # Django admin configuration
│   └── manage.py
├── requirements.txt
└── README.md
```

## Features

- RESTful API for inventory management
- One-to-many relationship: Items belong to Categories
- Django Admin interface for data management
- Django REST Framework for API endpoints

## Setup

1. Create and activate virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Navigate to the Django project directory:

```bash
cd core
```

4. Run migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

5. Create superuser (optional):

```bash
python manage.py createsuperuser
```

6. Run development server:

```bash
python manage.py runserver
```

## API Endpoints

- `GET/POST /api/items/` - List all items or create a new item
- `GET/PUT/PATCH/DELETE /api/items/{id}/` - Retrieve, update, or delete a specific item
- `GET /admin/` - Django admin interface

## Models

### Category

- `name` (CharField): Category name

### Item

- `name` (CharField): Item name
- `quantity` (IntegerField): Item quantity
- `category` (ForeignKey): Reference to Category

## Future Enhancements

- Excel import/export functionality
- Authentication and authorization
- Pagination and filtering
- Search functionality
- API documentation (Swagger/OpenAPI)
