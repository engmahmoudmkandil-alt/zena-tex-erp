from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import pandas as pd
import io
import csv
import json
import logging
from pydantic import BaseModel
import os

logger = logging.getLogger(__name__)

export_router = APIRouter(prefix="/api/export")


class ExportRequest(BaseModel):
    entity: str  # products, boms, inventory, etc.
    format: str  # csv, excel, json
    filters: Optional[Dict[str, Any]] = None


class ImportRequest(BaseModel):
    entity: str
    data: List[Dict[str, Any]]
    mode: str = "append"  # append, update, replace


class ExportService:
    """Handles data export in multiple formats"""
    
    SUPPORTED_ENTITIES = [
        "products", "boms", "work_centers", "warehouses", "bins",
        "inventory_items", "stock_moves", "adjustments",
        "employees", "suppliers", "customers",
        "production_orders", "work_orders", "quality_checks",
        "attendance", "payroll"
    ]
    
    @staticmethod
    async def export_to_csv(db: AsyncIOMotorDatabase, entity: str, filters: Dict = None) -> bytes:
        """Export entity to CSV format"""
        if entity not in ExportService.SUPPORTED_ENTITIES:
            raise ValueError(f"Entity {entity} not supported for export")
        
        # Get data from MongoDB
        query = filters or {}
        data = await db[entity].find(query, {"_id": 0}).to_list(10000)
        
        if not data:
            # Return empty CSV with headers
            return b"No data found"
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Convert to CSV
        output = io.StringIO()
        df.to_csv(output, index=False, encoding='utf-8-sig')  # BOM for Excel compatibility
        return output.getvalue().encode('utf-8-sig')
    
    @staticmethod
    async def export_to_excel(db: AsyncIOMotorDatabase, entity: str, filters: Dict = None) -> bytes:
        """Export entity to Excel format"""
        if entity not in ExportService.SUPPORTED_ENTITIES:
            raise ValueError(f"Entity {entity} not supported for export")
        
        query = filters or {}
        data = await db[entity].find(query, {"_id": 0}).to_list(10000)
        
        if not data:
            raise ValueError("No data to export")
        
        df = pd.DataFrame(data)
        
        # Convert to Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=entity, index=False)
        
        return output.getvalue()
    
    @staticmethod
    async def export_to_json(db: AsyncIOMotorDatabase, entity: str, filters: Dict = None) -> bytes:
        """Export entity to JSON format"""
        if entity not in ExportService.SUPPORTED_ENTITIES:
            raise ValueError(f"Entity {entity} not supported for export")
        
        query = filters or {}
        data = await db[entity].find(query, {"_id": 0}).to_list(10000)
        
        return json.dumps(data, indent=2, ensure_ascii=False).encode('utf-8')


class ImportService:
    """Handles data import from multiple formats"""
    
    @staticmethod
    async def import_from_csv(db: AsyncIOMotorDatabase, entity: str, file_content: bytes, mode: str = "append"):
        """Import data from CSV"""
        # Parse CSV
        csv_str = file_content.decode('utf-8-sig')
        df = pd.read_csv(io.StringIO(csv_str))
        
        # Convert to list of dicts
        records = df.to_dict('records')
        
        return await ImportService._import_records(db, entity, records, mode)
    
    @staticmethod
    async def import_from_excel(db: AsyncIOMotorDatabase, entity: str, file_content: bytes, mode: str = "append"):
        """Import data from Excel"""
        df = pd.read_excel(io.BytesIO(file_content))
        records = df.to_dict('records')
        
        return await ImportService._import_records(db, entity, records, mode)
    
    @staticmethod
    async def import_from_json(db: AsyncIOMotorDatabase, entity: str, file_content: bytes, mode: str = "append"):
        """Import data from JSON"""
        records = json.loads(file_content.decode('utf-8'))
        
        return await ImportService._import_records(db, entity, records, mode)
    
    @staticmethod
    async def _import_records(db: AsyncIOMotorDatabase, entity: str, records: List[Dict], mode: str):
        """Import records based on mode"""
        if mode == "replace":
            # Clear collection and insert
            await db[entity].delete_many({})
            result = await db[entity].insert_many(records)
            return {"mode": "replace", "inserted": len(result.inserted_ids)}
        
        elif mode == "update":
            # Update existing records by ID
            updated = 0
            inserted = 0
            for record in records:
                if "id" in record:
                    result = await db[entity].update_one(
                        {"id": record["id"]},
                        {"$set": record},
                        upsert=True
                    )
                    if result.matched_count > 0:
                        updated += 1
                    else:
                        inserted += 1
            return {"mode": "update", "updated": updated, "inserted": inserted}
        
        else:  # append
            # Add timestamps if not present
            for record in records:
                if "created_at" not in record:
                    record["created_at"] = datetime.now(timezone.utc).isoformat()
            
            result = await db[entity].insert_many(records)
            return {"mode": "append", "inserted": len(result.inserted_ids)}


class GitHubExportService:
    """Export database schema and configuration to GitHub"""
    
    @staticmethod
    async def export_schema(db: AsyncIOMotorDatabase) -> Dict[str, Any]:
        """Export database schema as JSON"""
        collections = await db.list_collection_names()
        
        schema = {
            "collections": [],
            "export_date": datetime.now(timezone.utc).isoformat(),
            "version": "1.0"
        }
        
        for collection_name in collections:
            # Get sample document to infer schema
            sample = await db[collection_name].find_one()
            
            if sample:
                collection_schema = {
                    "name": collection_name,
                    "fields": {},
                    "count": await db[collection_name].count_documents({})
                }
                
                # Infer types from sample
                for field, value in sample.items():
                    if field != "_id":
                        collection_schema["fields"][field] = type(value).__name__
                
                schema["collections"].append(collection_schema)
        
        return schema
    
    @staticmethod
    def generate_readme(schema: Dict) -> str:
        """Generate README.md for GitHub export"""
        readme = f"""# ERP System Database Schema

Exported: {schema['export_date']}
Version: {schema['version']}

## Collections

Total Collections: {len(schema['collections'])}

"""
        
        for collection in schema['collections']:
            readme += f"""### {collection['name']}

Document Count: {collection['count']}

Fields:
"""
            for field, field_type in collection['fields'].items():
                readme += f"- `{field}` ({field_type})\n"
            readme += "\n"
        
        return readme


class BackupService:
    """Handle daily cloud backups"""
    
    @staticmethod
    async def create_backup(db: AsyncIOMotorDatabase) -> Dict[str, Any]:
        """Create full database backup"""
        backup_data = {
            "backup_date": datetime.now(timezone.utc).isoformat(),
            "collections": {}
        }
        
        collections = await db.list_collection_names()
        
        for collection_name in collections:
            data = await db[collection_name].find({}, {"_id": 0}).to_list(100000)
            backup_data["collections"][collection_name] = data
        
        # Save to file
        backup_filename = f"backup_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
        backup_path = os.path.join("/app/backups", backup_filename)
        
        os.makedirs("/app/backups", exist_ok=True)
        
        with open(backup_path, 'w') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
        
        # Get file size
        file_size = os.path.getsize(backup_path)
        
        return {
            "filename": backup_filename,
            "path": backup_path,
            "size_bytes": file_size,
            "size_mb": round(file_size / 1024 / 1024, 2),
            "collections_backed_up": len(collections),
            "created_at": backup_data["backup_date"]
        }
    
    @staticmethod
    async def restore_backup(db: AsyncIOMotorDatabase, backup_path: str):
        """Restore database from backup"""
        with open(backup_path, 'r') as f:
            backup_data = json.load(f)
        
        restored_collections = 0
        
        for collection_name, data in backup_data["collections"].items():
            if data:
                # Clear existing data
                await db[collection_name].delete_many({})
                # Restore
                await db[collection_name].insert_many(data)
                restored_collections += 1
        
        return {
            "restored_collections": restored_collections,
            "backup_date": backup_data["backup_date"]
        }
