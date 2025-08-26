# Dynamic Elements Manager API

FastAPI backend for the Dynamic Elements Manager application.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create uploads directory:
```bash
mkdir uploads
```

3. Run the development server:
```bash
python run.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Dynamic Elements
- `GET /api/v1/elements/` - List all elements
- `POST /api/v1/elements/` - Create new element
- `GET /api/v1/elements/{id}` - Get element by ID
- `PUT /api/v1/elements/{id}` - Update element
- `DELETE /api/v1/elements/{id}` - Delete element
- `POST /api/v1/elements/{id}/validate` - Mark element as validated

### Dataset Entries
- `GET /api/v1/dataset/` - List all dataset entries
- `POST /api/v1/dataset/` - Create new dataset entry
- `GET /api/v1/dataset/{id}` - Get dataset entry by ID
- `DELETE /api/v1/dataset/{id}` - Delete dataset entry

### File Upload
- `POST /api/v1/files/upload` - Upload files
- `GET /api/v1/files/{id}` - Download file by ID
- `GET /api/v1/files/` - List files (optionally by element_id)
- `DELETE /api/v1/files/{id}` - Delete file

## Database

The application uses SQLite by default. The database file will be created automatically as `dynamic_elements.db`.

## Configuration

Environment variables can be set in `.env` file:

- `DATABASE_URL` - Database connection string
- `BACKEND_CORS_ORIGINS` - Allowed CORS origins (comma-separated)
- `UPLOAD_FOLDER` - Directory for file uploads
- `MAX_UPLOAD_SIZE` - Maximum file size in bytes
- `ALLOWED_EXTENSIONS` - Allowed file extensions (comma-separated)