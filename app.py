import os
from app import create_app, db

app = create_app(os.getenv('FLASK_ENV', 'development'))
logger = app.logger

@app.route('/')
def index():
    logger.debug('Root endpoint accessed')
    return {
        'name': 'Trip Planner API',
        'version': '1.0.0',
        'status': 'running'
    }

@app.route('/health')
def health():
    """Health check endpoint for K8s liveness/readiness probes"""
    import time
    from sqlalchemy import text

    logger.info('Health check initiated')

    start_time = time.time()
    health_status = {
        'status': 'healthy',
        'timestamp': time.time(),
        'checks': {}
    }

    # Check 1: Database Connection
    try:
        logger.debug('Checking database connection...')
        db_start = time.time()
        db.session.execute(text('SELECT 1'))
        db_duration = (time.time() - db_start) * 1000  # Convert to ms

        health_status['checks']['database'] = {
            'status': 'healthy',
            'response_time_ms': round(db_duration, 2)
        }
        logger.info('Database health check passed', extra={
            'extra_data': {
                'response_time_ms': round(db_duration, 2),
                'check': 'database'
            }
        })
    except Exception as e:
        db_duration = (time.time() - db_start) * 1000 if 'db_start' in locals() else 0
        health_status['status'] = 'unhealthy'
        health_status['checks']['database'] = {
            'status': 'unhealthy',
            'error': str(e),
            'response_time_ms': round(db_duration, 2)
        }
        logger.error('Database health check failed', exc_info=e, extra={
            'extra_data': {
                'error': str(e),
                'check': 'database',
                'response_time_ms': round(db_duration, 2)
            }
        })

    # Check 2: Application Status
    try:
        logger.debug('Checking application status...')
        health_status['checks']['application'] = {
            'status': 'healthy',
            'environment': os.getenv('FLASK_ENV', 'development'),
            'debug_mode': app.debug
        }
        logger.debug('Application health check passed', extra={
            'extra_data': {
                'environment': os.getenv('FLASK_ENV', 'development'),
                'debug_mode': app.debug,
                'check': 'application'
            }
        })
    except Exception as e:
        health_status['status'] = 'unhealthy'
        health_status['checks']['application'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
        logger.error('Application health check failed', exc_info=e, extra={
            'extra_data': {'error': str(e), 'check': 'application'}
        })

    # Calculate total health check duration
    total_duration = (time.time() - start_time) * 1000
    health_status['total_response_time_ms'] = round(total_duration, 2)

    # Determine HTTP status code
    http_status = 200 if health_status['status'] == 'healthy' else 503

    # Log final health check result
    if health_status['status'] == 'healthy':
        logger.info('Health check completed: HEALTHY', extra={
            'extra_data': {
                'status': 'healthy',
                'total_response_time_ms': round(total_duration, 2),
                'checks_passed': sum(1 for c in health_status['checks'].values() if c['status'] == 'healthy'),
                'total_checks': len(health_status['checks'])
            }
        })
    else:
        logger.warning('Health check completed: UNHEALTHY', extra={
            'extra_data': {
                'status': 'unhealthy',
                'total_response_time_ms': round(total_duration, 2),
                'failed_checks': [k for k, v in health_status['checks'].items() if v['status'] == 'unhealthy']
            }
        })

    return health_status, http_status

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    logger.info(f'Starting Flask app on port {port}', extra={
        'extra_data': {
            'port': port,
            'environment': os.getenv('FLASK_ENV', 'development')
        }
    })
    app.run(host='0.0.0.0', port=port, debug=True)
