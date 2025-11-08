from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
from enum import Enum


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Enums
class StockMoveType(str, Enum):
    RECEIPT = "receipt"
    ISSUE = "issue"
    TRANSFER = "transfer"
    ADJUSTMENT = "adjustment"


# Models
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


# Helper function to update inventory
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


# Product endpoints
@api_router.post("/products", response_model=Product)
async def create_product(product: ProductCreate):
    # Check if code already exists
    existing = await db.products.find_one({"code": product.code})
    if existing:
        raise HTTPException(status_code=400, detail="Product code already exists")
    
    product_obj = Product(**product.model_dump())
    await db.products.insert_one(product_obj.model_dump())
    return product_obj


@api_router.get("/products", response_model=List[Product])
async def get_products():
    products = await db.products.find({}, {"_id": 0}).to_list(1000)
    return products


@api_router.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: str):
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


# Warehouse endpoints
@api_router.post("/warehouses", response_model=Warehouse)
async def create_warehouse(warehouse: WarehouseCreate):
    existing = await db.warehouses.find_one({"code": warehouse.code})
    if existing:
        raise HTTPException(status_code=400, detail="Warehouse code already exists")
    
    warehouse_obj = Warehouse(**warehouse.model_dump())
    await db.warehouses.insert_one(warehouse_obj.model_dump())
    return warehouse_obj


@api_router.get("/warehouses", response_model=List[Warehouse])
async def get_warehouses():
    warehouses = await db.warehouses.find({}, {"_id": 0}).to_list(1000)
    return warehouses


# Bin endpoints
@api_router.post("/bins", response_model=Bin)
async def create_bin(bin_data: BinCreate):
    # Verify warehouse exists
    warehouse = await db.warehouses.find_one({"id": bin_data.warehouse_id})
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    
    bin_obj = Bin(**bin_data.model_dump())
    await db.bins.insert_one(bin_obj.model_dump())
    return bin_obj


@api_router.get("/bins", response_model=List[Bin])
async def get_bins(warehouse_id: Optional[str] = None):
    query = {}
    if warehouse_id:
        query["warehouse_id"] = warehouse_id
    bins = await db.bins.find(query, {"_id": 0}).to_list(1000)
    return bins


# Inventory endpoints
@api_router.get("/inventory")
async def get_inventory(product_id: Optional[str] = None, warehouse_id: Optional[str] = None):
    query = {}
    if product_id:
        query["product_id"] = product_id
    if warehouse_id:
        query["warehouse_id"] = warehouse_id
    
    inventory = await db.inventory_items.find(query, {"_id": 0}).to_list(1000)
    
    # Enrich with product and warehouse details
    for item in inventory:
        product = await db.products.find_one({"id": item["product_id"]}, {"_id": 0})
        warehouse = await db.warehouses.find_one({"id": item["warehouse_id"]}, {"_id": 0})
        item["product"] = product
        item["warehouse"] = warehouse
        
        if item.get("bin_id"):
            bin_data = await db.bins.find_one({"id": item["bin_id"]}, {"_id": 0})
            item["bin"] = bin_data
    
    return inventory


# Stock move endpoints
@api_router.post("/stock-moves", response_model=StockMove)
async def create_stock_move(move: StockMoveCreate):
    # Verify product exists
    product = await db.products.find_one({"id": move.product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    move_obj = StockMove(**move.model_dump())
    await db.stock_moves.insert_one(move_obj.model_dump())
    
    # Update inventory based on move type
    if move.move_type == StockMoveType.RECEIPT:
        # Add to destination
        await update_inventory(move.product_id, move.to_warehouse_id, move.to_bin_id, move.quantity)
    
    elif move.move_type == StockMoveType.ISSUE:
        # Remove from source
        await update_inventory(move.product_id, move.from_warehouse_id, move.from_bin_id, -move.quantity)
    
    elif move.move_type == StockMoveType.TRANSFER:
        # Remove from source, add to destination
        await update_inventory(move.product_id, move.from_warehouse_id, move.from_bin_id, -move.quantity)
        await update_inventory(move.product_id, move.to_warehouse_id, move.to_bin_id, move.quantity)
    
    return move_obj


@api_router.get("/stock-moves", response_model=List[StockMove])
async def get_stock_moves(product_id: Optional[str] = None):
    query = {}
    if product_id:
        query["product_id"] = product_id
    moves = await db.stock_moves.find(query, {"_id": 0}).sort("created_at", -1).to_list(1000)
    return moves


# Adjustment endpoints
@api_router.post("/adjustments", response_model=Adjustment)
async def create_adjustment(adjustment: AdjustmentCreate):
    # Verify product exists
    product = await db.products.find_one({"id": adjustment.product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Verify warehouse exists
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
    
    # Also create a stock move for tracking
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
    
    return adjustment_obj


@api_router.get("/adjustments", response_model=List[Adjustment])
async def get_adjustments():
    adjustments = await db.adjustments.find({}, {"_id": 0}).sort("created_at", -1).to_list(1000)
    return adjustments


@api_router.get("/")
async def root():
    return {"message": "Inventory Management API"}


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
