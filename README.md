# Ticketing API

Event ticket reservation backend that stays correct under concurrent load
(no overselling, no double bookings). Built with FastAPI, SQLAlchemy 2.0 and MySQL 8.

> Work in progress. Architecture notes, benchmark results and a live demo link will be added as the project progresses.

## Quick start

```bash
docker compose up --build
```

- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health and http://localhost:8000/health/db

### Database migrations

```bash
docker compose exec api alembic revision --autogenerate -m "initial schema"
docker compose exec api alembic upgrade head
```

### Tests

```bash
docker compose exec api pytest
```

## Data model

See [docs/er-diagram.md](docs/er-diagram.md).
