# CrisisGrid AI - Backend API

FastAPI backend for the CrisisGrid AI crisis intelligence platform.

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

Ensure your `.env` file is configured in the `Buildproject/` directory with:

```bash
DATABASE_URL=postgresql://crisisgrid:crisisgrid_password@localhost:5432/crisisgrid
JWT_SECRET=your_secure_secret_here
FRONTEND_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,https://crisisgrid-ai.vercel.app
WATSONX_ENABLED=true
WATSONX_API_KEY=your_key_here
WATSONX_PROJECT_ID=your_project_id_here
CLOUDANT_ENABLED=true
CLOUDANT_URL=your_cloudant_url_here
CLOUDANT_API_KEY=your_cloudant_key_here
```

### 3. Verify PostgreSQL

Ensure PostgreSQL is running:

```bash
# Check if PostgreSQL is running
pg_isready

# Test connection
psql postgresql://crisisgrid:crisisgrid_password@localhost:5432/crisisgrid
```

### 4. Run the Server

```bash
# From backend directory
python -m app.main

# Or with uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Testing the API

### Health Check

```bash
# Simple health check
curl http://localhost:8000/health

# Detailed health check
curl http://localhost:8000/api/v1/health/detailed

# Ping
curl http://localhost:8000/api/v1/ping
```

### API Documentation

Once the server is running, visit:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

## Demo Seed Data

Create 50 demo users and 300 Nairobi/Kenya crisis reports:

```bash
cd Buildproject/backend
python scripts/seed_data.py
```

All seeded users use password `Password123!`.

Demo accounts:

| Role | Email |
| --- | --- |
| Citizen | `citizen.demo01@demo.crisisgrid.ai` |
| Authority | `authority.demo01@demo.crisisgrid.ai` |
| Admin | `admin.demo01@demo.crisisgrid.ai` |

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py        # Configuration management
│   ├── db/
│   │   ├── __init__.py
│   │   └── session.py       # Database session management
│   └── api/
│       ├── __init__.py
│       └── routes/
│           ├── __init__.py
│           └── health.py    # Health check endpoints
├── requirements.txt
└── README.md
```

## Environment Variables

### Required
- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET` - Secret key for JWT tokens
- `FRONTEND_ORIGINS` - Comma-separated CORS allowlist

### Optional (IBM Services)
- `CLOUDANT_ENABLED` - Enable IBM Cloudant (default: false)
- `CLOUDANT_URL` - Cloudant instance URL
- `CLOUDANT_API_KEY` - Cloudant API key
- `WATSONX_ENABLED` - Enable watsonx.ai (default: false)
- `WATSONX_API_KEY` - watsonx.ai API key
- `WATSONX_PROJECT_ID` - watsonx.ai project ID

### Optional (External Services)
- `WEATHER_ENABLED` - Enable weather API (default: false)
- `SMS_ENABLED` - Enable SMS dispatch (default: false)

## Development

### Running Tests

```bash
pytest
```

### Code Quality

```bash
# Format code
black app/

# Lint
flake8 app/

# Type checking
mypy app/
```

## Next Steps

After Phase 1 (Backend Skeleton) is complete:

1. **Phase 2:** Add database models and schemas
2. **Phase 3:** Implement report submission API
3. **Phase 4:** Build verification and decision engine
4. **Phase 5:** Add GeoRisk and clustering logic

## Troubleshooting

### Database Connection Failed

```bash
# Check PostgreSQL is running
pg_isready

# Verify connection string
echo $DATABASE_URL

# Test connection manually
psql $DATABASE_URL
```

### Import Errors

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>
```

## Support

For issues or questions, refer to:
- Main project README
- ../../docs/planning/BUILD_PLAN.md
- ../../docs/ibm/IBM_PRODUCT_ACCESS_REQUIREMENTS.md
