# Changelog

All notable changes to this project will be documented in this file.

## [v2.0.0] - 2025-09-09

### BREAKING CHANGES
- **Framework Migration**: Complete migration from Flask to FastAPI
  - Replaced Flask, Flasgger, and Flask-SQLAlchemy with FastAPI, Uvicorn, and SQLAlchemy 2.0
  - All endpoints now return FastAPI response models with proper OpenAPI documentation
  - Server changed from Waitress to Uvicorn with hot reload support in debug mode

### Added
- **FastAPI Core Dependencies**:
  - `fastapi==0.104.1` - Modern, fast web framework with automatic OpenAPI documentation
  - `uvicorn[standard]==0.24.0` - ASGI server with WebSocket and HTTP/2 support
  - `pydantic==2.5.0` - Data validation using Python type annotations
  - `pydantic-settings==2.1.0` - Settings management with environment variable support
  - `python-multipart==0.0.6` - Form and file upload support

- **Enhanced API Documentation**: 
  - Interactive OpenAPI documentation at `/docs` (Swagger UI)
  - Alternative documentation at `/redoc` (ReDoc)
  - Comprehensive API categorization with tags: System, App, HTTP, Filesystem, Database, ToDo
  - Detailed response models and error handling

- **Improved Configuration System**:
  - Pydantic-based configuration with type validation
  - Environment variable support with `APP22_` prefix
  - Backward compatibility properties for legacy configuration access
  - Enhanced MongoDB configuration options

- **Modern Route Architecture**:
  - Modular router system with separate files for each functional area
  - FastAPI dependency injection for database sessions
  - Proper async/await support where applicable
  - Type-safe request/response models

- **Enhanced Testing Suite**:
  - Updated to use `httpx` instead of Flask test client
  - `pytest-asyncio` support for async testing
  - Improved test isolation with proper database cleanup
  - Mock-friendly implementations for external dependencies

### Changed
- **Application Structure**:
  - Reorganized routes into separate modules under `app/routes/`
  - Centralized router registration in `app/routes/__init__.py`
  - Database models and setup moved to dedicated `database.py` module
  - Configuration migrated to Pydantic BaseSettings pattern

- **Server Runtime**:
  - Development server now uses Uvicorn with hot reload
  - Production server uses Uvicorn without reload for better performance
  - Removed Waitress dependency in favor of modern ASGI server

- **Database Integration**:
  - Updated to SQLAlchemy 2.0 with modern session management
  - Proper dependency injection for database sessions
  - Enhanced error handling and logging for database operations

- **Docker & Deployment**:
  - Updated Dockerfile to use Python 3.12.3
  - Simplified container entrypoint to use new Uvicorn-based runner
  - Updated Helm charts for FastAPI deployment patterns

### Removed
- **Legacy Flask Dependencies**:
  - `Flask==2.1.2`
  - `flasgger==0.9.7.1` (replaced by FastAPI's built-in OpenAPI)
  - `Flask-SQLAlchemy==2.5.1`
  - `waitress` (replaced by Uvicorn)
  - `greenlet` and other Flask-specific dependencies

- **Obsolete Packages**:
  - Various Flask ecosystem packages no longer needed with FastAPI
  - Legacy configuration patterns and imports

### Fixed
- **Type Safety**: Full type annotations throughout the codebase
- **Error Handling**: Consistent HTTP exception handling with proper status codes
- **Documentation**: All endpoints now have comprehensive documentation
- **Testing**: More reliable test suite with proper async support
- **Configuration**: Robust environment variable parsing and validation

### Migration Notes
- **API Compatibility**: All existing endpoints maintain the same paths and functionality
- **Response Format**: JSON responses now use Pydantic models for consistency
- **Environment Variables**: All `APP22_` prefixed variables continue to work as before
- **Database**: Existing SQLite database files remain compatible
- **Docker**: Container interface remains unchanged, only internal implementation differs

### Performance Improvements
- **Faster Startup**: FastAPI's efficient routing and dependency injection
- **Better Concurrency**: ASGI-based server supports WebSockets and HTTP/2
- **Reduced Memory**: Elimination of Flask's overhead and dependencies
- **Hot Reload**: Development server supports automatic reloading on code changes

[2.0.0]: https://github.com/your-org/app22/releases/tag/v2.0.0
