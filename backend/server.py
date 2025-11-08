from fastapi import FastAPI, APIRouter, HTTPException, Depends, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional, Any
import uuid
from datetime import datetime, timezone, timedelta
from enum import Enum
import bcrypt
import requests
import random
from twilio.rest import Client
from models_masters import (
    BOM, BOMCreate, BOMComponent,
    WorkCenter, WorkCenterCreate,
    Employee, EmployeeCreate,
    Supplier, SupplierCreate,
    Customer, CustomerCreate
)


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Twilio setup (will be configured with env vars)
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', '')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', '')
TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER', '')

twilio_client = None
if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

security = HTTPBearer(auto_error=False)


# Enums
class StockMoveType(str, Enum):
    RECEIPT = "receipt"
    ISSUE = "issue"
    TRANSFER = "transfer"
    ADJUSTMENT = "adjustment"


class UserRole(str, Enum):
    ADMIN = "Admin"
    PRODUCTION_MANAGER = "Production Manager"
    INVENTORY_OFFICER = "Inventory Officer"
    HR_OFFICER = "HR Officer"
    ACCOUNTANT = "Accountant"
    CEO_VIEWER = "CEO/Viewer"


class AuditAction(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


# Authentication Models
class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    password_hash: Optional[str] = None
    name: str
    picture: Optional[str] = None
    phone: Optional[str] = None
    role: UserRole = UserRole.INVENTORY_OFFICER
    is_active: bool = True
    otp_enabled: bool = False
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    phone: Optional[str] = None
    role: UserRole = UserRole.INVENTORY_OFFICER


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserSession(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    session_token: str
    expires_at: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OTPVerification(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    phone: str
    otp_code: str
    expires_at: datetime
    verified: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AuditLog(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    user_email: str
    action: AuditAction
    resource_type: str
    resource_id: str
    before_data: Optional[dict] = None
    after_data: Optional[dict] = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# Original Models
class Product(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    code: str
    name: str
    description: Optional[str] = None
    unit: str = "pcs"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ProductCreate(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    unit: str = "pcs"


class Warehouse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    code: str
    name: str
    location: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class WarehouseCreate(BaseModel):
    code: str
    name: str
    location: Optional[str] = None


class Bin(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    warehouse_id: str
    code: str
    name: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class BinCreate(BaseModel):
    warehouse_id: str
    code: str
    name: str


class InventoryItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_id: str
    warehouse_id: str
    bin_id: Optional[str] = None
    quantity: float = 0.0
    last_updated: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class StockMove(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_id: str
    move_type: StockMoveType
    from_warehouse_id: Optional[str] = None
    from_bin_id: Optional[str] = None
    to_warehouse_id: Optional[str] = None
    to_bin_id: Optional[str] = None
    quantity: float
    reference: Optional[str] = None
    notes: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class StockMoveCreate(BaseModel):
    product_id: str
    move_type: StockMoveType
    from_warehouse_id: Optional[str] = None
    from_bin_id: Optional[str] = None
    to_warehouse_id: Optional[str] = None
    to_bin_id: Optional[str] = None
    quantity: float
    reference: Optional[str] = None
    notes: Optional[str] = None


class Adjustment(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_id: str
    warehouse_id: str
    bin_id: Optional[str] = None
    quantity_change: float
    reason: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class AdjustmentCreate(BaseModel):
    product_id: str
    warehouse_id: str
    bin_id: Optional[str] = None
    quantity_change: float
    reason: str


# Helper Functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))


def generate_otp() -> str:
    return str(random.randint(100000, 999999))


async def send_sms_otp(phone: str, otp: str):
    if not twilio_client:
        logging.warning("Twilio not configured. OTP not sent.")
        return False
    
    try:
        message = twilio_client.messages.create(
            body=f"Your verification code is: {otp}",
            from_=TWILIO_PHONE_NUMBER,
            to=phone
        )
        return True
    except Exception as e:
        logging.error(f"Failed to send SMS: {e}")
        return False


async def log_audit(user_id: str, user_email: str, action: AuditAction, resource_type: str, 
                   resource_id: str, before_data: Optional[dict] = None, after_data: Optional[dict] = None):
    audit = AuditLog(
        user_id=user_id,
        user_email=user_email,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        before_data=before_data,
        after_data=after_data
    )
    await db.audit_logs.insert_one(audit.model_dump())


async def get_current_user(request: Request) -> User:
    # Check cookie first
    session_token = request.cookies.get("session_token")
    
    # Fallback to Authorization header
    if not session_token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            session_token = auth_header.replace("Bearer ", "")
    
    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Find session
    session = await db.user_sessions.find_one({"session_token": session_token})
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    # Check expiry - handle timezone-aware/naive datetime comparison
    expires_at = session["expires_at"]
    if isinstance(expires_at, datetime):
        # If it's timezone-naive, assume it's UTC
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
    
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Session expired")
    
    # Get user
    user = await db.users.find_one({"id": session["user_id"]}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not user.get("is_active", True):
        raise HTTPException(status_code=403, detail="User is inactive")
    
    return User(**user)


def check_permission(required_roles: List[UserRole]):
    async def permission_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in required_roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return permission_checker


async def update_inventory(product_id: str, warehouse_id: str, bin_id: Optional[str], quantity_change: float):
    query = {
        "product_id": product_id,
        "warehouse_id": warehouse_id
    }
    if bin_id:
        query["bin_id"] = bin_id
    
    existing = await db.inventory_items.find_one(query)
    
    if existing:
        new_quantity = existing["quantity"] + quantity_change
        await db.inventory_items.update_one(
            query,
            {"$set": {
                "quantity": new_quantity,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }}
        )
    else:
        inventory_item = InventoryItem(
            product_id=product_id,
            warehouse_id=warehouse_id,
            bin_id=bin_id,
            quantity=quantity_change
        )
        await db.inventory_items.insert_one(inventory_item.model_dump())


# Authentication Endpoints
@api_router.post("/auth/register")
async def register(user_data: UserCreate):
    # Check if user exists
    existing = await db.users.find_one({"email": user_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user = User(
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        name=user_data.name,
        phone=user_data.phone,
        role=user_data.role
    )
    
    await db.users.insert_one(user.model_dump())
    
    # Log audit
    await log_audit(user.id, user.email, AuditAction.CREATE, "user", user.id, after_data={"email": user.email, "role": user.role})
    
    return {"message": "User registered successfully", "user_id": user.id}


@api_router.post("/auth/login")
async def login(credentials: UserLogin, response: Response):
    # Find user
    user = await db.users.find_one({"email": credentials.email}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Verify password
    if not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user_obj = User(**user)
    
    if not user_obj.is_active:
        raise HTTPException(status_code=403, detail="User is inactive")
    
    # Check if 2FA is enabled
    if user_obj.otp_enabled and user_obj.phone:
        # Generate and send OTP
        otp_code = generate_otp()
        otp = OTPVerification(
            user_id=user_obj.id,
            phone=user_obj.phone,
            otp_code=otp_code,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=10)
        )
        await db.otp_verifications.insert_one(otp.model_dump())
        
        await send_sms_otp(user_obj.phone, otp_code)
        
        return {
            "requires_otp": True,
            "user_id": user_obj.id,
            "message": "OTP sent to your phone"
        }
    
    # Create session
    session_token = str(uuid.uuid4())
    session = UserSession(
        user_id=user_obj.id,
        session_token=session_token,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7)
    )
    
    await db.user_sessions.insert_one(session.model_dump())
    
    # Set cookie
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=7 * 24 * 60 * 60,
        path="/"
    )
    
    return {
        "session_token": session_token,
        "user": {
            "id": user_obj.id,
            "email": user_obj.email,
            "name": user_obj.name,
            "role": user_obj.role,
            "picture": user_obj.picture
        }
    }


@api_router.post("/auth/verify-otp")
async def verify_otp(user_id: str, otp_code: str, response: Response):
    # Find OTP
    otp = await db.otp_verifications.find_one({
        "user_id": user_id,
        "otp_code": otp_code,
        "verified": False
    })
    
    if not otp:
        raise HTTPException(status_code=401, detail="Invalid OTP")
    
    # Check OTP expiry - handle timezone-aware/naive datetime comparison
    expires_at = otp["expires_at"]
    if isinstance(expires_at, datetime):
        # If it's timezone-naive, assume it's UTC
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
    
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="OTP expired")
    
    # Mark as verified
    await db.otp_verifications.update_one(
        {"id": otp["id"]},
        {"$set": {"verified": True}}
    )
    
    # Get user
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    user_obj = User(**user)
    
    # Create session
    session_token = str(uuid.uuid4())
    session = UserSession(
        user_id=user_obj.id,
        session_token=session_token,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7)
    )
    
    await db.user_sessions.insert_one(session.model_dump())
    
    # Set cookie
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=7 * 24 * 60 * 60,
        path="/"
    )
    
    return {
        "session_token": session_token,
        "user": {
            "id": user_obj.id,
            "email": user_obj.email,
            "name": user_obj.name,
            "role": user_obj.role,
            "picture": user_obj.picture
        }
    }


@api_router.get("/auth/session")
async def get_session_data(request: Request):
    # Handle Emergent OAuth session_id from header
    session_id = request.headers.get("X-Session-ID")
    
    if session_id:
        # Call Emergent auth service
        try:
            response = requests.get(
                "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
                headers={"X-Session-ID": session_id}
            )
            response.raise_for_status()
            data = response.json()
            
            # Check if user exists
            user = await db.users.find_one({"email": data["email"]}, {"_id": 0})
            
            if not user:
                # Create new user
                new_user = User(
                    email=data["email"],
                    name=data["name"],
                    picture=data.get("picture"),
                    role=UserRole.INVENTORY_OFFICER
                )
                await db.users.insert_one(new_user.model_dump())
                user = new_user.model_dump()
                await log_audit(new_user.id, new_user.email, AuditAction.CREATE, "user", new_user.id, 
                              after_data={"email": new_user.email, "source": "google_oauth"})
            
            user_obj = User(**user)
            
            # Create session with Emergent session_token
            session = UserSession(
                user_id=user_obj.id,
                session_token=data["session_token"],
                expires_at=datetime.now(timezone.utc) + timedelta(days=7)
            )
            
            await db.user_sessions.insert_one(session.model_dump())
            
            return {
                "session_token": data["session_token"],
                "user": {
                    "id": user_obj.id,
                    "email": user_obj.email,
                    "name": user_obj.name,
                    "role": user_obj.role,
                    "picture": user_obj.picture
                }
            }
        except Exception as e:
            logging.error(f"OAuth session error: {e}")
            raise HTTPException(status_code=400, detail="Invalid session ID")
    
    raise HTTPException(status_code=400, detail="No session ID provided")


@api_router.get("/auth/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "role": current_user.role,
        "picture": current_user.picture,
        "phone": current_user.phone,
        "otp_enabled": current_user.otp_enabled
    }


@api_router.post("/auth/logout")
async def logout(request: Request, response: Response, current_user: User = Depends(get_current_user)):
    session_token = request.cookies.get("session_token")
    
    if session_token:
        await db.user_sessions.delete_one({"session_token": session_token})
    
    response.delete_cookie(key="session_token", path="/")
    
    return {"message": "Logged out successfully"}


@api_router.patch("/auth/toggle-2fa")
async def toggle_2fa(enable: bool, current_user: User = Depends(get_current_user)):
    if enable and not current_user.phone:
        raise HTTPException(status_code=400, detail="Phone number required for 2FA")
    
    await db.users.update_one(
        {"id": current_user.id},
        {"$set": {"otp_enabled": enable}}
    )
    
    return {"message": f"2FA {'enabled' if enable else 'disabled'} successfully"}


# User Management (Admin only)
@api_router.get("/users", response_model=List[User])
async def get_users(current_user: User = Depends(check_permission([UserRole.ADMIN]))):
    users = await db.users.find({}, {"_id": 0, "password_hash": 0}).to_list(1000)
    return users


@api_router.patch("/users/{user_id}/role")
async def update_user_role(user_id: str, role: UserRole, current_user: User = Depends(check_permission([UserRole.ADMIN]))):
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    await db.users.update_one(
        {"id": user_id},
        {"$set": {"role": role}}
    )
    
    await log_audit(current_user.id, current_user.email, AuditAction.UPDATE, "user", user_id,
                   before_data={"role": user["role"]}, after_data={"role": role})
    
    return {"message": "Role updated successfully"}


# Audit Logs
@api_router.get("/audit-logs")
async def get_audit_logs(
    resource_type: Optional[str] = None,
    user_id: Optional[str] = None,
    current_user: User = Depends(check_permission([UserRole.ADMIN, UserRole.ACCOUNTANT, UserRole.CEO_VIEWER]))
):
    query = {}
    if resource_type:
        query["resource_type"] = resource_type
    if user_id:
        query["user_id"] = user_id
    
    logs = await db.audit_logs.find(query, {"_id": 0}).sort("timestamp", -1).to_list(1000)
    return logs


# Product endpoints (with auth and audit)
@api_router.post("/products", response_model=Product)
async def create_product(product: ProductCreate, current_user: User = Depends(check_permission(
    [UserRole.ADMIN, UserRole.PRODUCTION_MANAGER, UserRole.INVENTORY_OFFICER]
))):
    existing = await db.products.find_one({"code": product.code})
    if existing:
        raise HTTPException(status_code=400, detail="Product code already exists")
    
    product_obj = Product(**product.model_dump())
    await db.products.insert_one(product_obj.model_dump())
    
    await log_audit(current_user.id, current_user.email, AuditAction.CREATE, "product", product_obj.id,
                   after_data=product_obj.model_dump())
    
    return product_obj


@api_router.get("/products", response_model=List[Product])
async def get_products(current_user: User = Depends(get_current_user)):
    products = await db.products.find({}, {"_id": 0}).to_list(1000)
    return products


@api_router.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: str, current_user: User = Depends(get_current_user)):
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


# Warehouse endpoints (with auth and audit)
@api_router.post("/warehouses", response_model=Warehouse)
async def create_warehouse(warehouse: WarehouseCreate, current_user: User = Depends(check_permission(
    [UserRole.ADMIN, UserRole.INVENTORY_OFFICER]
))):
    existing = await db.warehouses.find_one({"code": warehouse.code})
    if existing:
        raise HTTPException(status_code=400, detail="Warehouse code already exists")
    
    warehouse_obj = Warehouse(**warehouse.model_dump())
    await db.warehouses.insert_one(warehouse_obj.model_dump())
    
    await log_audit(current_user.id, current_user.email, AuditAction.CREATE, "warehouse", warehouse_obj.id,
                   after_data=warehouse_obj.model_dump())
    
    return warehouse_obj


@api_router.get("/warehouses", response_model=List[Warehouse])
async def get_warehouses(current_user: User = Depends(get_current_user)):
    warehouses = await db.warehouses.find({}, {"_id": 0}).to_list(1000)
    return warehouses


# Bin endpoints (with auth and audit)
@api_router.post("/bins", response_model=Bin)
async def create_bin(bin_data: BinCreate, current_user: User = Depends(check_permission(
    [UserRole.ADMIN, UserRole.INVENTORY_OFFICER]
))):
    warehouse = await db.warehouses.find_one({"id": bin_data.warehouse_id})
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    
    bin_obj = Bin(**bin_data.model_dump())
    await db.bins.insert_one(bin_obj.model_dump())
    
    await log_audit(current_user.id, current_user.email, AuditAction.CREATE, "bin", bin_obj.id,
                   after_data=bin_obj.model_dump())
    
    return bin_obj


@api_router.get("/bins", response_model=List[Bin])
async def get_bins(warehouse_id: Optional[str] = None, current_user: User = Depends(get_current_user)):
    query = {}
    if warehouse_id:
        query["warehouse_id"] = warehouse_id
    bins = await db.bins.find(query, {"_id": 0}).to_list(1000)
    return bins


# Inventory endpoints (with auth)
@api_router.get("/inventory")
async def get_inventory(
    product_id: Optional[str] = None,
    warehouse_id: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    query = {}
    if product_id:
        query["product_id"] = product_id
    if warehouse_id:
        query["warehouse_id"] = warehouse_id
    
    inventory = await db.inventory_items.find(query, {"_id": 0}).to_list(1000)
    
    for item in inventory:
        product = await db.products.find_one({"id": item["product_id"]}, {"_id": 0})
        warehouse = await db.warehouses.find_one({"id": item["warehouse_id"]}, {"_id": 0})
        item["product"] = product
        item["warehouse"] = warehouse
        
        if item.get("bin_id"):
            bin_data = await db.bins.find_one({"id": item["bin_id"]}, {"_id": 0})
            item["bin"] = bin_data
    
    return inventory


# Stock move endpoints (with auth and audit)
@api_router.post("/stock-moves", response_model=StockMove)
async def create_stock_move(move: StockMoveCreate, current_user: User = Depends(check_permission(
    [UserRole.ADMIN, UserRole.INVENTORY_OFFICER]
))):
    product = await db.products.find_one({"id": move.product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    move_obj = StockMove(**move.model_dump())
    await db.stock_moves.insert_one(move_obj.model_dump())
    
    # Update inventory based on move type
    if move.move_type == StockMoveType.RECEIPT:
        await update_inventory(move.product_id, move.to_warehouse_id, move.to_bin_id, move.quantity)
    elif move.move_type == StockMoveType.ISSUE:
        await update_inventory(move.product_id, move.from_warehouse_id, move.from_bin_id, -move.quantity)
    elif move.move_type == StockMoveType.TRANSFER:
        await update_inventory(move.product_id, move.from_warehouse_id, move.from_bin_id, -move.quantity)
        await update_inventory(move.product_id, move.to_warehouse_id, move.to_bin_id, move.quantity)
    
    await log_audit(current_user.id, current_user.email, AuditAction.CREATE, "stock_move", move_obj.id,
                   after_data=move_obj.model_dump())
    
    return move_obj


@api_router.get("/stock-moves", response_model=List[StockMove])
async def get_stock_moves(product_id: Optional[str] = None, current_user: User = Depends(get_current_user)):
    query = {}
    if product_id:
        query["product_id"] = product_id
    moves = await db.stock_moves.find(query, {"_id": 0}).sort("created_at", -1).to_list(1000)
    return moves


# Adjustment endpoints (with auth and audit)
@api_router.post("/adjustments", response_model=Adjustment)
async def create_adjustment(adjustment: AdjustmentCreate, current_user: User = Depends(check_permission(
    [UserRole.ADMIN, UserRole.INVENTORY_OFFICER]
))):
    product = await db.products.find_one({"id": adjustment.product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    warehouse = await db.warehouses.find_one({"id": adjustment.warehouse_id})
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    
    adjustment_obj = Adjustment(**adjustment.model_dump())
    await db.adjustments.insert_one(adjustment_obj.model_dump())
    
    # Update inventory
    await update_inventory(
        adjustment.product_id,
        adjustment.warehouse_id,
        adjustment.bin_id,
        adjustment.quantity_change
    )
    
    # Create stock move for tracking
    stock_move = StockMove(
        product_id=adjustment.product_id,
        move_type=StockMoveType.ADJUSTMENT,
        to_warehouse_id=adjustment.warehouse_id if adjustment.quantity_change > 0 else None,
        from_warehouse_id=adjustment.warehouse_id if adjustment.quantity_change < 0 else None,
        to_bin_id=adjustment.bin_id if adjustment.quantity_change > 0 else None,
        from_bin_id=adjustment.bin_id if adjustment.quantity_change < 0 else None,
        quantity=abs(adjustment.quantity_change),
        reference=adjustment_obj.id,
        notes=adjustment.reason
    )
    await db.stock_moves.insert_one(stock_move.model_dump())
    
    await log_audit(current_user.id, current_user.email, AuditAction.CREATE, "adjustment", adjustment_obj.id,
                   after_data=adjustment_obj.model_dump())
    
    return adjustment_obj


@api_router.get("/adjustments", response_model=List[Adjustment])
async def get_adjustments(current_user: User = Depends(get_current_user)):
    adjustments = await db.adjustments.find({}, {"_id": 0}).sort("created_at", -1).to_list(1000)
    return adjustments


# ===== MASTERS ENDPOINTS =====

# BOM endpoints
@api_router.post("/boms", response_model=BOM)
async def create_bom(bom: BOMCreate, current_user: User = Depends(check_permission(
    [UserRole.ADMIN, UserRole.PRODUCTION_MANAGER]
))):
    # Verify product exists
    product = await db.products.find_one({"id": bom.product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Verify all components exist
    for component in bom.components:
        comp_product = await db.products.find_one({"id": component.product_id})
        if not comp_product:
            raise HTTPException(status_code=404, detail=f"Component product {component.product_id} not found")
    
    bom_obj = BOM(**bom.model_dump())
    await db.boms.insert_one(bom_obj.model_dump())
    
    await log_audit(current_user.id, current_user.email, AuditAction.CREATE, "bom", bom_obj.id,
                   after_data=bom_obj.model_dump())
    
    return bom_obj


@api_router.get("/boms", response_model=List[BOM])
async def get_boms(current_user: User = Depends(get_current_user)):
    boms = await db.boms.find({}, {"_id": 0}).to_list(1000)
    return boms


@api_router.get("/boms/{bom_id}", response_model=BOM)
async def get_bom(bom_id: str, current_user: User = Depends(get_current_user)):
    bom = await db.boms.find_one({"id": bom_id}, {"_id": 0})
    if not bom:
        raise HTTPException(status_code=404, detail="BOM not found")
    return bom


# WorkCenter endpoints
@api_router.post("/work-centers", response_model=WorkCenter)
async def create_work_center(work_center: WorkCenterCreate, current_user: User = Depends(check_permission(
    [UserRole.ADMIN, UserRole.PRODUCTION_MANAGER]
))):
    existing = await db.work_centers.find_one({"code": work_center.code})
    if existing:
        raise HTTPException(status_code=400, detail="Work center code already exists")
    
    wc_obj = WorkCenter(**work_center.model_dump())
    await db.work_centers.insert_one(wc_obj.model_dump())
    
    await log_audit(current_user.id, current_user.email, AuditAction.CREATE, "work_center", wc_obj.id,
                   after_data=wc_obj.model_dump())
    
    return wc_obj


@api_router.get("/work-centers", response_model=List[WorkCenter])
async def get_work_centers(current_user: User = Depends(get_current_user)):
    work_centers = await db.work_centers.find({}, {"_id": 0}).to_list(1000)
    return work_centers


# Employee endpoints
@api_router.post("/employees", response_model=Employee)
async def create_employee(employee: EmployeeCreate, current_user: User = Depends(check_permission(
    [UserRole.ADMIN, UserRole.HR_OFFICER]
))):
    existing = await db.employees.find_one({"code": employee.code})
    if existing:
        raise HTTPException(status_code=400, detail="Employee code already exists")
    
    emp_obj = Employee(**employee.model_dump())
    await db.employees.insert_one(emp_obj.model_dump())
    
    await log_audit(current_user.id, current_user.email, AuditAction.CREATE, "employee", emp_obj.id,
                   after_data=emp_obj.model_dump())
    
    return emp_obj


@api_router.get("/employees", response_model=List[Employee])
async def get_employees(current_user: User = Depends(get_current_user)):
    employees = await db.employees.find({}, {"_id": 0}).to_list(1000)
    return employees


# Supplier endpoints
@api_router.post("/suppliers", response_model=Supplier)
async def create_supplier(supplier: SupplierCreate, current_user: User = Depends(check_permission(
    [UserRole.ADMIN, UserRole.PRODUCTION_MANAGER, UserRole.ACCOUNTANT]
))):
    existing = await db.suppliers.find_one({"code": supplier.code})
    if existing:
        raise HTTPException(status_code=400, detail="Supplier code already exists")
    
    supp_obj = Supplier(**supplier.model_dump())
    await db.suppliers.insert_one(supp_obj.model_dump())
    
    await log_audit(current_user.id, current_user.email, AuditAction.CREATE, "supplier", supp_obj.id,
                   after_data=supp_obj.model_dump())
    
    return supp_obj


@api_router.get("/suppliers", response_model=List[Supplier])
async def get_suppliers(current_user: User = Depends(get_current_user)):
    suppliers = await db.suppliers.find({}, {"_id": 0}).to_list(1000)
    return suppliers


# Customer endpoints
@api_router.post("/customers", response_model=Customer)
async def create_customer(customer: CustomerCreate, current_user: User = Depends(check_permission(
    [UserRole.ADMIN, UserRole.PRODUCTION_MANAGER, UserRole.ACCOUNTANT]
))):
    existing = await db.customers.find_one({"code": customer.code})
    if existing:
        raise HTTPException(status_code=400, detail="Customer code already exists")
    
    cust_obj = Customer(**customer.model_dump())
    await db.customers.insert_one(cust_obj.model_dump())
    
    await log_audit(current_user.id, current_user.email, AuditAction.CREATE, "customer", cust_obj.id,
                   after_data=cust_obj.model_dump())
    
    return cust_obj


@api_router.get("/customers", response_model=List[Customer])
async def get_customers(current_user: User = Depends(get_current_user)):
    customers = await db.customers.find({}, {"_id": 0}).to_list(1000)
    return customers


@api_router.get("/")
async def root():
    return {"message": "Inventory Management API with Authentication"}


# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
