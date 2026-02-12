# Data Aggregator

A Flask web application for uploading CSV/Excel files with advertising data, aggregating metrics by year, and viewing results.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running

```bash
python app.py
```

The app starts at `http://localhost:5000`. A default admin account is created on first launch: `admin@admin.com` / `admin123`.

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `SECRET_KEY` | Session signing key | Randomly generated |

## Project Structure

```
app.py              — app factory, Flask/Login/CSRF initialization
config.py           — configuration (prod, test)
models.py           — User model (Flask-Login)
parser.py           — file reading and validation
template.csv        — expected column definitions

db/                 — database package (SQLite)
  connection.py     — connection, table init, column metadata
  users.py          — user CRUD, password verification
  records.py        — record insert, clear, aggregation
  logs.py           — upload logs

routes/             — Flask blueprints
  auth.py           — login, registration, logout
  main.py           — file upload, results, clear
  admin.py          — admin panel (logs, users, data)
  decorators.py     — admin_required decorator

templates/          — Jinja2 templates
tests/              — pytest tests
```

## Testing

```bash
python -m pytest tests/ -v
```

## Roles

- **user** — upload files, view aggregated results
- **admin** — all of the above + clear database, view upload logs, user list, raw data
