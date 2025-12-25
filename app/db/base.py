"""
AI INSTRUCTION: SQLAlchemy Base Class
This file provides the base class for ALL database models.

RULES FOR AI:
1. ALL models MUST inherit from Base
2. Import Base from here, never create your own
3. This file should NEVER be modified after creation
4. Use declarative_base() pattern (SQLAlchemy 2.0 style)

PATTERN: When creating a new model:
  ```python
  from app.db.base import Base
  
  class YourModel(Base):
      __tablename__ = "your_table"
      # ... fields here
  ```

AI: DO NOT create multiple base classes. Use this one.
"""

from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """
    AI PATTERN: SQLAlchemy Base Class
    
    This is the base class for ALL database models in this application.
    
    WHY THIS EXISTS:
    - Provides common functionality to all models
    - Enables SQLAlchemy to track all models
    - Required for Alembic migrations to detect models
    - Allows us to add common fields/methods later if needed
    
    USAGE IN MODELS:
    ```python
    from app.db.base import Base
    from sqlalchemy import Column, Integer, String
    
    class User(Base):
        __tablename__ = "users"
        
        id = Column(Integer, primary_key=True, index=True)
        email = Column(String, unique=True, index=True, nullable=False)
    ```
    
    AI INSTRUCTIONS:
    - Always import this Base, never create your own
    - Every model file must: from app.db.base import Base
    - Every model class must: class YourModel(Base):
    - Never modify this file unless adding common functionality to ALL models
    """
    
    pass  # AI: We use pass because DeclarativeBase provides all functionality



# AI USAGE EXAMPLES
"""
HOW AI SHOULD USE THIS FILE:

1. CREATING A NEW MODEL:
   File: app/db/models/product.py
   ```python
   from sqlalchemy import Column, Integer, String, Float
   from app.db.base import Base
   
   class Product(Base):
       __tablename__ = "products"
       
       id = Column(Integer, primary_key=True, index=True)
       name = Column(String, nullable=False)
       price = Column(Float, nullable=False)
   ```

2. IMPORTING MODELS FOR ALEMBIC:
   File: app/db/base.py or alembic/env.py
   ```python
   from app.db.base import Base
   from app.db.models.user import User
   from app.db.models.product import Product
   
   # Alembic will detect all models that inherit from Base
   ```

3. COMMON PATTERN - Models with Timestamps:
   If you want ALL models to have created_at/updated_at,
   you could add them to Base (advanced, not needed for MVP):
   
   ```python
   from datetime import datetime
   from sqlalchemy import Column, DateTime
   from sqlalchemy.orm import DeclarativeBase
   
   class Base(DeclarativeBase):
       created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
       updated_at = Column(DateTime, default=datetime.utcnow, 
                          onupdate=datetime.utcnow, nullable=False)
   ```
   
   AI: Only add this if user specifically requests timestamp tracking
   on all models. Otherwise keep Base simple.

AI ANTI-PATTERNS (DO NOT DO):
Creating multiple base classes
Modifying this file frequently
Putting model-specific logic here
Creating models without inheriting from Base
"""