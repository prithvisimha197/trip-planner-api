from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from sqlalchemy import or_
from app import db
from app.models import Trip
from app.logging_config import get_logger

bp = Blueprint('trips', __name__, url_prefix='/api/trips')
logger = get_logger(__name__)

@bp.route('', methods=['GET'])
@jwt_required()
def get_trips():
    """Get all trips for authenticated user with filtering and pagination"""
    user_id = int(get_jwt_identity())

    logger.info('Fetching trips', extra={
        'extra_data': {'user_id': user_id}
    })

    # Get query parameters
    status = request.args.get('status', 'all')
    page = request.args.get('page', 1, type=int)
    limit = min(request.args.get('limit', 10, type=int), 100)
    sort_by = request.args.get('sort', 'start_date')
    order = request.args.get('order', 'desc')
    search = request.args.get('search', '')

    logger.debug('Query parameters', extra={
        'extra_data': {
            'user_id': user_id,
            'status': status,
            'page': page,
            'limit': limit,
            'sort_by': sort_by,
            'order': order,
            'search': search
        }
    })
    
    # Base query
    query = Trip.query.filter_by(user_id=user_id)
    
    # Filter by status
    if status != 'all':
        from datetime import date
        today = date.today()
        if status == 'current':
            query = query.filter(Trip.start_date <= today, Trip.end_date >= today)
        elif status == 'upcoming':
            query = query.filter(Trip.start_date > today)
        elif status == 'past':
            query = query.filter(Trip.end_date < today)
    
    # Search filter
    if search:
        search_pattern = f'%{search}%'
        query = query.filter(
            or_(
                Trip.title.ilike(search_pattern),
                Trip.destination.ilike(search_pattern)
            )
        )
    
    # Sorting
    sort_column = getattr(Trip, sort_by, Trip.start_date)
    if order == 'desc':
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())
    
    # Pagination
    try:
        paginated = query.paginate(page=page, per_page=limit, error_out=False)

        logger.info('Trips retrieved successfully', extra={
            'extra_data': {
                'user_id': user_id,
                'count': len(paginated.items),
                'total': paginated.total,
                'page': page
            }
        })

        return jsonify({
            'data': [trip.to_dict(include_places=False) for trip in paginated.items],
            'pagination': {
                'page': page,
                'limit': limit,
                'total': paginated.total,
                'totalPages': paginated.pages,
                'hasNext': paginated.has_next,
                'hasPrev': paginated.has_prev
            }
        }), 200
    except Exception as e:
        logger.error('Failed to fetch trips', exc_info=e, extra={
            'extra_data': {'user_id': user_id}
        })
        return jsonify({'error': 'Failed to fetch trips'}), 500

@bp.route('/<int:trip_id>', methods=['GET'])
@jwt_required()
def get_trip(trip_id):
    """Get single trip with places"""
    user_id = int(get_jwt_identity())

    logger.info('Fetching single trip', extra={
        'extra_data': {'user_id': user_id, 'trip_id': trip_id}
    })

    try:
        trip = Trip.query.filter_by(id=trip_id, user_id=user_id).first_or_404()

        include_places = request.args.get('includePlaces', 'true').lower() == 'true'

        logger.info('Trip retrieved successfully', extra={
            'extra_data': {
                'user_id': user_id,
                'trip_id': trip_id,
                'include_places': include_places
            }
        })

        return jsonify(trip.to_dict(include_places=include_places)), 200
    except Exception as e:
        logger.warning('Trip not found', extra={
            'extra_data': {'user_id': user_id, 'trip_id': trip_id}
        })
        raise

@bp.route('', methods=['POST'])
@jwt_required()
def create_trip():
    """Create a new trip"""
    user_id = int(get_jwt_identity())
    data = request.get_json()

    logger.info('Creating trip', extra={
        'extra_data': {
            'user_id': user_id,
            'destination': data.get('destination', 'unknown')
        }
    })

    # Validate required fields
    required_fields = ['title', 'destination', 'startDate', 'endDate']
    if not all(field in data for field in required_fields):
        logger.warning('Trip creation failed: missing fields', extra={
            'extra_data': {
                'user_id': user_id,
                'provided_fields': list(data.keys()),
                'missing_fields': [f for f in required_fields if f not in data]
            }
        })
        return jsonify({'error': 'Missing required fields'}), 400

    # Parse dates
    try:
        start_date = datetime.strptime(data['startDate'], '%Y-%m-%d').date()
        end_date = datetime.strptime(data['endDate'], '%Y-%m-%d').date()
    except ValueError as e:
        logger.warning('Trip creation failed: invalid date format', extra={
            'extra_data': {'user_id': user_id}
        })
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

    # Validate date logic
    if end_date < start_date:
        logger.warning('Trip creation failed: invalid date range', extra={
            'extra_data': {
                'user_id': user_id,
                'start_date': str(start_date),
                'end_date': str(end_date)
            }
        })
        return jsonify({'error': 'End date must be after start date'}), 400

    try:
        # Create trip
        trip = Trip(
            user_id=user_id,
            title=data['title'],
            destination=data['destination'],
            start_date=start_date,
            end_date=end_date
        )

        db.session.add(trip)
        db.session.commit()

        logger.info('Trip created successfully', extra={
            'extra_data': {
                'user_id': user_id,
                'trip_id': trip.id,
                'destination': trip.destination,
                'start_date': str(trip.start_date),
                'end_date': str(trip.end_date)
            }
        })

        return jsonify(trip.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        logger.error('Trip creation failed with exception', exc_info=e, extra={
            'extra_data': {'user_id': user_id}
        })
        return jsonify({'error': 'Failed to create trip'}), 500

@bp.route('/<int:trip_id>', methods=['PUT'])
@jwt_required()
def update_trip(trip_id):
    """Update an existing trip"""
    user_id = int(get_jwt_identity())

    logger.info('Updating trip', extra={
        'extra_data': {'user_id': user_id, 'trip_id': trip_id}
    })

    try:
        trip = Trip.query.filter_by(id=trip_id, user_id=user_id).first_or_404()
        data = request.get_json()

        logger.debug('Update data received', extra={
            'extra_data': {
                'user_id': user_id,
                'trip_id': trip_id,
                'fields': list(data.keys())
            }
        })

        # Update fields
        if 'title' in data:
            trip.title = data['title']
        if 'destination' in data:
            trip.destination = data['destination']
        if 'startDate' in data:
            try:
                trip.start_date = datetime.strptime(data['startDate'], '%Y-%m-%d').date()
            except ValueError:
                logger.warning('Trip update failed: invalid start date format', extra={
                    'extra_data': {'user_id': user_id, 'trip_id': trip_id}
                })
                return jsonify({'error': 'Invalid start date format'}), 400
        if 'endDate' in data:
            try:
                trip.end_date = datetime.strptime(data['endDate'], '%Y-%m-%d').date()
            except ValueError:
                logger.warning('Trip update failed: invalid end date format', extra={
                    'extra_data': {'user_id': user_id, 'trip_id': trip_id}
                })
                return jsonify({'error': 'Invalid end date format'}), 400

        # Validate date logic
        if trip.end_date < trip.start_date:
            logger.warning('Trip update failed: invalid date range', extra={
                'extra_data': {
                    'user_id': user_id,
                    'trip_id': trip_id,
                    'start_date': str(trip.start_date),
                    'end_date': str(trip.end_date)
                }
            })
            return jsonify({'error': 'End date must be after start date'}), 400

        db.session.commit()

        logger.info('Trip updated successfully', extra={
            'extra_data': {
                'user_id': user_id,
                'trip_id': trip_id,
                'updated_fields': list(data.keys())
            }
        })

        return jsonify(trip.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        logger.error('Trip update failed with exception', exc_info=e, extra={
            'extra_data': {'user_id': user_id, 'trip_id': trip_id}
        })
        return jsonify({'error': 'Failed to update trip'}), 500

@bp.route('/<int:trip_id>', methods=['DELETE'])
@jwt_required()
def delete_trip(trip_id):
    """Delete a trip"""
    user_id = int(get_jwt_identity())

    logger.info('Deleting trip', extra={
        'extra_data': {'user_id': user_id, 'trip_id': trip_id}
    })

    try:
        trip = Trip.query.filter_by(id=trip_id, user_id=user_id).first_or_404()

        db.session.delete(trip)
        db.session.commit()

        logger.info('Trip deleted successfully', extra={
            'extra_data': {
                'user_id': user_id,
                'trip_id': trip_id,
                'destination': trip.destination
            }
        })

        return jsonify({'message': 'Trip deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        logger.error('Trip deletion failed', exc_info=e, extra={
            'extra_data': {'user_id': user_id, 'trip_id': trip_id}
        })
        return jsonify({'error': 'Failed to delete trip'}), 500
