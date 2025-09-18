import logging
import sys
from typing import Dict, Any
from datetime import datetime
import json
import traceback
from pathlib import Path

from app.core.config import settings


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add extra fields if present
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        if hasattr(record, 'account_id'):
            log_entry['account_id'] = record.account_id
        if hasattr(record, 'duration_ms'):
            log_entry['duration_ms'] = record.duration_ms
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
        
        return json.dumps(log_entry, ensure_ascii=False)


def setup_logging() -> None:
    """Setup application logging configuration."""
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler with structured format
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = StructuredFormatter()
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler for application logs
    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_dir / "app.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(console_formatter)
    root_logger.addHandler(file_handler)
    
    # Error file handler
    error_handler = logging.handlers.RotatingFileHandler(
        filename=log_dir / "error.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(console_formatter)
    root_logger.addHandler(error_handler)
    
    # Silence noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get logger instance with structured formatting."""
    return logging.getLogger(name)


class LoggerMixin:
    """Mixin class to add logging capabilities to any class."""
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger instance for this class."""
        return get_logger(self.__class__.__module__ + "." + self.__class__.__name__)
    
    def log_info(self, message: str, **kwargs) -> None:
        """Log info message with extra context."""
        self.logger.info(message, extra=kwargs)
    
    def log_error(self, message: str, exc_info: bool = True, **kwargs) -> None:
        """Log error message with exception info."""
        self.logger.error(message, exc_info=exc_info, extra=kwargs)
    
    def log_warning(self, message: str, **kwargs) -> None:
        """Log warning message with extra context."""
        self.logger.warning(message, extra=kwargs)
    
    def log_debug(self, message: str, **kwargs) -> None:
        """Log debug message with extra context."""
        self.logger.debug(message, extra=kwargs)


def log_api_request(request_id: str, method: str, path: str, user_id: str = None) -> None:
    """Log API request with structured data."""
    logger = get_logger("api.request")
    logger.info(
        f"{method} {path}",
        extra={
            "request_id": request_id,
            "method": method,
            "path": path,
            "user_id": user_id
        }
    )


def log_api_response(request_id: str, status_code: int, duration_ms: float) -> None:
    """Log API response with performance metrics."""
    logger = get_logger("api.response")
    logger.info(
        f"Response {status_code}",
        extra={
            "request_id": request_id,
            "status_code": status_code,
            "duration_ms": duration_ms
        }
    )


def log_instagram_api_call(endpoint: str, account_id: int = None, success: bool = True, error: str = None) -> None:
    """Log Instagram API calls for monitoring."""
    logger = get_logger("instagram.api")
    
    if success:
        logger.info(
            f"Instagram API call successful: {endpoint}",
            extra={"endpoint": endpoint, "account_id": account_id}
        )
    else:
        logger.error(
            f"Instagram API call failed: {endpoint} - {error}",
            extra={"endpoint": endpoint, "account_id": account_id, "error": error}
        )


def log_celery_task(task_name: str, task_id: str, status: str, **kwargs) -> None:
    """Log Celery task execution."""
    logger = get_logger("celery.task")
    logger.info(
        f"Celery task {status}: {task_name}",
        extra={
            "task_name": task_name,
            "task_id": task_id,
            "status": status,
            **kwargs
        }
    )


def log_database_query(query: str, duration_ms: float, rows_affected: int = None) -> None:
    """Log database queries for performance monitoring."""
    logger = get_logger("database.query")
    
    extra_data = {
        "duration_ms": duration_ms,
        "query_type": query.strip().split()[0].upper()
    }
    
    if rows_affected is not None:
        extra_data["rows_affected"] = rows_affected
    
    if duration_ms > 1000:  # Log slow queries
        logger.warning(f"Slow query detected: {query[:100]}...", extra=extra_data)
    else:
        logger.debug(f"Database query: {query[:100]}...", extra=extra_data)


# Initialize logging on module import
setup_logging()
