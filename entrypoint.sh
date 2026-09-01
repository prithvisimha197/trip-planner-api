#!/bin/bash
# entrypoint.sh

set -e  # Exit on error

echo "🔄 Checking database..."

# Check if migration versions exist
if [ -d "migrations/versions" ] && [ "$(ls -A migrations/versions 2>/dev/null)" ]; then
  echo "📦 Running migrations..."
  flask db upgrade
  echo "✅ Migrations applied successfully!"
else
  echo "⚠️  No migrations found, creating tables directly..."
  python manage.py create-all
  echo "✅ Tables created successfully!"
fi

echo "✅ Database ready!"
echo "🚀 Starting Flask app..."

# Start the app
exec python app.py
