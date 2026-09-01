#!/bin/bash

# Trip Planner API - Setup Script

echo "🚀 Setting up Trip Planner API..."

# Check Python version
echo "📋 Checking Python version..."
python3 --version

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your database credentials"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your PostgreSQL credentials"
echo "2. Create PostgreSQL database: createdb trip_planner"
echo "3. Initialize database: flask db init && flask db migrate && flask db upgrade"
echo "4. (Optional) Seed sample data: python seed_data.py"
echo "5. Run the API: ./run.sh or python app.py"
echo ""
