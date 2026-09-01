#!/bin/bash

# Trip Planner API - Development Run Script

echo "🚀 Starting Trip Planner API..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate

    # Check if Flask is installed
    if ! venv/bin/python3 -c "import flask" 2>/dev/null; then
        echo "📥 Installing dependencies..."
        venv/bin/pip3 install -q -r requirements.txt
    fi
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "✏️  Please edit .env with your database credentials"
    exit 1
fi

# Export environment variables
export FLASK_APP=app.py
export FLASK_ENV=development

# Run the application with venv's python
echo "✅ Starting Flask server on http://localhost:5000"
if [ -d "venv" ]; then
    venv/bin/python3 app.py
else
    python3 app.py
fi
