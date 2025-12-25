"""
AI INSTRUCTION: Database Session Management
This file manages database connections and sessions.

RULES FOR AI:
1. Use get_db() for dependency injection in routes
2. NEVER create engine or SessionLocal manually elsewhere
3. Sessions are automatically closed after request
4. This file handles connection pooling automatically

PATTERN: In routes, use dependency injection:
  ```python
  @router.get("/users")
  def get_users(db: Session = Depends(get_db)):
      # db is automatically provided and closed
      users = db.query(User).all()
      return users
  ```

AI: DO NOT modify this file unless changing database connection logic.
"""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings


# DATABASE ENGINE

"""
 AI EXPLANATION: What is an Engine?

The engine is the starting point for database interaction.
It manages:
- Connection pool (reuses connections for performance)
- Dialect (SQLite, PostgreSQL, MySQL, etc.)
- Connection parameters

We create it ONCE and reuse it throughout the application.
"""

# Create engine based on database URL from settings
engine = create_engine(
    settings.database_url,
    
    # AI: This setting is only for SQLite
    # It allows multiple threads to access the database
    # Remove this line if using PostgreSQL
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    
    # AI: Echo SQL queries if debug mode is enabled
    # This logs all SQL statements - useful for debugging
    # DISABLE in production for performance
    echo=settings.db_echo or settings.debug,
    
    # AI: Connection pool settings (optional, defaults are usually fine)
    # Uncomment these if you need custom pool settings:
    # pool_size=5,  # Number of connections to maintain
    # max_overflow=10,  # Max connections above pool_size
    # pool_timeout=30,  # Seconds to wait for connection
    # pool_recycle=3600,  # Recycle connections after 1 hour
)


# SESSION FACTORY

"""
 AI EXPLANATION: What is SessionLocal?

SessionLocal is a factory that creates database sessions.
A session represents a "workspace" for database operations.

Think of it like:
- Engine = Database connection manager
- Session = Your current conversation with the database

We use this factory to create new sessions for each request.
"""

SessionLocal = sessionmaker(
    # AI: Bind to our engine
    bind=engine,
    
    # AI: autocommit=False means we control when to commit
    # This is IMPORTANT for transaction safety
    autocommit=False,
    
    # AI: autoflush=False means we control when to flush changes
    # Flush = write changes to database but don't commit yet
    autoflush=False,
    
    # AI: expire_on_commit=False means objects remain usable after commit
    # This prevents additional queries when accessing committed objects
    expire_on_commit=False,
)


# DEPENDENCY INJECTION FUNCTION

def get_db() -> Generator[Session, None, None]:
    """
     AI PATTERN: Database Session Dependency
    
    This is the STANDARD way to get database access in routes.
    
    HOW IT WORKS:
    1. Creates a new database session
    2. Yields it to the route function
    3. Automatically closes it after the request (even if error occurs)
    
    WHY USE THIS:
    - Ensures sessions are always closed (prevents connection leaks)
    - Each request gets its own session (prevents cross-request issues)
    - FastAPI automatically handles the try/finally logic
    
    USAGE IN ROUTES:
    ```python
    from sqlalchemy.orm import Session
    from fastapi import Depends
    from app.db.session import get_db
    
    @router.get("/users")
    def list_users(db: Session = Depends(get_db)):
        users = db.query(User).all()
        return users
    ```
    
    AI: ALWAYS use Depends(get_db) to get database access.
    NEVER create sessions manually with SessionLocal().
    """
    
    # AI: Create a new session
    db = SessionLocal()
    
    try:
        # AI: Yield the session to the route
        # This is where the route function runs
        yield db
        
    finally:
        # AI: This ALWAYS runs, even if an error occurred
        # Ensures the session is closed and resources are freed
        db.close()


# UTILITY FUNCTIONS

def init_db() -> None:
    """
     AI PATTERN: Database Initialization
    
    This function creates all tables defined in your models.
    
    WHEN TO USE:
    - First time setup (development)
    - Testing (create test database)
    - NOT for production (use Alembic migrations instead)
    
    HOW TO USE:
    ```python
    from app.db.session import init_db
    from app.db.base import Base
    # Import all models so Base knows about them
    from app.db.models.user import User
    
    init_db()  # Creates all tables
    ```
    
    AI: For production, generate and run Alembic migrations instead.
    This is a convenience function for development only.
    """
    from app.db.base import Base
    
    # AI: Import all models here so SQLAlchemy knows about them
    # This is required for create_all() to work
    # Add new model imports as you create them
    
    # Example:
    # from app.db.models.user import User
    # from app.db.models.product import Product
    
    # AI: Create all tables
    Base.metadata.create_all(bind=engine)


# AI USAGE EXAMPLES

"""
 HOW AI SHOULD USE THIS FILE:

1. IN ROUTES (Most Common):
   ```python
   from fastapi import APIRouter, Depends
   from sqlalchemy.orm import Session
   from app.db.session import get_db
   
   router = APIRouter()
   
   @router.get("/items")
   def get_items(db: Session = Depends(get_db)):
       items = db.query(Item).all()
       return items
   ```

2. IN SERVICES (Dependency Injection):
   ```python
   class UserService:
       def __init__(self, db: Session):
           self.db = db
       
       def get_user(self, user_id: int):
           return self.db.query(User).filter(User.id == user_id).first()
   
   # In route:
   def get_user_service(db: Session = Depends(get_db)) -> UserService:
       return UserService(db)
   
   @router.get("/users/{user_id}")
   def get_user(
       user_id: int,
       service: UserService = Depends(get_user_service)
   ):
       return service.get_user(user_id)
   ```

3. FOR DATABASE INITIALIZATION (Development Only):
   ```python
   # In app/main.py startup event or scripts/init_db.py
   from app.db.session import init_db
   
   @app.on_event("startup")
   def startup_event():
       init_db()  # Creates all tables
   ```

4. MANUAL SESSION (Rare - only for scripts):
   ```python
   from app.db.session import SessionLocal
   
   def some_script():
       db = SessionLocal()
       try:
           # Do database operations
           users = db.query(User).all()
           db.commit()
       except Exception:
           db.rollback()
           raise
       finally:
           db.close()
   ```
   
   AI: Use this pattern ONLY in standalone scripts.
   In FastAPI routes, ALWAYS use Depends(get_db).

AI ANTI-PATTERNS (DO NOT DO):
Creating engine multiple times
Not closing sessions
Using SessionLocal() directly in routes
Creating global session instances
Forgetting to commit after writes

AI: If user asks for database testing utilities, add them to this file
as separate functions (e.g., get_test_db, reset_test_db).
"""