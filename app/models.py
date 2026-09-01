"""Database models for the Trip Planner application"""
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.logging_config import get_logger

logger = get_logger(__name__)


class User(db.Model):
    """User model for authentication and profile"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    security_question = db.Column(db.String(255), nullable=False)
    security_answer_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    trips = db.relationship('Trip', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        """Hash and set the user's password"""
        logger.debug('Setting password hash for user', extra={
            'extra_data': {'email': self.email}
        })
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the hash"""
        result = check_password_hash(self.password_hash, password)
        logger.debug('Password check', extra={
            'extra_data': {'email': self.email, 'valid': result}
        })
        return result

    def set_security_answer(self, answer):
        """Hash and set the security answer"""
        logger.debug('Setting security answer hash for user', extra={
            'extra_data': {'email': self.email}
        })
        self.security_answer_hash = generate_password_hash(answer.lower().strip())

    def check_security_answer(self, answer):
        """Check if the provided security answer matches the hash"""
        result = check_password_hash(self.security_answer_hash, answer.lower().strip())
        logger.debug('Security answer check', extra={
            'extra_data': {'email': self.email, 'valid': result}
        })
        return result

    def to_dict(self):
        """Convert user to dictionary (exclude sensitive data)"""
        return {
            'id': self.id,
            'email': self.email,
            'dob': self.dob.isoformat() if self.dob else None,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<User {self.email}>'


class Trip(db.Model):
    """Trip model for storing travel plans"""
    __tablename__ = 'trips'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    destination = db.Column(db.String(255), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    places = db.relationship('Place', backref='trip', lazy=True, cascade='all, delete-orphan')

    def get_status(self):
        """Calculate trip status based on dates"""
        today = date.today()
        if self.start_date <= today <= self.end_date:
            status = 'current'
        elif today < self.start_date:
            status = 'upcoming'
        else:
            status = 'past'

        logger.debug('Trip status calculated', extra={
            'extra_data': {
                'trip_id': self.id,
                'destination': self.destination,
                'status': status,
                'start_date': self.start_date.isoformat(),
                'end_date': self.end_date.isoformat()
            }
        })
        return status

    def to_dict(self, include_places=True):
        """Convert trip to dictionary"""
        result = {
            'id': self.id,
            'userId': self.user_id,
            'title': self.title,
            'destination': self.destination,
            'startDate': self.start_date.isoformat() if self.start_date else None,
            'endDate': self.end_date.isoformat() if self.end_date else None,
            'status': self.get_status(),
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }

        if include_places:
            result['places'] = [place.to_dict() for place in self.places]
            logger.debug('Trip serialized with places', extra={
                'extra_data': {
                    'trip_id': self.id,
                    'places_count': len(self.places)
                }
            })
        else:
            logger.debug('Trip serialized without places', extra={
                'extra_data': {'trip_id': self.id}
            })

        return result

    def __repr__(self):
        return f'<Trip {self.title} to {self.destination}>'


class Place(db.Model):
    """Place/activity model for trip checklists"""
    __tablename__ = 'places'

    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Convert place to dictionary"""
        return {
            'id': self.id,
            'tripId': self.trip_id,
            'name': self.name,
            'completed': self.completed,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<Place {self.name} ({"✓" if self.completed else "○"})>'
