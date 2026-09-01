"""
Professional logging configuration for Flask API
Compatible with ELK Stack, Kibana, CloudWatch, etc.
"""
import os
import logging
import json
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from datetime import datetime
from flask import request, g
import uuid


class FlushingFileHandler(RotatingFileHandler):
    """
    RotatingFileHandler that flushes after every emit.
    Prevents log loss on crashes and enables real-time log monitoring.
    """
    def emit(self, record):
        super().emit(record)
        self.flush()


class FlushingTimedRotatingFileHandler(TimedRotatingFileHandler):
    """
    TimedRotatingFileHandler that flushes after every emit.
    Prevents log loss on crashes and enables real-time log monitoring.
    """
    def emit(self, record):
        super().emit(record)
        self.flush()


class JSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logging
    Compatible with ELK Stack, Datadog, Splunk, etc.
    """
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }

        # Add request context if available
        try:
            if hasattr(g, 'request_id'):
                log_data['request_id'] = g.request_id

            # Add session ID for cross-service correlation
            if hasattr(g, 'session_id'):
                log_data['session_id'] = g.session_id

            if request:
                log_data['request'] = {
                    'method': request.method,
                    'path': request.path,
                    'ip': request.remote_addr,
                    'user_agent': request.headers.get('User-Agent', 'unknown')
                }
        except RuntimeError:
            # Outside request context - this is fine
            pass

        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': self.formatException(record.exc_info)
            }

        # Add custom fields from extra
        if hasattr(record, 'extra_data'):
            log_data['data'] = record.extra_data

        return json.dumps(log_data)


class RequestFormatter(logging.Formatter):
    """
    Human-readable formatter with request context
    For development/debugging
    """
    def format(self, record):
        try:
            request_id = getattr(g, 'request_id', 'no-request')
            session_id = getattr(g, 'session_id', 'no-session')
        except RuntimeError:
            # Outside request context
            request_id = 'no-request'
            session_id = 'no-session'
        record.request_id = request_id
        record.session_id = session_id
        return super().format(record)


def setup_logging(app):
    """
    Configure application logging with rotation and structured output

    Features:
    - JSON logs for production (ELK/Kibana compatible)
    - Human-readable logs for development
    - Rotating file handlers
    - Request ID tracking
    - Different log levels per environment
    """

    # Determine log level based on environment
    env = app.config.get('ENV', 'production')
    if env == 'development':
        log_level = logging.DEBUG
        use_json = False
    else:
        log_level = logging.INFO
        use_json = True

    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)

    # Remove default handlers
    app.logger.handlers.clear()
    app.logger.setLevel(log_level)

    # === Console Handler ===
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)

    if use_json:
        console_handler.setFormatter(JSONFormatter())
    else:
        console_formatter = RequestFormatter(
            '[%(asctime)s] [req:%(request_id)s] [sess:%(session_id)s] %(levelname)s in %(module)s: %(message)s'
        )
        console_handler.setFormatter(console_formatter)

    app.logger.addHandler(console_handler)

    # === Application Log File (Rotating by size) ===
    app_log_file = os.path.join(log_dir, 'app.log')
    app_file_handler = FlushingFileHandler(
        app_log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=10  # Keep 10 backup files
    )
    app_file_handler.setLevel(log_level)
    app_file_handler.setFormatter(JSONFormatter() if use_json else RequestFormatter(
        '[%(asctime)s] [req:%(request_id)s] [sess:%(session_id)s] %(levelname)s: %(message)s'
    ))
    app.logger.addHandler(app_file_handler)

    # === Error Log File (Rotating by time - daily) ===
    error_log_file = os.path.join(log_dir, 'error.log')
    error_file_handler = FlushingTimedRotatingFileHandler(
        error_log_file,
        when='midnight',
        interval=1,
        backupCount=30  # Keep 30 days of error logs
    )
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(JSONFormatter())
    app.logger.addHandler(error_file_handler)

    # === Access Log File (Rotating daily) ===
    access_log_file = os.path.join(log_dir, 'access.log')
    access_file_handler = FlushingTimedRotatingFileHandler(
        access_log_file,
        when='midnight',
        interval=1,
        backupCount=7  # Keep 7 days of access logs
    )
    access_file_handler.setLevel(logging.INFO)
    access_file_handler.setFormatter(JSONFormatter())

    # Create access logger
    access_logger = logging.getLogger('access')
    access_logger.setLevel(logging.INFO)
    access_logger.addHandler(access_file_handler)
    access_logger.propagate = False

    app.logger.info('Logging configured', extra={
        'extra_data': {
            'log_level': logging.getLevelName(log_level),
            'log_dir': log_dir,
            'json_format': use_json,
            'environment': env
        }
    })

    return access_logger


def log_request(app, access_logger):
    """
    Middleware to log all incoming requests with performance metrics
    """
    import time

    @app.before_request
    def before_request():
        g.request_id = str(uuid.uuid4())
        g.start_time = time.time()

        # Capture session ID from frontend for cross-service correlation
        g.session_id = request.headers.get('X-Session-ID', 'no-session')

        app.logger.debug('Request started', extra={
            'extra_data': {
                'method': request.method,
                'path': request.path,
                'query_string': request.query_string.decode('utf-8'),
                'remote_addr': request.remote_addr,
                'session_id': g.session_id
            }
        })

    @app.after_request
    def after_request(response):
        if hasattr(g, 'start_time'):
            duration_ms = (time.time() - g.start_time) * 1000

            # Log to access logger
            access_logger.info('Request completed', extra={
                'extra_data': {
                    'request_id': g.request_id,
                    'session_id': g.session_id,
                    'method': request.method,
                    'path': request.path,
                    'status_code': response.status_code,
                    'duration_ms': round(duration_ms, 2),
                    'remote_addr': request.remote_addr,
                    'user_agent': request.headers.get('User-Agent', 'unknown')
                }
            })

            # Log slow requests as warnings
            if duration_ms > 1000:
                app.logger.warning('Slow request detected', extra={
                    'extra_data': {
                        'duration_ms': round(duration_ms, 2),
                        'path': request.path,
                        'method': request.method
                    }
                })

        return response

    @app.teardown_request
    def teardown_request(exception=None):
        if exception:
            app.logger.error('Request failed with exception', exc_info=exception, extra={
                'extra_data': {
                    'path': request.path,
                    'method': request.method
                }
            })


def get_logger(name):
    """
    Get a logger instance with the application's configuration
    Usage: logger = get_logger(__name__)
    """
    return logging.getLogger(name)
