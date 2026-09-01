#!/usr/bin/env python
"""
Database management script for Trip Planner API
Similar to Rails rake tasks
"""
import os
import sys
from app import create_app, db
from flask_migrate import Migrate, init, migrate, upgrade, downgrade

app = create_app(os.getenv('FLASK_ENV', 'development'))
migrate_obj = Migrate(app, db)


def print_help():
    """Print available commands"""
    print("""
Trip Planner Database Management (Like Rails rake)
===================================================

Usage: python manage.py <command>

Commands:
  init          Initialize migrations (first time only)
  migrate       Generate a new migration file
  upgrade       Apply migrations to database
  downgrade     Rollback last migration
  create-all    Create all tables directly (development only)
  drop-all      Drop all tables (DANGER!)
  reset         Drop all tables and recreate (DANGER!)
  seed          Seed the database with sample data
  
Examples:
  python manage.py init
  python manage.py migrate -m "create users table"
  python manage.py upgrade
  python manage.py downgrade
    """)


def create_all_tables():
    """Create all tables (like db.create_all())"""
    with app.app_context():
        db.create_all()
        print("✅ All tables created successfully!")


def drop_all_tables():
    """Drop all tables (DANGER!)"""
    with app.app_context():
        confirm = input("⚠️  This will delete ALL data! Type 'yes' to confirm: ")
        if confirm.lower() == 'yes':
            db.drop_all()
            print("✅ All tables dropped!")
        else:
            print("❌ Cancelled")


def reset_database():
    """Drop and recreate all tables (DANGER!)"""
    with app.app_context():
        confirm = input("⚠️  This will DELETE ALL DATA and recreate tables! Type 'yes' to confirm: ")
        if confirm.lower() == 'yes':
            db.drop_all()
            db.create_all()
            print("✅ Database reset complete!")
        else:
            print("❌ Cancelled")


def seed_database():
    """Seed database with sample data"""
    from app.models import User
    from datetime import date
    
    with app.app_context():
        # Check if data already exists
        if User.query.first():
            print("⚠️  Database already has data. Skipping seed.")
            return
        
        # Create sample user
        user = User(
            email='demo@tripplanner.com',
            dob=date(1990, 1, 1),
            security_question='What is your favorite color?'
        )
        user.set_password('demo123')
        user.set_security_answer('blue')
        
        db.session.add(user)
        db.session.commit()
        
        print("✅ Database seeded successfully!")
        print("   Email: demo@tripplanner.com")
        print("   Password: demo123")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'help':
        print_help()
    elif command == 'create-all':
        create_all_tables()
    elif command == 'drop-all':
        drop_all_tables()
    elif command == 'reset':
        reset_database()
    elif command == 'seed':
        seed_database()
    else:
        print(f"❌ Unknown command: {command}")
        print("Run 'python manage.py help' for available commands")
        sys.exit(1)
