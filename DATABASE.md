# Database Management Guide

Flask database management similar to Ruby on Rails `rake` tasks.

---

## 🚀 Quick Start (Docker)

### Create Tables (First Time)

```bash
# Option 1: Direct table creation (simple, good for development)
docker compose exec api python manage.py create-all

# Option 2: Using migrations (recommended for production)
docker compose exec api flask db upgrade
```

### Seed Database with Demo Data

```bash
docker compose exec api python manage.py seed
```

**Demo credentials:**
- Email: `demo@tripplanner.com`
- Password: `demo123`

---

## 📋 Available Commands

### Ruby on Rails → Flask Equivalent

| Rails Command | Flask Equivalent | Description |
|--------------|------------------|-------------|
| `rake db:create` | _Not needed_ | Database created by PostgreSQL |
| `rake db:migrate` | `flask db upgrade` | Run migrations |
| `rake db:rollback` | `flask db downgrade` | Rollback migration |
| `rake db:seed` | `python manage.py seed` | Seed database |
| `rake db:reset` | `python manage.py reset` | Drop & recreate |
| `rake db:drop` | `python manage.py drop-all` | Drop all tables |

---

## 🛠️ Development Workflow

### Local Development (without Docker)

```bash
# Activate virtual environment
source venv/bin/activate

# Create tables
python manage.py create-all

# Or use migrations
flask db upgrade

# Seed with demo data
python manage.py seed

# Run the app
python app.py
```

### Docker Development

```bash
# Start services
docker compose up -d

# Create tables
docker compose exec api python manage.py create-all

# Seed data
docker compose exec api python manage.py seed

# View logs
docker compose logs -f api
```

---

## 🔄 Migration Workflow (Production)

### 1. Create Initial Migration

```bash
# First time only
docker compose exec api flask db init

# Generate migration from models
docker compose exec api flask db migrate -m "Initial migration"
```

### 2. Apply Migrations

```bash
# Run migrations
docker compose exec api flask db upgrade
```

### 3. Rollback (if needed)

```bash
# Rollback one migration
docker compose exec api flask db downgrade

# Rollback to beginning
docker compose exec api flask db downgrade base
```

---

## 🧪 Reset Database (Development Only)

**⚠️ WARNING: This deletes ALL data!**

```bash
# Drop all tables and recreate
docker compose exec api python manage.py reset

# Re-seed
docker compose exec api python manage.py seed
```

---

## 📊 Database Schema

### Tables

**users**
- id (Primary Key)
- email (Unique)
- password_hash
- dob (Date of Birth)
- security_question
- security_answer_hash
- created_at

**trips**
- id (Primary Key)
- user_id (Foreign Key → users)
- title
- destination
- start_date
- end_date
- created_at
- updated_at

**places**
- id (Primary Key)
- trip_id (Foreign Key → trips)
- name
- completed (Boolean)
- created_at

---

## 🐛 Troubleshooting

### "relation 'users' does not exist"

**Solution:** Tables haven't been created yet.

```bash
docker compose exec api python manage.py create-all
```

### "Database doesn't exist"

**Solution:** Check docker-compose.yml environment variables match.

```yaml
POSTGRES_DB: tripplanner_db  # Must match DATABASE_URL
DATABASE_URL: postgresql://tripplanner:mypassword@db:5432/tripplanner_db
```

### Start Fresh

```bash
# Stop containers
docker compose down

# Remove volumes (deletes data)
docker compose down -v

# Start again
docker compose up -d

# Create tables
docker compose exec api python manage.py create-all

# Seed
docker compose exec api python manage.py seed
```

---

## 🎯 Best Practices

### Development
- Use `python manage.py create-all` for quick setup
- Use `python manage.py seed` for demo data
- Reset database freely with `python manage.py reset`

### Production
- **Always use migrations** (`flask db upgrade`)
- Never use `create-all` or `reset` in production
- Backup before running migrations
- Test migrations in staging first

---

## 📝 Creating New Migrations

When you change models:

```bash
# 1. Modify app/models.py
# 2. Generate migration
docker compose exec api flask db migrate -m "Add column to users"

# 3. Review migration file in migrations/versions/
# 4. Apply migration
docker compose exec api flask db upgrade
```

---

## 🚀 Kubernetes / Production

In production, run migrations as an **init container** or **Job**:

```yaml
# K8s Job example
apiVersion: batch/v1
kind: Job
metadata:
  name: db-migrate
spec:
  template:
    spec:
      containers:
      - name: migrate
        image: trip-planner-api:v1.0
        command: ["flask", "db", "upgrade"]
```

---

**Need help?** Check the logs:
```bash
docker compose logs api
```
