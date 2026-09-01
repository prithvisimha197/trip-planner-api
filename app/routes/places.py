from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Trip, Place
from app.logging_config import get_logger

bp = Blueprint('places', __name__, url_prefix='/api')
logger = get_logger(__name__)

@bp.route('/trips/<int:trip_id>/places', methods=['GET'])
@jwt_required()
def get_trip_places(trip_id):
    """Get all places for a trip with filtering and pagination"""
    user_id = int(get_jwt_identity())

    logger.info('Fetching places for trip', extra={
        'extra_data': {'user_id': user_id, 'trip_id': trip_id}
    })

    try:
        # Verify trip belongs to user
        trip = Trip.query.filter_by(id=trip_id, user_id=user_id).first_or_404()

        # Get query parameters
        completed_param = request.args.get('completed')
        completed = None
        if completed_param is not None:
            completed = completed_param.lower() == 'true'

        page = request.args.get('page', 1, type=int)
        limit = min(request.args.get('limit', 50, type=int), 100)
        search = request.args.get('search', '')

        # Base query
        query = Place.query.filter_by(trip_id=trip_id)

        # Filter by completion status
        if completed is not None:
            query = query.filter_by(completed=completed)

        # Search filter
        if search:
            query = query.filter(Place.name.ilike(f'%{search}%'))

        # Order by creation date
        query = query.order_by(Place.created_at.asc())

        # Pagination
        paginated = query.paginate(page=page, per_page=limit, error_out=False)

        logger.info('Places retrieved successfully', extra={
            'extra_data': {
                'user_id': user_id,
                'trip_id': trip_id,
                'count': len(paginated.items),
                'total': paginated.total
            }
        })

        return jsonify({
            'tripId': trip_id,
            'data': [place.to_dict() for place in paginated.items],
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
        logger.error('Failed to fetch places', exc_info=e, extra={
            'extra_data': {'user_id': user_id, 'trip_id': trip_id}
        })
        return jsonify({'error': 'Failed to fetch places'}), 500

@bp.route('/trips/<int:trip_id>/places', methods=['POST'])
@jwt_required()
def create_place(trip_id):
    """Add a new place to a trip"""
    user_id = int(get_jwt_identity())

    logger.info('Creating place', extra={
        'extra_data': {
            'user_id': user_id,
            'trip_id': trip_id,
            'name': request.get_json().get('name', 'unknown') if request.get_json() else 'unknown'
        }
    })

    try:
        # Verify trip belongs to user
        trip = Trip.query.filter_by(id=trip_id, user_id=user_id).first_or_404()

        data = request.get_json()

        if not data.get('name'):
            logger.warning('Place creation failed: missing name', extra={
                'extra_data': {'user_id': user_id, 'trip_id': trip_id}
            })
            return jsonify({'error': 'Place name is required'}), 400

        place = Place(
            trip_id=trip_id,
            name=data['name'],
            completed=data.get('completed', False)
        )

        db.session.add(place)
        db.session.commit()

        logger.info('Place created successfully', extra={
            'extra_data': {
                'user_id': user_id,
                'trip_id': trip_id,
                'place_id': place.id,
                'name': place.name
            }
        })

        return jsonify(place.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        logger.error('Place creation failed', exc_info=e, extra={
            'extra_data': {'user_id': user_id, 'trip_id': trip_id}
        })
        return jsonify({'error': 'Failed to create place'}), 500

@bp.route('/places/<int:place_id>', methods=['GET'])
@jwt_required()
def get_place(place_id):
    """Get a single place"""
    user_id = int(get_jwt_identity())

    logger.info('Fetching place', extra={
        'extra_data': {'user_id': user_id, 'place_id': place_id}
    })

    try:
        place = Place.query.get_or_404(place_id)

        # Verify place belongs to user's trip
        if place.trip.user_id != user_id:
            logger.warning('Unauthorized place access attempt', extra={
                'extra_data': {
                    'user_id': user_id,
                    'place_id': place_id,
                    'owner_id': place.trip.user_id
                }
            })
            return jsonify({'error': 'Unauthorized'}), 403

        logger.info('Place retrieved successfully', extra={
            'extra_data': {'user_id': user_id, 'place_id': place_id}
        })

        return jsonify(place.to_dict()), 200
    except Exception as e:
        logger.error('Failed to fetch place', exc_info=e, extra={
            'extra_data': {'user_id': user_id, 'place_id': place_id}
        })
        raise

@bp.route('/places/<int:place_id>', methods=['PUT', 'PATCH'])
@jwt_required()
def update_place(place_id):
    """Update a place (toggle completed, edit name)"""
    user_id = int(get_jwt_identity())

    logger.info('Updating place', extra={
        'extra_data': {'user_id': user_id, 'place_id': place_id}
    })

    try:
        place = Place.query.get_or_404(place_id)

        # Verify place belongs to user's trip
        if place.trip.user_id != user_id:
            logger.warning('Unauthorized place update attempt', extra={
                'extra_data': {
                    'user_id': user_id,
                    'place_id': place_id,
                    'owner_id': place.trip.user_id
                }
            })
            return jsonify({'error': 'Unauthorized'}), 403

        data = request.get_json()

        if 'name' in data:
            place.name = data['name']
        if 'completed' in data:
            place.completed = data['completed']

        db.session.commit()

        logger.info('Place updated successfully', extra={
            'extra_data': {
                'user_id': user_id,
                'place_id': place_id,
                'updated_fields': list(data.keys())
            }
        })

        return jsonify(place.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        logger.error('Place update failed', exc_info=e, extra={
            'extra_data': {'user_id': user_id, 'place_id': place_id}
        })
        return jsonify({'error': 'Failed to update place'}), 500

@bp.route('/places/<int:place_id>', methods=['DELETE'])
@jwt_required()
def delete_place(place_id):
    """Delete a place"""
    user_id = int(get_jwt_identity())

    logger.info('Deleting place', extra={
        'extra_data': {'user_id': user_id, 'place_id': place_id}
    })

    try:
        place = Place.query.get_or_404(place_id)

        # Verify place belongs to user's trip
        if place.trip.user_id != user_id:
            logger.warning('Unauthorized place deletion attempt', extra={
                'extra_data': {
                    'user_id': user_id,
                    'place_id': place_id,
                    'owner_id': place.trip.user_id
                }
            })
            return jsonify({'error': 'Unauthorized'}), 403

        place_name = place.name  # Store before deletion

        db.session.delete(place)
        db.session.commit()

        logger.info('Place deleted successfully', extra={
            'extra_data': {
                'user_id': user_id,
                'place_id': place_id,
                'name': place_name
            }
        })

        return jsonify({'message': 'Place deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        logger.error('Place deletion failed', exc_info=e, extra={
            'extra_data': {'user_id': user_id, 'place_id': place_id}
        })
        return jsonify({'error': 'Failed to delete place'}), 500
