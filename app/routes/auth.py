from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import datetime
from app import db
from app.models import User
from app.logging_config import get_logger

bp = Blueprint('auth', __name__, url_prefix='/api/auth')
logger = get_logger(__name__)

@bp.route('/register', methods=['POST'])
def register():
    """Create a new user account"""
    data = request.get_json()
    email = data.get('email', 'unknown')

    logger.info('Registration attempt', extra={
        'extra_data': {'email': email}
    })

    # Validate required fields
    required_fields = ['email', 'password', 'dob', 'securityQuestion', 'securityAnswer']
    if not all(field in data for field in required_fields):
        logger.warning('Registration failed: missing fields', extra={
            'extra_data': {
                'email': email,
                'provided_fields': list(data.keys()),
                'missing_fields': [f for f in required_fields if f not in data]
            }
        })
        return jsonify({'error': 'Missing required fields'}), 400

    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        logger.warning('Registration failed: email already exists', extra={
            'extra_data': {'email': email}
        })
        return jsonify({'error': 'Email already registered'}), 409  # 409 Conflict

    try:
        # Create new user
        user = User(
            email=data['email'],
            dob=datetime.strptime(data['dob'], '%Y-%m-%d').date(),
            security_question=data['securityQuestion']
        )
        user.set_password(data['password'])
        user.set_security_answer(data['securityAnswer'])

        db.session.add(user)
        db.session.commit()

        logger.info('User registered successfully', extra={
            'extra_data': {
                'user_id': user.id,
                'email': user.email
            }
        })

        return jsonify({
            'message': 'Account created successfully',
            'user': user.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        logger.error('Registration failed with exception', exc_info=e, extra={
            'extra_data': {'email': email}
        })
        return jsonify({'error': 'Registration failed'}), 500

@bp.route('/login', methods=['POST'])
def login():
    """Login user and return JWT token"""
    data = request.get_json()
    email = data.get('email', 'unknown')

    logger.info('Login attempt', extra={
        'extra_data': {'email': email}
    })

    if not data.get('email') or not data.get('password'):
        logger.warning('Login failed: missing credentials', extra={
            'extra_data': {'email': email}
        })
        return jsonify({'error': 'Email and password required'}), 400

    user = User.query.filter_by(email=data['email']).first()

    if not user or not user.check_password(data['password']):
        logger.warning('Login failed: invalid credentials', extra={
            'extra_data': {
                'email': email,
                'reason': 'user_not_found' if not user else 'invalid_password'
            }
        })
        return jsonify({'error': 'Invalid email or password'}), 401

    access_token = create_access_token(identity=str(user.id))

    logger.info('User logged in successfully', extra={
        'extra_data': {
            'user_id': user.id,
            'email': user.email
        }
    })

    return jsonify({
        'token': access_token,
        'user': user.to_dict()
    }), 200

@bp.route('/reset-password/verify-credentials', methods=['POST'])
def verify_reset_credentials():
    """Step 1: Verify email and DOB"""
    data = request.get_json()
    email = data.get('email', 'unknown')

    logger.info('Password reset: verifying credentials', extra={
        'extra_data': {'email': email}
    })

    if not data.get('email') or not data.get('dob'):
        logger.warning('Password reset failed: missing credentials', extra={
            'extra_data': {'email': email}
        })
        return jsonify({'error': 'Email and date of birth are required'}), 400

    user = User.query.filter_by(email=data['email']).first()

    if not user:
        logger.warning('Password reset failed: account not found', extra={
            'extra_data': {'email': email}
        })
        return jsonify({'error': 'Account not found'}), 404

    # Verify DOB
    try:
        provided_dob = datetime.strptime(data['dob'], '%Y-%m-%d').date()
        if user.dob != provided_dob:
            logger.warning('Password reset failed: DOB mismatch', extra={
                'extra_data': {'email': email}
            })
            return jsonify({'error': 'Date of birth does not match'}), 401
    except ValueError:
        logger.warning('Password reset failed: invalid date format', extra={
            'extra_data': {'email': email}
        })
        return jsonify({'error': 'Invalid date format'}), 400

    logger.info('Credentials verified successfully', extra={
        'extra_data': {'email': email, 'user_id': user.id}
    })

    # Return security question for next step
    return jsonify({
        'message': 'Credentials verified',
        'securityQuestion': user.security_question
    }), 200

@bp.route('/reset-password/verify-security-answer', methods=['POST'])
def verify_security_answer():
    """Step 2: Verify security answer"""
    data = request.get_json()
    email = data.get('email', 'unknown')

    logger.info('Password reset: verifying security answer', extra={
        'extra_data': {'email': email}
    })

    if not data.get('email') or not data.get('securityAnswer'):
        logger.warning('Security answer verification failed: missing fields', extra={
            'extra_data': {'email': email}
        })
        return jsonify({'error': 'Email and security answer are required'}), 400

    user = User.query.filter_by(email=data['email']).first()

    if not user:
        logger.warning('Security answer verification failed: account not found', extra={
            'extra_data': {'email': email}
        })
        return jsonify({'error': 'Account not found'}), 404

    # Verify security answer
    if not user.check_security_answer(data['securityAnswer']):
        logger.warning('Security answer verification failed: incorrect answer', extra={
            'extra_data': {'email': email, 'user_id': user.id}
        })
        return jsonify({'error': 'Security answer is incorrect'}), 401

    logger.info('Security answer verified successfully', extra={
        'extra_data': {'email': email, 'user_id': user.id}
    })

    return jsonify({'message': 'Security answer verified'}), 200

@bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Step 3: Reset password after all verifications"""
    data = request.get_json()
    email = data.get('email', 'unknown')

    logger.info('Password reset: resetting password', extra={
        'extra_data': {'email': email}
    })

    required_fields = ['email', 'dob', 'securityAnswer', 'newPassword']
    if not all(field in data for field in required_fields):
        logger.warning('Password reset failed: missing fields', extra={
            'extra_data': {'email': email}
        })
        return jsonify({'error': 'Missing required fields'}), 400

    user = User.query.filter_by(email=data['email']).first()

    if not user:
        logger.warning('Password reset failed: account not found', extra={
            'extra_data': {'email': email}
        })
        return jsonify({'error': 'Account not found'}), 404

    # Verify DOB
    try:
        provided_dob = datetime.strptime(data['dob'], '%Y-%m-%d').date()
        if user.dob != provided_dob:
            logger.warning('Password reset failed: DOB mismatch', extra={
                'extra_data': {'email': email, 'user_id': user.id}
            })
            return jsonify({'error': 'Date of birth does not match'}), 401
    except ValueError:
        logger.warning('Password reset failed: invalid date format', extra={
            'extra_data': {'email': email}
        })
        return jsonify({'error': 'Invalid date format'}), 400

    # Verify security answer
    if not user.check_security_answer(data['securityAnswer']):
        logger.warning('Password reset failed: incorrect security answer', extra={
            'extra_data': {'email': email, 'user_id': user.id}
        })
        return jsonify({'error': 'Security answer is incorrect'}), 401

    try:
        # Update password
        user.set_password(data['newPassword'])
        db.session.commit()

        logger.info('Password reset successfully', extra={
            'extra_data': {'email': email, 'user_id': user.id}
        })

        return jsonify({'message': 'Password reset successfully'}), 200
    except Exception as e:
        db.session.rollback()
        logger.error('Password reset failed with exception', exc_info=e, extra={
            'extra_data': {'email': email}
        })
        return jsonify({'error': 'Password reset failed'}), 500

@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current authenticated user"""
    user_id = int(get_jwt_identity())

    logger.debug('Fetching current user info', extra={
        'extra_data': {'user_id': user_id}
    })

    try:
        user = User.query.get_or_404(user_id)

        logger.debug('User info retrieved', extra={
            'extra_data': {'user_id': user_id, 'email': user.email}
        })

        return jsonify(user.to_dict()), 200
    except Exception as e:
        logger.error('Failed to get user info', exc_info=e, extra={
            'extra_data': {'user_id': user_id}
        })
        raise

@bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user (client should discard token)"""
    user_id = int(get_jwt_identity())

    logger.info('User logging out', extra={
        'extra_data': {'user_id': user_id}
    })

    return jsonify({'message': 'Logged out successfully'}), 200
