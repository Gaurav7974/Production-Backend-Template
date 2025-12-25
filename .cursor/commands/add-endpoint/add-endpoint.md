# Add Endpoint Command

This command generates a new API endpoint following the template's patterns.

## Usage

When user asks to add a new endpoint, follow these steps:

## Step 1: Understand Requirements

Ask clarifying questions if needed:
- What resource is this endpoint for?
- What HTTP method (GET, POST, PUT, DELETE)?
- What data does it accept?
- What should it return?
- Does it need authentication?

## Step 2: Check for Existing Files

Look for existing files in this order:
1. app/schemas/{resource}.py
2. app/db/models/{resource}.py
3. app/services/{resource}_service.py
4. app/api/v1/routes/{resource}.py

## Step 3: Create Schema (if needed)

If schema doesn't exist, create app/schemas/{resource}.py:

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class {Resource}Base(BaseModel):
    """Base schema with common fields"""
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None

class {Resource}Create({Resource}Base):
    """Schema for creating a {resource}"""
    pass

class {Resource}Update(BaseModel):
    """Schema for updating a {resource}"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None

class {Resource}Response({Resource}Base):
    """Schema for API responses"""
    id: int
    created_at: datetime
    
    model_config = {"from_attributes": True}
```

## Step 4: Create Model (if needed)

If model doesn't exist, create app/db/models/{resource}.py:

```python
from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from app.db.base import Base

class {Resource}(Base):
    __tablename__ = "{resources}"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

## Step 5: Create Service (if needed)

If service doesn't exist, create app/services/{resource}_service.py:

```python
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.exceptions import NotFoundException, ValidationException
from app.db.models.{resource} import {Resource}
from app.schemas.{resource} import {Resource}Create, {Resource}Update, {Resource}Response

class {Resource}Service:
    def __init__(self, db: Session):
        self.db = db
    
    async def get(self, {resource}_id: int) -> {Resource}Response:
        db_{resource} = self.db.query({Resource}).filter(
            {Resource}.id == {resource}_id
        ).first()
        
        if not db_{resource}:
            raise NotFoundException(f"{Resource} {{{resource}_id}} not found")
        
        return {Resource}Response.model_validate(db_{resource})
    
    async def list(self, skip: int = 0, limit: int = 100) -> List[{Resource}Response]:
        {resources} = self.db.query({Resource}).offset(skip).limit(limit).all()
        return [{Resource}Response.model_validate({resource}) for {resource} in {resources}]
    
    async def create(self, {resource}_data: {Resource}Create) -> {Resource}Response:
        db_{resource} = {Resource}(**{resource}_data.model_dump())
        self.db.add(db_{resource})
        self.db.commit()
        self.db.refresh(db_{resource})
        return {Resource}Response.model_validate(db_{resource})
    
    async def update(
        self, 
        {resource}_id: int, 
        {resource}_data: {Resource}Update
    ) -> {Resource}Response:
        db_{resource} = self.db.query({Resource}).filter(
            {Resource}.id == {resource}_id
        ).first()
        
        if not db_{resource}:
            raise NotFoundException(f"{Resource} {{{resource}_id}} not found")
        
        update_data = {resource}_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_{resource}, key, value)
        
        self.db.commit()
        self.db.refresh(db_{resource})
        return {Resource}Response.model_validate(db_{resource})
    
    async def delete(self, {resource}_id: int) -> None:
        db_{resource} = self.db.query({Resource}).filter(
            {Resource}.id == {resource}_id
        ).first()
        
        if not db_{resource}:
            raise NotFoundException(f"{Resource} {{{resource}_id}} not found")
        
        self.db.delete(db_{resource})
        self.db.commit()
```

## Step 6: Create or Update Routes

If routes file doesn't exist, create app/api/v1/routes/{resource}.py:

```python
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.{resource} import {Resource}Create, {Resource}Update, {Resource}Response
from app.services.{resource}_service import {Resource}Service

router = APIRouter(prefix="/{resources}", tags=["{resources}"])

@router.post("", response_model={Resource}Response, status_code=status.HTTP_201_CREATED)
async def create_{resource}(
    {resource}_data: {Resource}Create,
    db: Session = Depends(get_db)
):
    """Create a new {resource}"""
    service = {Resource}Service(db)
    return await service.create({resource}_data)

@router.get("", response_model=List[{Resource}Response])
async def list_{resources}(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List {resources} with pagination"""
    service = {Resource}Service(db)
    return await service.list(skip=skip, limit=limit)

@router.get("/{{{resource}_id}}", response_model={Resource}Response)
async def get_{resource}(
    {resource}_id: int,
    db: Session = Depends(get_db)
):
    """Get a single {resource}"""
    service = {Resource}Service(db)
    return await service.get({resource}_id)

@router.put("/{{{resource}_id}}", response_model={Resource}Response)
async def update_{resource}(
    {resource}_id: int,
    {resource}_data: {Resource}Update,
    db: Session = Depends(get_db)
):
    """Update a {resource}"""
    service = {Resource}Service(db)
    return await service.update({resource}_id, {resource}_data)

@router.delete("/{{{resource}_id}}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_{resource}(
    {resource}_id: int,
    db: Session = Depends(get_db)
):
    """Delete a {resource}"""
    service = {Resource}Service(db)
    await service.delete({resource}_id)
```

If routes file exists, add just the new endpoint.

## Step 7: Register Router

Update app/api/v1/router.py:

```python
from app.api.v1.routes import {resource}

api_router.include_router({resource}.router)
```

## Step 8: Generate Migration

After creating/modifying models, remind user to generate migration:

```bash
alembic revision --autogenerate -m "Add {resource} table"
alembic upgrade head
```

## Step 9: Create Tests

Create tests/api/v1/test_{resource}.py:

```python
from fastapi.testclient import TestClient

def test_create_{resource}(client: TestClient):
    response = client.post(
        "/api/v1/{resources}",
        json={"name": "Test {Resource}", "description": "Test description"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test {Resource}"
    assert "id" in data

def test_list_{resources}(client: TestClient):
    response = client.get("/api/v1/{resources}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_{resource}(client: TestClient):
    # Create first
    create_response = client.post(
        "/api/v1/{resources}",
        json={"name": "Test {Resource}"}
    )
    {resource}_id = create_response.json()["id"]
    
    # Get
    response = client.get(f"/api/v1/{resources}/{{{resource}_id}}")
    assert response.status_code == 200
    assert response.json()["id"] == {resource}_id

def test_update_{resource}(client: TestClient):
    # Create first
    create_response = client.post(
        "/api/v1/{resources}",
        json={"name": "Test {Resource}"}
    )
    {resource}_id = create_response.json()["id"]
    
    # Update
    response = client.put(
        f"/api/v1/{resources}/{{{resource}_id}}",
        json={"name": "Updated {Resource}"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated {Resource}"

def test_delete_{resource}(client: TestClient):
    # Create first
    create_response = client.post(
        "/api/v1/{resources}",
        json={"name": "Test {Resource}"}
    )
    {resource}_id = create_response.json()["id"]
    
    # Delete
    response = client.delete(f"/api/v1/{resources}/{{{resource}_id}}")
    assert response.status_code == 204
    
    # Verify deleted
    response = client.get(f"/api/v1/{resources}/{{{resource}_id}}")
    assert response.status_code == 404
```

## Checklist

Before marking complete, verify:
- [ ] Schema created/updated with proper validation
- [ ] Model created/updated with proper columns and indexes
- [ ] Service created/updated with business logic
- [ ] Routes created/updated with proper HTTP methods
- [ ] Router registered in app/api/v1/router.py
- [ ] Tests created
- [ ] Migration reminder given to user

## Example Usage

User: "Add an endpoint to create products"

AI Response:
1. Creates app/schemas/product.py with ProductCreate, ProductUpdate, ProductResponse
2. Creates app/db/models/product.py with Product model
3. Creates app/services/product_service.py with CRUD operations
4. Creates app/api/v1/routes/products.py with POST /products endpoint
5. Updates app/api/v1/router.py to include products router
6. Reminds user to run migration
7. Creates test file

## Notes

- Always look at examples/ directories first
- Follow exact naming conventions
- Use dependency injection
- Raise custom exceptions in services
- Keep routes thin
- Validate with Pydantic
- Return Pydantic schemas from services