"""
AI INSTRUCTION: Custom Exception Handling
This file defines custom exceptions and exception handlers.

RULES FOR AI:
1. Use these custom exceptions in services (NOT in routes)
2. Routes should never handle exceptions - middleware does that
3. Add new exception types here as needed
4. Always provide clear error messages

PATTERN: In services, raise exceptions:
  ```python
  if not user:
      raise NotFoundException(f"User {user_id} not found")
  
  if user.email != new_email:
      raise ValidationException("Cannot change email")
  ```

AI: Exception handling is automatic. Just raise these exceptions in services.
"""

from typing import Any, Dict, Optional

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse

# CUSTOM EXCEPTION CLASSES
class BaseAPIException(Exception):
    """
    AI PATTERN: Base Exception Class
    
    All custom exceptions inherit from this.
    This allows us to handle all custom exceptions consistently.
    
    AI: Don't use this directly. Use the specific exceptions below.
    """
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class NotFoundException(BaseAPIException):
    """
    AI PATTERN: Resource Not Found (404)
    
    Use when a requested resource doesn't exist.
    
    EXAMPLES:
    ```python
    # User not found
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundException(f"User with id {user_id} not found")
    
    # Product not found
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise NotFoundException(f"Product {product_id} not found")
    ```
    
    AI: Use this whenever a GET/PUT/DELETE operation can't find the resource.
    """
    
    def __init__(self, message: str = "Resource not found", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            details=details
        )


class ValidationException(BaseAPIException):
    """
    AI PATTERN: Business Logic Validation Error (400)
    
    Use when data is technically valid but violates business rules.
    
    DIFFERENCE FROM PYDANTIC VALIDATION:
    - Pydantic validates data structure (required fields, types)
    - This validates business logic (duplicate email, insufficient stock)
    
    EXAMPLES:
    ```python
    # Duplicate email
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise ValidationException("Email already registered")
    
    # Insufficient stock
    if product.stock < quantity:
        raise ValidationException(
            f"Insufficient stock. Available: {product.stock}",
            details={"available": product.stock, "requested": quantity}
        )
    
    # Invalid state transition
    if order.status == "delivered":
        raise ValidationException("Cannot cancel delivered order")
    ```
    
    AI: Use this for business rule violations, not data format issues.
    """
    
    def __init__(self, message: str = "Validation error", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )


class UnauthorizedException(BaseAPIException):
    """
    AI PATTERN: Authentication Required (401)
    
    Use when user is not authenticated.
    
    EXAMPLES:
    ```python
    # No token provided
    if not token:
        raise UnauthorizedException("Authentication required")
    
    # Invalid token
    try:
        payload = decode_token(token)
    except JWTError:
        raise UnauthorizedException("Invalid authentication token")
    
    # Expired token
    if token_expired(token):
        raise UnauthorizedException("Token has expired")
    ```
    
    AI: Use this when authentication is missing or invalid.
    This is different from ForbiddenException (403).
    """
    
    def __init__(self, message: str = "Authentication required", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details
        )


class ForbiddenException(BaseAPIException):
    """
    AI PATTERN: Permission Denied (403)
    
    Use when user is authenticated but lacks permission.
    
    EXAMPLES:
    ```python
    # Not the owner
    if post.user_id != current_user.id:
        raise ForbiddenException("You can only edit your own posts")
    
    # Wrong role
    if current_user.role != "admin":
        raise ForbiddenException("Admin access required")
    
    # Banned user
    if current_user.is_banned:
        raise ForbiddenException("Your account has been banned")
    ```
    
    AI: Use this when user is authenticated but not authorized.
    401 = "who are you?" | 403 = "I know who you are, but you can't do this"
    """
    
    def __init__(self, message: str = "Permission denied", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            details=details
        )


class ConflictException(BaseAPIException):
    """
    AI PATTERN: Resource Conflict (409)
    
    Use when operation conflicts with current resource state.
    
    EXAMPLES:
    ```python
    # Duplicate unique value
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        raise ConflictException(f"Username '{username}' already exists")
    
    # Resource in use
    if category.products.count() > 0:
        raise ConflictException("Cannot delete category with existing products")
    
    # Concurrent modification
    if product.version != expected_version:
        raise ConflictException("Product was modified by another user")
    ```
    
    AI: Use this for conflicts that aren't simple validation errors.
    """
    
    def __init__(self, message: str = "Resource conflict", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            details=details
        )


class InternalServerException(BaseAPIException):
    """
    AI PATTERN: Internal Server Error (500)
    
    Use when something unexpected happens on the server.
    
    EXAMPLES:
    ```python
    # External service failure
    try:
        response = external_api.call()
    except Exception as e:
        raise InternalServerException(f"External service error: {str(e)}")
    
    # Unexpected state
    if calculated_total < 0:
        raise InternalServerException("Calculated negative total - data corruption?")
    ```
    
    AI: Use sparingly. Most errors should be more specific.
    This indicates something we didn't anticipate went wrong.
    """
    
    def __init__(self, message: str = "Internal server error", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )


# EXCEPTION HANDLERS
async def base_api_exception_handler(request: Request, exc: BaseAPIException) -> JSONResponse:
    """
    AI PATTERN: Custom Exception Handler
    
    This function catches all custom exceptions and returns consistent JSON responses.
    
    RESPONSE FORMAT:
    {
        "error": {
            "message": "User not found",
            "details": {"user_id": 123},
            "path": "/api/v1/users/123",
            "timestamp": "2024-01-20T10:30:00"
        }
    }
    
    AI: This is registered in main.py. Don't modify unless changing error format.
    """
    from datetime import datetime
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.message,
                "details": exc.details,
                "path": str(request.url.path),
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
     AI PATTERN: Catch-All Exception Handler
    
    This catches any unhandled exceptions (Python exceptions, not our custom ones).
    
    WHY THIS EXISTS:
    - Prevents ugly stack traces from reaching users
    - Logs the error for debugging
    - Returns user-friendly error message
    
    AI: This should rarely be triggered if you use custom exceptions properly.
    """
    import logging
    
    logger = logging.getLogger(__name__)
    logger.exception("Unhandled exception occurred", exc_info=exc)
    
    from datetime import datetime
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "message": "An unexpected error occurred",
                "details": {},
                "path": str(request.url.path),
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    )


# AI USAGE EXAMPLES


"""
🤖 HOW AI SHOULD USE THIS FILE:

1. IN SERVICES (Most Common):
   ```python
   from app.core.exceptions import NotFoundException, ValidationException
   
   class UserService:
       def get_user(self, db: Session, user_id: int):
           user = db.query(User).filter(User.id == user_id).first()
           if not user:
               raise NotFoundException(f"User {user_id} not found")
           return user
       
       def create_user(self, db: Session, email: str):
           existing = db.query(User).filter(User.email == email).first()
           if existing:
               raise ValidationException("Email already registered")
           # ... create user
   ```

2. WITH ADDITIONAL DETAILS:
   ```python
   from app.core.exceptions import ValidationException
   
   if product.stock < quantity:
       raise ValidationException(
           "Insufficient stock",
           details={
               "product_id": product.id,
               "available": product.stock,
               "requested": quantity
           }
       )
   ```

3. IN MAIN.PY (Register Handlers):
   ```python
   from fastapi import FastAPI
   from app.core.exceptions import (
       BaseAPIException,
       base_api_exception_handler,
       generic_exception_handler
   )
   
   app = FastAPI()
   
   app.add_exception_handler(BaseAPIException, base_api_exception_handler)
   app.add_exception_handler(Exception, generic_exception_handler)
   ```

4. ADDING NEW EXCEPTION TYPES:
   If you need a new specific exception:
   ```python
   class RateLimitException(BaseAPIException):
       def __init__(self, message: str = "Rate limit exceeded", details=None):
           super().__init__(
               message=message,
               status_code=status.HTTP_429_TOO_MANY_REQUESTS,
               details=details
           )
   ```

AI DECISION TREE - Which Exception to Use:
- Resource not found? → NotFoundException
- Business rule violation? → ValidationException
- Not logged in? → UnauthorizedException
- Logged in but no permission? → ForbiddenException
- Duplicate/conflict? → ConflictException
- Server/external error? → InternalServerException

AI ANTI-PATTERNS (DO NOT DO):
Raising exceptions in routes (do it in services)
Returning error responses manually in routes
Using HTTPException for business logic errors
Swallowing exceptions without re-raising
Using generic Exception instead of specific ones
"""