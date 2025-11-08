from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional
from datetime import datetime, timezone
import uuid


# BOM Models
class BOMComponent(BaseModel):
    product_id: str
    quantity: float
    unit: str = "pcs"


class BOM(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    product_id: str  # Finished product
    version: str = "1.0"
    components: List[BOMComponent] = []
    is_active: bool = True
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class BOMCreate(BaseModel):
    name: str
    product_id: str
    version: str = "1.0"
    components: List[BOMComponent] = []
    is_active: bool = True


# WorkCenter Models
class WorkCenter(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    code: str
    name: str
    description: Optional[str] = None
    capacity: float = 1.0  # units per hour
    efficiency: float = 100.0  # percentage
    cost_per_hour: float = 0.0
    is_active: bool = True
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class WorkCenterCreate(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    capacity: float = 1.0
    efficiency: float = 100.0
    cost_per_hour: float = 0.0
    is_active: bool = True


# Employee Models
class Employee(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    code: str
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    hire_date: Optional[str] = None
    salary: Optional[float] = None
    is_active: bool = True
    user_id: Optional[str] = None  # Link to system user
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class EmployeeCreate(BaseModel):
    code: str
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    hire_date: Optional[str] = None
    salary: Optional[float] = None
    is_active: bool = True
    user_id: Optional[str] = None


# Supplier Models
class Supplier(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    code: str
    name: str
    contact_person: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    payment_terms: Optional[str] = None
    rating: Optional[float] = None
    is_active: bool = True
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class SupplierCreate(BaseModel):
    code: str
    name: str
    contact_person: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    payment_terms: Optional[str] = None
    rating: Optional[float] = None
    is_active: bool = True


# Customer Models
class Customer(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    code: str
    name: str
    contact_person: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    payment_terms: Optional[str] = None
    credit_limit: Optional[float] = None
    outstanding_balance: float = 0.0
    is_active: bool = True
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class CustomerCreate(BaseModel):
    code: str
    name: str
    contact_person: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    payment_terms: Optional[str] = None
    credit_limit: Optional[float] = None
    is_active: bool = True
