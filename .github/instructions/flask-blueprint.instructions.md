---
applyTo: 'src/webchat/blueprints/**'
---
# Flask Blueprint Template - Best Practices Guide

## Overview

This template provides a comprehensive foundation for creating modular, maintainable Flask blueprints following industry best practices. It demonstrates proper separation of concerns, security patterns, testing strategies, and performance optimization techniques suitable for any feature domain.

## GitHub Copilot Optimization Guidelines

### For Optimal Copilot Performance:
1. **Use descriptive variable and function names** - Copilot understands intent better
2. **Include type hints everywhere** - Helps Copilot suggest accurate code
3. **Write clear docstrings** - Copilot uses them to understand context
4. **Follow consistent patterns** - Copilot learns from repetitive structures
5. **Use standardized file structures** - Copilot expects common patterns
6. **Include examples in comments** - Helps Copilot generate similar code

### Copilot-Friendly Code Patterns:
```python
# GOOD: Clear intent, typed, documented
def create_user_account(self, user_data: Dict[str, Any]) -> ServiceResult:
    """
    Create a new user account with validation and business rules.
    
    Args:
        user_data: Dictionary containing username, email, password
        
    Returns:
        ServiceResult with success status and user data or error details
        
    Example:
        result = service.create_user_account({
            'username': 'john_doe',
            'email': 'john@example.com', 
            'password': 'secure_password'
        })
    """
    
# BAD: Unclear intent, no types, no documentation
def create(self, data):
    pass
```

### Copilot-Optimized Naming Conventions:
- **Classes**: `UserManagementService`, `EmailValidationError`, `DatabaseConnectionPool`
- **Methods**: `validate_user_email`, `calculate_order_total`, `send_welcome_notification`
- **Variables**: `user_registration_data`, `validation_error_messages`, `database_query_result`
- **Constants**: `MAX_LOGIN_ATTEMPTS`, `DEFAULT_PAGE_SIZE`, `EMAIL_VALIDATION_REGEX`

### Template Placeholders for Copilot:
```python
# TODO: Implement user authentication logic
# PATTERN: Standard CRUD operations for [ENTITY_NAME]
# EXAMPLE: Similar to UserService.create_user_account()
# OPTIMIZE: Add caching for frequently accessed data
# VALIDATE: Check user permissions before [ACTION]
```

**KEY PRINCIPLE: Routes must NEVER contain business logic. All business logic belongs in the service layer or common utilities.**

## Performance Optimization Requirements

### 1. **Database Performance**
- **Query Optimization**: Use SQLAlchemy query optimization patterns
- **Indexing**: Add database indexes on frequently queried fields
- **Lazy Loading**: Implement lazy loading for relationships
- **Connection Pooling**: Configure database connection pooling
- **Query Monitoring**: Log slow queries for optimization

```python
# filepath: feature_blueprint/models.py
"""
Database models with performance optimizations.
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Index
from sqlalchemy.orm import relationship, defer

class FeatureModel(db.Model):
    """Model with performance optimizations."""
    
    __tablename__ = 'features'
    
    # Add indexes for frequently queried fields
    __table_args__ = (
        Index('idx_feature_category_active', 'category', 'is_active'),
        Index('idx_feature_created_at', 'created_at'),
        Index('idx_feature_name', 'name'),
    )
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False, index=True)
    priority = Column(Integer, default=5, index=True)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Lazy load large text fields
    large_content = defer(Column(Text))
    
    @classmethod
    def get_active_by_category(cls, category: str):
        """Optimized query for active features by category."""
        return cls.query.filter(
            cls.category == category,
            cls.is_active == True
        ).options(defer('large_content'))
    
    @classmethod
    def get_with_pagination(cls, page: int = 1, per_page: int = 20):
        """Get features with pagination for performance."""
        return cls.query.filter_by(is_active=True).paginate(
            page=page, per_page=per_page, error_out=False
        )
```

### 2. **Caching Strategy**
- **Application-Level Caching**: Use Flask-Caching for expensive operations
- **Database Query Caching**: Cache frequently used queries
- **Template Caching**: Cache rendered templates when appropriate
- **Static Asset Caching**: Configure browser caching for static files

```python
# filepath: feature_blueprint/services.py
"""
Service layer with caching implementation.
"""
from flask_caching import Cache
from functools import wraps
import hashlib
import json

cache = Cache()

def cache_key(*args, **kwargs):
    """Generate cache key from arguments."""
    key_data = str(args) + str(sorted(kwargs.items()))
    return hashlib.md5(key_data.encode()).hexdigest()

def cached_result(timeout=300):
    """Decorator for caching service method results."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = f"{func.__name__}_{cache_key(*args, **kwargs)}"
            
            # Try to get from cache
            result = cache.get(key)
            if result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(key, result, timeout=timeout)
            logger.debug(f"Cache miss for {func.__name__}, result cached")
            
            return result
        return wrapper
    return decorator

class FeatureService:
    """Service class with performance optimizations."""
    
    @cached_result(timeout=600)  # Cache for 10 minutes
    def get_feature_statistics(self) -> Dict[str, Any]:
        """
        Get feature statistics with caching.
        Expensive calculation cached for performance.
        """
        logger.info("Calculating feature statistics")
        start_time = time.time()
        
        try:
            # Expensive database operations
            total_features = FeatureModel.query.count()
            active_features = FeatureModel.query.filter_by(is_active=True).count()
            categories = db.session.query(FeatureModel.category).distinct().count()
            
            # Complex calculations
            stats = {
                'total_features': total_features,
                'active_features': active_features,
                'inactive_features': total_features - active_features,
                'total_categories': categories,
                'activity_rate': (active_features / total_features) * 100 if total_features > 0 else 0,
                'last_updated': datetime.utcnow().isoformat()
            }
            
            # Log performance metrics
            execution_time = time.time() - start_time
            logger.info(f"Statistics calculation completed in {execution_time:.2f}s")
            
            return stats
            
        except Exception as e:
            logger.error(f"Error calculating statistics: {e}")
            raise
    
    def get_feature_data(self, filters: Optional[Dict[str, Any]] = None, 
                        page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """
        Get feature data with pagination and performance monitoring.
        """
        start_time = time.time()
        logger.info(f"Retrieving feature data - Page: {page}, Per page: {per_page}")
        
        try:
            # Build optimized query
            query = FeatureModel.query.options(defer('large_content'))
            
            # Apply filters efficiently
            if filters:
                query = self._apply_filters_optimized(query, filters)
            
            # Use pagination for performance
            pagination = query.paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            # Process results
            data = {
                'items': [item.to_dict() for item in pagination.items],
                'total_count': pagination.total,
                'page': page,
                'per_page': per_page,
                'total_pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Log performance metrics
            execution_time = time.time() - start_time
            logger.info(f"Retrieved {len(pagination.items)} items in {execution_time:.2f}s")
            
            return data
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Error retrieving feature data after {execution_time:.2f}s: {e}")
            raise
    
    def _apply_filters_optimized(self, query, filters: Dict[str, Any]):
        """Apply filters with optimized database queries."""
        if 'category' in filters and filters['category']:
            query = query.filter(FeatureModel.category == filters['category'])
        
        if 'is_active' in filters and filters['is_active'] is not None:
            query = query.filter(FeatureModel.is_active == filters['is_active'])
        
        if 'search' in filters and filters['search']:
            search_term = f"%{filters['search']}%"
            query = query.filter(
                FeatureModel.name.ilike(search_term) |
                FeatureModel.description.ilike(search_term)
            )
        
        return query
```

### 3. **Asynchronous Operations**
- **Background Tasks**: Use Celery for long-running operations
- **Async Processing**: Implement async patterns for I/O operations
- **Task Queues**: Queue heavy processing tasks
- **Progress Tracking**: Provide progress updates for long operations

```python
# filepath: feature_blueprint/tasks.py
"""
Background tasks for performance optimization.
"""
from celery import Celery
from typing import Dict, Any
import logging

celery = Celery('feature_tasks')
logger = logging.getLogger(__name__)

@celery.task(bind=True)
def process_bulk_features(self, feature_data_list: List[Dict[str, Any]]):
    """
    Process multiple features in background for performance.
    
    :param feature_data_list: List of feature data to process
    :return: Processing results
    """
    total_items = len(feature_data_list)
    processed_items = 0
    failed_items = 0
    
    logger.info(f"Starting bulk processing of {total_items} features")
    
    for i, feature_data in enumerate(feature_data_list):
        try:
            # Update progress
            progress = int((i / total_items) * 100)
            self.update_state(
                state='PROGRESS',
                meta={'current': i, 'total': total_items, 'progress': progress}
            )
            
            # Process individual feature
            feature_service = FeatureService()
            result = feature_service.create_feature_item(feature_data)
            
            if result['success']:
                processed_items += 1
                logger.debug(f"Processed feature: {feature_data.get('name')}")
            else:
                failed_items += 1
                logger.warning(f"Failed to process feature: {result['error']}")
                
        except Exception as e:
            failed_items += 1
            logger.error(f"Error processing feature {i}: {e}")
    
    # Final results
    results = {
        'total_items': total_items,
        'processed_items': processed_items,
        'failed_items': failed_items,
        'success_rate': (processed_items / total_items) * 100 if total_items > 0 else 0
    }
    
    logger.info(f"Bulk processing completed: {results}")
    return results

@celery.task
def cleanup_inactive_features():
    """Background task to cleanup inactive features."""
    logger.info("Starting feature cleanup task")
    
    try:
        # Cleanup logic here
        feature_service = FeatureService()
        result = feature_service.cleanup_inactive_features()
        
        logger.info(f"Cleanup completed: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Cleanup task failed: {e}")
        raise
```

## Data Logging Requirements

### 1. **Comprehensive Logging Strategy**
- **Structured Logging**: Use JSON format for log entries
- **Log Levels**: Implement appropriate log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **Performance Logging**: Log execution times and resource usage
- **User Activity Logging**: Track user actions for analytics
- **Error Tracking**: Detailed error logging with context

```python
# filepath: src/common/logging_utils.py
"""
Enhanced logging utilities for performance and data tracking.
"""
import logging
import json
import time
import functools
from datetime import datetime
from typing import Dict, Any, Optional
from flask import request, g, current_user

class PerformanceLogger:
    """Logger for performance metrics and data tracking."""
    
    def __init__(self, logger_name: str = None):
        self.logger = logging.getLogger(logger_name or __name__)
        self.setup_structured_logging()
    
    def setup_structured_logging(self):
        """Configure structured JSON logging."""
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler for structured logs
        file_handler = logging.FileHandler('logs/performance.log')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
    
    def log_performance_metric(self, operation: str, execution_time: float, 
                             metadata: Optional[Dict[str, Any]] = None):
        """
        Log performance metrics in structured format.
        
        :param operation: Operation name
        :param execution_time: Execution time in seconds
        :param metadata: Additional metadata
        """
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'type': 'performance_metric',
            'operation': operation,
            'execution_time_seconds': execution_time,
            'user_id': getattr(current_user, 'id', None) if current_user else None,
            'request_path': getattr(request, 'path', None) if request else None,
            'metadata': metadata or {}
        }
        
        # Log as WARNING if slow, INFO if normal
        if execution_time > 5.0:  # Slow operation threshold
            self.logger.warning(f"SLOW_OPERATION: {json.dumps(log_data)}")
        elif execution_time > 1.0:  # Medium operation threshold
            self.logger.info(f"MEDIUM_OPERATION: {json.dumps(log_data)}")
        else:
            self.logger.debug(f"FAST_OPERATION: {json.dumps(log_data)}")
    
    def log_user_activity(self, action: str, entity_type: str, entity_id: Optional[int] = None,
                         metadata: Optional[Dict[str, Any]] = None):
        """
        Log user activity for analytics and auditing.
        
        :param action: Action performed (create, read, update, delete, etc.)
        :param entity_type: Type of entity (user, feature, etc.)
        :param entity_id: ID of the entity
        :param metadata: Additional context
        """
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'type': 'user_activity',
            'user_id': getattr(current_user, 'id', None) if current_user else None,
            'action': action,
            'entity_type': entity_type,
            'entity_id': entity_id,
            'ip_address': getattr(request, 'remote_addr', None) if request else None,
            'user_agent': getattr(request, 'user_agent', {}).string if request else None,
            'request_path': getattr(request, 'path', None) if request else None,
            'metadata': metadata or {}
        }
        
        self.logger.info(f"USER_ACTIVITY: {json.dumps(log_data)}")
    
    def log_database_query(self, query_type: str, table_name: str, 
                          execution_time: float, row_count: Optional[int] = None):
        """
        Log database query performance.
        
        :param query_type: Type of query (SELECT, INSERT, UPDATE, DELETE)
        :param table_name: Table name
        :param execution_time: Query execution time
        :param row_count: Number of rows affected/returned
        """
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'type': 'database_query',
            'query_type': query_type,
            'table_name': table_name,
            'execution_time_seconds': execution_time,
            'row_count': row_count,
            'user_id': getattr(current_user, 'id', None) if current_user else None
        }
        
        # Log slow queries as warnings
        if execution_time > 2.0:
            self.logger.warning(f"SLOW_QUERY: {json.dumps(log_data)}")
        else:
            self.logger.debug(f"DB_QUERY: {json.dumps(log_data)}")
    
    def log_error_with_context(self, error: Exception, operation: str, 
                              context: Optional[Dict[str, Any]] = None):
        """
        Log errors with full context for debugging.
        
        :param error: Exception that occurred
        :param operation: Operation being performed
        :param context: Additional context information
        """
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'type': 'error',
            'operation': operation,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'user_id': getattr(current_user, 'id', None) if current_user else None,
            'request_path': getattr(request, 'path', None) if request else None,
            'context': context or {}
        }
        
        self.logger.error(f"ERROR: {json.dumps(log_data)}", exc_info=True)

def performance_monitor(operation_name: str = None):
    """
    Decorator to monitor function performance and log metrics.
    
    :param operation_name: Custom operation name for logging
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            perf_logger = PerformanceLogger()
            operation = operation_name or f"{func.__module__}.{func.__name__}"
            
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Extract metadata from result if available
                metadata = {}
                if isinstance(result, dict) and 'metadata' in result:
                    metadata = result['metadata']
                
                perf_logger.log_performance_metric(operation, execution_time, metadata)
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                perf_logger.log_error_with_context(
                    e, operation, 
                    {'execution_time': execution_time, 'args': str(args), 'kwargs': str(kwargs)}
                )
                raise
                
        return wrapper
    return decorator

def log_user_action(action: str, entity_type: str, entity_id: int = None):
    """
    Decorator to log user actions.
    
    :param action: Action performed
    :param entity_type: Type of entity
    :param entity_id: Entity ID (can be extracted from function args)
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            perf_logger = PerformanceLogger()
            
            # Extract entity_id from function arguments if not provided
            actual_entity_id = entity_id
            if actual_entity_id is None and args:
                # Try to find ID in args (common pattern: first arg is often ID)
                if len(args) > 0 and isinstance(args[0], int):
                    actual_entity_id = args[0]
            
            try:
                result = func(*args, **kwargs)
                
                # Log successful action
                metadata = {'success': True}
                if isinstance(result, dict):
                    metadata.update(result.get('metadata', {}))
                
                perf_logger.log_user_activity(action, entity_type, actual_entity_id, metadata)
                return result
                
            except Exception as e:
                # Log failed action
                perf_logger.log_user_activity(
                    action, entity_type, actual_entity_id, 
                    {'success': False, 'error': str(e)}
                )
                raise
                
        return wrapper
    return decorator
```

### 2. **Service Layer with Logging**

```python
# filepath: feature_blueprint/services.py
"""
Service layer with comprehensive performance and data logging.
"""
from src.common.logging_utils import PerformanceLogger, performance_monitor, log_user_action

class FeatureService:
    """Service class with performance monitoring and data logging."""
    
    def __init__(self) -> None:
        """Initialize service with logging."""
        self.logger = PerformanceLogger(__name__)
        self.cache: Dict[str, Any] = {}
        self.config: Dict[str, Any] = {}
    
    @performance_monitor("feature_creation")
    @log_user_action("create", "feature")
    def create_feature_item(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create feature with performance monitoring and activity logging.
        
        :param data: Feature data dictionary
        :return: Creation result with performance metadata
        """
        start_time = time.time()
        
        try:
            self.logger.log_user_activity(
                "create_feature_start", "feature", 
                metadata={'input_data_size': len(str(data))}
            )
            
            # Validation timing
            validation_start = time.time()
            self._validate_item_data(data)
            validation_time = time.time() - validation_start
            
            # Database operation timing
            db_start = time.time()
            item = FeatureModel(**data)
            db.session.add(item)
            db.session.commit()
            db_time = time.time() - db_start
            
            self.logger.log_database_query("INSERT", "features", db_time, 1)
            
            # Total execution time
            total_time = time.time() - start_time
            
            # Log detailed performance metrics
            self.logger.log_performance_metric(
                "feature_creation_detailed",
                total_time,
                {
                    'validation_time': validation_time,
                    'database_time': db_time,
                    'feature_id': item.id,
                    'feature_name': item.name
                }
            )
            
            return {
                'success': True,
                'feature': item.to_dict(),
                'metadata': {
                    'execution_time': total_time,
                    'validation_time': validation_time,
                    'database_time': db_time
                }
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.log_error_with_context(
                e, "feature_creation", 
                {'input_data': data, 'execution_time': execution_time}
            )
            raise
    
    @performance_monitor("feature_search")
    def search_features(self, criteria: Dict[str, Any], page: int = 1, 
                       per_page: int = 20) -> Dict[str, Any]:
        """
        Search features with comprehensive performance logging.
        
        :param criteria: Search criteria
        :param page: Page number
        :param per_page: Items per page
        :return: Search results with performance data
        """
        search_start = time.time()
        
        try:
            # Log search operation start
            self.logger.log_user_activity(
                "search_features", "feature",
                metadata={
                    'criteria': criteria,
                    'page': page,
                    'per_page': per_page
                }
            )
            
            # Build query with timing
            query_build_start = time.time()
            query = FeatureModel.query.options(defer('large_content'))
            
            # Apply filters
            if criteria.get('category'):
                query = query.filter(FeatureModel.category == criteria['category'])
            
            if criteria.get('search_term'):
                search_pattern = f"%{criteria['search_term']}%"
                query = query.filter(
                    FeatureModel.name.ilike(search_pattern) |
                    FeatureModel.description.ilike(search_pattern)
                )
            
            query_build_time = time.time() - query_build_start
            
            # Execute query with timing
            query_exec_start = time.time()
            pagination = query.paginate(
                page=page, per_page=per_page, error_out=False
            )
            query_exec_time = time.time() - query_exec_start
            
            # Log database query performance
            self.logger.log_database_query(
                "SELECT", "features", query_exec_time, len(pagination.items)
            )
            
            # Process results
            results = [item.to_dict() for item in pagination.items]
            
            total_time = time.time() - search_start
            
            # Log comprehensive search metrics
            self.logger.log_performance_metric(
                "feature_search_complete",
                total_time,
                {
                    'query_build_time': query_build_time,
                    'query_execution_time': query_exec_time,
                    'results_count': len(results),
                    'total_pages': pagination.pages,
                    'criteria': criteria
                }
            )
            
            return {
                'success': True,
                'data': {
                    'items': results,
                    'pagination': {
                        'page': page,
                        'per_page': per_page,
                        'total': pagination.total,
                        'pages': pagination.pages
                    }
                },
                'metadata': {
                    'search_time': total_time,
                    'query_build_time': query_build_time,
                    'query_execution_time': query_exec_time
                }
            }
            
        except Exception as e:
            search_time = time.time() - search_start
            self.logger.log_error_with_context(
                e, "feature_search",
                {'criteria': criteria, 'search_time': search_time}
            )
            raise
```

### 3. **Route Performance Monitoring**

```python
# filepath: feature_blueprint/routes.py
"""
Routes with performance monitoring and request logging.
"""
from src.common.logging_utils import PerformanceLogger
import time

def register_routes(bp: Blueprint) -> None:
    """Register routes with performance monitoring."""
    
    perf_logger = PerformanceLogger(__name__)
    
    @bp.before_request
    def before_request():
        """Log request start and set timing."""
        g.start_time = time.time()
        perf_logger.log_user_activity(
            "request_start", "http_request",
            metadata={
                'method': request.method,
                'path': request.path,
                'args': dict(request.args),
                'content_length': request.content_length
            }
        )
    
    @bp.after_request
    def after_request(response):
        """Log request completion with performance metrics."""
        if hasattr(g, 'start_time'):
            request_time = time.time() - g.start_time
            
            perf_logger.log_performance_metric(
                f"http_request_{request.method}",
                request_time,
                {
                    'path': request.path,
                    'status_code': response.status_code,
                    'content_length': response.content_length,
                    'user_id': getattr(current_user, 'id', None) if current_user else None
                }
            )
            
            # Log slow requests
            if request_time > 2.0:
                perf_logger.logger.warning(
                    f"SLOW_REQUEST: {request.method} {request.path} "
                    f"took {request_time:.2f}s (Status: {response.status_code})"
                )
        
        return response
    
    @bp.route('/')
    def index():
        """Feature dashboard with request timing."""
        try:
            # Service call already has performance monitoring
            result = feature_service.get_dashboard_data()
            
            return render_template(
                'feature_blueprint/index.html',
                **result['data']
            )
            
        except Exception as e:
            perf_logger.log_error_with_context(e, "dashboard_view")
            flash('Error loading dashboard', 'error')
            return render_template('feature_blueprint/index.html')
```

This enhanced template ensures that:

1. **Performance is monitored** at all levels (database, service, route)
2. **Comprehensive logging** captures user activity, performance metrics, and errors
3. **Structured logging** enables easy analysis and monitoring
4. **Database operations** are optimized with indexing and query monitoring
5. **Caching strategies** improve response times for expensive operations
6. **Background tasks** handle long-running operations asynchronously
7. **Clear separation** between HTTP, business logic, and data layers

## Blueprint Architecture

```
feature_blueprint/
├── __init__.py              # Blueprint registration and configuration
├── routes.py               # Route handlers (HTTP ONLY - NO BUSINESS LOGIC)
├── services.py             # Business logic layer
├── models.py               # Data models (SQLAlchemy)
├── forms.py                # Form validation (Flask-WTF)
├── utils.py                # Utility functions
├── api/                    # API endpoints
│   ├── __init__.py
│   └── endpoints.py
├── templates/              # Jinja2 templates
│   └── feature_blueprint/
│       ├── base.html       # Base template
│       ├── index.html      # Main view
│       └── components/     # Reusable components
└── static/                 # Blueprint-specific static files
    ├── css/
    ├── js/
    └── images/
```

### Copilot File Naming Patterns:
- **Services**: `user_management_service.py`, `email_notification_service.py`
- **Models**: `user_model.py`, `order_model.py`, `product_model.py`
- **Forms**: `user_registration_form.py`, `product_search_form.py`
- **API**: `user_api_endpoints.py`, `order_api_endpoints.py`
- **Utils**: `validation_utils.py`, `email_utils.py`, `date_utils.py`

## Entity Management with Common Directory

**All entity management and reusable components should utilize the [`common`](/data/projects/code_workspace/rbcz_doc_poc/rbcz_doc_eval/src/common) directory:**

### Entity Example: User Management

````python
# filepath: src/common/entities/user_entity.py
"""
User entity management using common utilities.
Demonstrates proper entity handling with common directory components.

COPILOT PATTERN: Standard entity management class
TEMPLATE: Replace 'User' with your entity name throughout
EXAMPLE: ProductEntity, OrderEntity, CustomerEntity
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from ..models.user_model import UserModel
from ..validation import EntityValidator
from ..output_manager import OutputManager

logger = logging.getLogger(__name__)

class UserEntity:
    """
    User entity management class using common utilities.
    Centralizes all user-related business logic.
    
    COPILOT PATTERN: Entity class template
    TODO: Implement validation rules specific to User entity
    OPTIMIZE: Add caching for frequently accessed users
    """
    
    def __init__(self) -> None:
        """
        Initialize user entity with common utilities.
        PATTERN: Standard entity initialization
        """
        self.validator = EntityValidator()
        self.output_manager = OutputManager()
    
    def create_user(self, user_data: Dict[str, Any]) -> Optional[UserModel]:
        """
        Create a new user entity.
        
        COPILOT PATTERN: Standard entity creation method
        TEMPLATE: create_[entity_name](self, entity_data: Dict[str, Any])
        VALIDATE: Always validate input data before creation
        
        :param user_data: User data dictionary containing username, email, etc.
        :return: Created UserModel instance or None if validation fails
        :raises: EntityValidationError if data is invalid
        
        Example usage:
            user_entity = UserEntity()
            new_user = user_entity.create_user({
                'username': 'john_doe',
                'email': 'john@example.com',
                'first_name': 'John',
                'last_name': 'Doe'
            })
        """
        try:
            # Validate using common validation
            validation_result = self.validator.validate_entity(user_data, 'user')
            if not validation_result.is_valid:
                logger.error(f"User validation failed: {validation_result.errors}")
                raise EntityValidationError(validation_result.errors)
            
            # Create user
            user = UserModel(
                username=user_data['username'],
                email=user_data['email'],
                first_name=user_data.get('first_name'),
                last_name=user_data.get('last_name')
            )
            
            # Save using common patterns
            saved_user = self._save_entity(user)
            
            # Log using common logging
            logger.info(f"Created user: {saved_user.id} - {saved_user.username}")
            
            return saved_user
            
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise
    
    def get_user_by_id(self, user_id: int) -> Optional[UserModel]:
        """
        Retrieve user by ID with common error handling.
        
        :param user_id: User ID to retrieve
        :return: UserModel instance or None if not found
        """
        try:
            user = UserModel.query.get(user_id)
            if user:
                logger.debug(f"Retrieved user: {user_id}")
            return user
            
        except Exception as e:
            logger.error(f"Error retrieving user {user_id}: {e}")
            return None
    
    def update_user(self, user_id: int, update_data: Dict[str, Any]) -> Optional[UserModel]:
        """
        Update user entity with validation.
        
        :param user_id: User ID to update
        :param update_data: Data to update
        :return: Updated UserModel or None if not found
        """
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return None
            
            # Validate update data
            validation_result = self.validator.validate_partial_entity(update_data, 'user')
            if not validation_result.is_valid:
                raise EntityValidationError(validation_result.errors)
            
            # Update user
            for key, value in update_data.items():
                if hasattr(user, key) and key not in ['id', 'created_at']:
                    setattr(user, key, value)
            
            user.updated_at = datetime.utcnow()
            
            # Save using common patterns
            updated_user = self._save_entity(user)
            logger.info(f"Updated user: {user_id}")
            
            return updated_user
            
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            raise
    
    def delete_user(self, user_id: int) -> bool:
        """
        Delete user entity.
        
        :param user_id: User ID to delete
        :return: True if deleted, False if not found
        """
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False
            
            # Soft delete or hard delete based on business rules
            user.is_active = False
            user.deleted_at = datetime.utcnow()
            
            self._save_entity(user)
            logger.info(f"Deleted user: {user_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {e}")
            raise
    
    def search_users(self, criteria: Dict[str, Any]) -> List[UserModel]:
        """
        Search users with criteria using common utilities.
        
        :param criteria: Search criteria dictionary
        :return: List of matching UserModel instances
        """
        try:
            query = UserModel.query.filter_by(is_active=True)
            
            # Apply search criteria using common query builder
            if 'username' in criteria:
                query = query.filter(UserModel.username.ilike(f"%{criteria['username']}%"))
            
            if 'email' in criteria:
                query = query.filter(UserModel.email.ilike(f"%{criteria['email']}%"))
            
            results = query.all()
            logger.debug(f"Found {len(results)} users matching criteria")
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching users: {e}")
            return []
    
    def _save_entity(self, entity: UserModel) -> UserModel:
        """Save entity using common database patterns."""
        from ..extensions import db
        
        try:
            db.session.add(entity)
            db.session.commit()
            return entity
        except Exception as e:
            db.session.rollback()
            raise

class EntityValidationError(Exception):
    """Custom exception for entity validation errors."""
    pass

## GitHub Copilot Best Practices for Blueprint Development

### 1. **Copilot-Optimized Function Signatures**
```python
# COPILOT PATTERN: Descriptive function names with clear intent
def validate_user_email_address(self, email_address: str) -> EmailValidationResult:
    """Validate email address format and domain."""
    
def calculate_user_account_balance(self, user_id: int, include_pending: bool = False) -> Decimal:
    """Calculate total account balance for user with optional pending transactions."""
    
def send_password_reset_notification(self, user_email: str, reset_token: str) -> NotificationResult:
    """Send password reset email with secure token to user."""
```

### 2. **Copilot-Friendly Code Comments**
```python
# TODO: Implement rate limiting for login attempts
# PATTERN: Standard authentication flow with session management
# EXAMPLE: Similar to UserAuthenticationService.authenticate_user()
# OPTIMIZE: Cache user permissions for better performance
# VALIDATE: Check user has required permissions before proceeding
# SECURITY: Ensure all user input is sanitized and validated
# PERFORMANCE: Consider adding database indexes for this query
# REFACTOR: Extract this logic into a separate utility function
```

### 3. **Structured Error Handling Patterns**
```python
class UserServiceError(Exception):
    """Base exception for user service operations."""
    pass

class UserNotFoundError(UserServiceError):
    """Exception raised when user cannot be found."""
    pass

class UserValidationError(UserServiceError):
    """Exception raised when user data validation fails."""
    pass

# COPILOT PATTERN: Consistent error handling
def get_user_profile_data(self, user_id: int) -> Dict[str, Any]:
    """Get comprehensive user profile data with error handling."""
    try:
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with ID {user_id} not found")
        
        profile_data = self._build_user_profile_response(user)
        return {'success': True, 'data': profile_data}
        
    except UserNotFoundError as e:
        logger.warning(f"User not found: {e}")
        return {'success': False, 'error': 'User not found'}
    except Exception as e:
        logger.error(f"Unexpected error getting user profile: {e}")
        return {'success': False, 'error': 'Internal server error'}
```

### 4. **Database Query Optimization Patterns**
```python
# COPILOT PATTERN: Optimized database queries with clear intent
class UserRepository:
    """Repository for user database operations with performance optimization."""
    
    def get_active_users_by_role(self, role_name: str, limit: int = 100) -> List[UserModel]:
        """Get active users by role with pagination for performance."""
        return UserModel.query.filter(
            UserModel.is_active == True,
            UserModel.role == role_name
        ).options(
            defer('large_profile_data'),  # Lazy load large fields
            joinedload('user_preferences')  # Eager load related data
        ).limit(limit).all()
    
    def search_users_by_criteria(self, search_criteria: UserSearchCriteria) -> PaginatedResult:
        """Search users with multiple criteria and pagination."""
        query = UserModel.query.filter(UserModel.is_active == True)
        
        # Apply search filters systematically
        if search_criteria.username_pattern:
            query = query.filter(UserModel.username.ilike(f"%{search_criteria.username_pattern}%"))
        
        if search_criteria.email_domain:
            query = query.filter(UserModel.email.ilike(f"%@{search_criteria.email_domain}"))
        
        if search_criteria.created_after:
            query = query.filter(UserModel.created_at >= search_criteria.created_after)
        
        return query.paginate(
            page=search_criteria.page,
            per_page=search_criteria.per_page,
            error_out=False
        )
```

### 5. **Service Layer Best Practices**
```python
# COPILOT PATTERN: Service class with clear responsibilities
class UserManagementService:
    """
    Service for managing user operations with business logic.
    
    Responsibilities:
    - User creation and validation
    - User profile management
    - User authentication workflows
    - User permission management
    """
    
    def __init__(self, user_repository: UserRepository, email_service: EmailService):
        """Initialize service with required dependencies."""
        self.user_repository = user_repository
        self.email_service = email_service
        self.logger = logging.getLogger(__name__)
    
    def create_new_user_account(self, registration_data: UserRegistrationData) -> UserCreationResult:
        """
        Create new user account with complete workflow.
        
        Business Rules:
        1. Validate email uniqueness
        2. Check username availability
        3. Enforce password policy
        4. Send welcome email
        5. Create default user preferences
        
        Args:
            registration_data: Complete user registration information
            
        Returns:
            UserCreationResult with success status and user data
        """
        try:
            # Business Rule 1: Check email uniqueness
            if self.user_repository.email_exists(registration_data.email):
                return UserCreationResult.failure("Email already registered")
            
            # Business Rule 2: Check username availability
            if self.user_repository.username_exists(registration_data.username):
                return UserCreationResult.failure("Username not available")
            
            # Business Rule 3: Validate password strength
            password_validation = self._validate_password_strength(registration_data.password)
            if not password_validation.is_valid:
                return UserCreationResult.failure(password_validation.error_message)
            
            # Create user entity
            new_user = self.user_repository.create_user(registration_data)
            
            # Business Rule 4: Send welcome email
            self.email_service.send_welcome_email(new_user.email, new_user.username)
            
            # Business Rule 5: Create default preferences
            self._create_default_user_preferences(new_user.id)
            
            self.logger.info(f"Successfully created user account: {new_user.username}")
            return UserCreationResult.success(new_user)
            
        except Exception as e:
            self.logger.error(f"Error creating user account: {e}")
            return UserCreationResult.failure("Account creation failed")
```

### 6. **Testing Patterns for Copilot**
```python
# COPILOT PATTERN: Comprehensive test structure
class TestUserManagementService:
    """Test suite for UserManagementService with clear test patterns."""
    
    @pytest.fixture
    def user_service(self, mock_user_repository, mock_email_service):
        """Create user service with mocked dependencies."""
        return UserManagementService(
            user_repository=mock_user_repository,
            email_service=mock_email_service
        )
    
    @pytest.fixture
    def valid_registration_data(self):
        """Create valid user registration data for testing."""
        return UserRegistrationData(
            username="test_user_123",
            email="test@example.com",
            password="SecurePassword123!",
            first_name="Test",
            last_name="User"
        )
    
    def test_create_user_account_success(self, user_service, valid_registration_data):
        """Test successful user account creation with all business rules."""
        # Arrange
        user_service.user_repository.email_exists.return_value = False
        user_service.user_repository.username_exists.return_value = False
        
        # Act
        result = user_service.create_new_user_account(valid_registration_data)
        
        # Assert
        assert result.is_success
        assert result.user.username == valid_registration_data.username
        user_service.email_service.send_welcome_email.assert_called_once()
    
    def test_create_user_account_email_already_exists(self, user_service, valid_registration_data):
        """Test user creation failure when email already exists."""
        # Arrange
        user_service.user_repository.email_exists.return_value = True
        
        # Act
        result = user_service.create_new_user_account(valid_registration_data)
        
        # Assert
        assert not result.is_success
        assert "Email already registered" in result.error_message
```

### 7. **Route Handler Patterns**
```python
# COPILOT PATTERN: Clean route handlers with no business logic
@user_blueprint.route('/users/register', methods=['POST'])
def register_new_user():
    """
    Handle user registration form submission.
    HTTP ONLY - all business logic in service layer.
    """
    registration_form = UserRegistrationForm()
    
    # HTTP: Validate form data
    if not registration_form.validate_on_submit():
        return render_template('users/register.html', form=registration_form)
    
    # SERVICE: Delegate all business logic
    registration_result = user_management_service.create_new_user_account(
        registration_form.to_registration_data()
    )
    
    # HTTP: Handle service result
    if registration_result.is_success:
        flash('Account created successfully! Please check your email.', 'success')
        return redirect(url_for('user.login'))
    else:
        flash(registration_result.error_message, 'error')
        return render_template('users/register.html', form=registration_form)

@user_blueprint.route('/api/users/<int:user_id>/profile', methods=['GET'])
@login_required
def get_user_profile_api(user_id: int):
    """
    API endpoint for user profile data.
    Returns JSON response with user profile information.
    """
    # SERVICE: Get profile data with business logic
    profile_result = user_management_service.get_user_profile_data(user_id)
    
    # HTTP: Return JSON response
    if profile_result['success']:
        return jsonify({
            'status': 'success',
            'data': profile_result['data']
        })
    else:
        return jsonify({
            'status': 'error',
            'message': profile_result['error']
        }), 404 if 'not found' in profile_result['error'] else 500
```

This enhanced template ensures that:

1. **Performance is monitored** at all levels (database, service, route)
2. **Comprehensive logging** captures user activity, performance metrics, and errors
3. **Structured logging** enables easy analysis and monitoring
4. **Database operations** are optimized with indexing and query monitoring
5. **Caching strategies** improve response times for expensive operations
6. **Background tasks** handle long-running operations asynchronously
7. **Clear separation** between HTTP, business logic, and data layers
8. **GitHub Copilot optimization** with descriptive names, clear patterns, and structured code