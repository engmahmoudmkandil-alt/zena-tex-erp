from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class CostingService:
    """Handles FIFO and Moving Average costing calculations"""
    
    @staticmethod
    async def calculate_cost(db: AsyncIOMotorDatabase, product_id: str, warehouse_id: str, 
                           quantity: float, transaction_type: str, 
                           cost_per_unit: Optional[float] = None) -> Dict[str, Any]:
        """
        Calculate cost for inventory transaction
        Returns: {total_cost, unit_cost, fifo_layers_consumed}
        """
        # Get product costing record
        costing = await db.product_costing.find_one({
            "product_id": product_id,
            "warehouse_id": warehouse_id
        })
        
        if not costing:
            # Initialize costing record
            costing = {
                "product_id": product_id,
                "warehouse_id": warehouse_id,
                "costing_method": "moving_average",
                "current_average_cost": 0.0,
                "total_quantity": 0.0,
                "total_value": 0.0,
                "fifo_layers": []
            }
            await db.product_costing.insert_one(costing)
        
        method = costing.get("costing_method", "moving_average")
        
        if transaction_type == "receipt":
            return await CostingService._handle_receipt(
                db, costing, quantity, cost_per_unit or 0.0, method
            )
        elif transaction_type in ["issue", "consumption"]:
            return await CostingService._handle_issue(
                db, costing, quantity, method
            )
        else:
            raise ValueError(f"Unknown transaction type: {transaction_type}")
    
    @staticmethod
    async def _handle_receipt(db, costing, quantity, cost_per_unit, method):
        """Handle receipt transaction"""
        total_cost = quantity * cost_per_unit
        
        if method == "moving_average":
            # Update moving average
            old_value = costing.get("total_value", 0.0)
            old_qty = costing.get("total_quantity", 0.0)
            new_value = old_value + total_cost
            new_qty = old_qty + quantity
            new_avg = new_value / new_qty if new_qty > 0 else cost_per_unit
            
            await db.product_costing.update_one(
                {"_id": costing["_id"]},
                {"$set": {
                    "current_average_cost": new_avg,
                    "total_quantity": new_qty,
                    "total_value": new_value,
                    "last_updated": datetime.now(timezone.utc).isoformat()
                }}
            )
            
            return {
                "total_cost": total_cost,
                "unit_cost": cost_per_unit,
                "new_average_cost": new_avg
            }
        
        elif method == "fifo":
            # Add FIFO layer
            layer = {
                "quantity": quantity,
                "cost": cost_per_unit,
                "date": datetime.now(timezone.utc).isoformat(),
                "remaining": quantity
            }
            
            fifo_layers = costing.get("fifo_layers", [])
            fifo_layers.append(layer)
            
            new_qty = costing.get("total_quantity", 0.0) + quantity
            new_value = costing.get("total_value", 0.0) + total_cost
            
            await db.product_costing.update_one(
                {"_id": costing["_id"]},
                {"$set": {
                    "fifo_layers": fifo_layers,
                    "total_quantity": new_qty,
                    "total_value": new_value,
                    "last_updated": datetime.now(timezone.utc).isoformat()
                }}
            )
            
            return {
                "total_cost": total_cost,
                "unit_cost": cost_per_unit
            }
    
    @staticmethod
    async def _handle_issue(db, costing, quantity, method):
        """Handle issue/consumption transaction"""
        if method == "moving_average":
            avg_cost = costing.get("current_average_cost", 0.0)
            total_cost = quantity * avg_cost
            
            new_qty = costing.get("total_quantity", 0.0) - quantity
            new_value = costing.get("total_value", 0.0) - total_cost
            
            if new_qty < 0:
                raise ValueError("Insufficient inventory (negative stock prevented)")
            
            await db.product_costing.update_one(
                {"_id": costing["_id"]},
                {"$set": {
                    "total_quantity": new_qty,
                    "total_value": new_value,
                    "last_updated": datetime.now(timezone.utc).isoformat()
                }}
            )
            
            return {
                "total_cost": total_cost,
                "unit_cost": avg_cost
            }
        
        elif method == "fifo":
            # Consume FIFO layers
            fifo_layers = costing.get("fifo_layers", [])
            remaining_to_issue = quantity
            total_cost = 0.0
            consumed_layers = []
            
            for layer in fifo_layers:
                if remaining_to_issue <= 0:
                    break
                
                available = layer.get("remaining", 0.0)
                if available <= 0:
                    continue
                
                consumed = min(available, remaining_to_issue)
                cost = consumed * layer["cost"]
                total_cost += cost
                
                layer["remaining"] = available - consumed
                remaining_to_issue -= consumed
                consumed_layers.append({
                    "quantity": consumed,
                    "cost": layer["cost"]
                })
            
            if remaining_to_issue > 0:
                raise ValueError(f"Insufficient inventory in FIFO layers (short by {remaining_to_issue})")
            
            # Remove fully consumed layers
            fifo_layers = [l for l in fifo_layers if l.get("remaining", 0) > 0]
            
            new_qty = costing.get("total_quantity", 0.0) - quantity
            new_value = costing.get("total_value", 0.0) - total_cost
            
            await db.product_costing.update_one(
                {"_id": costing["_id"]},
                {"$set": {
                    "fifo_layers": fifo_layers,
                    "total_quantity": new_qty,
                    "total_value": new_value,
                    "last_updated": datetime.now(timezone.utc).isoformat()
                }}
            )
            
            avg_unit_cost = total_cost / quantity if quantity > 0 else 0.0
            
            return {
                "total_cost": total_cost,
                "unit_cost": avg_unit_cost,
                "consumed_layers": consumed_layers
            }


class BackflushService:
    """Handles backflush material consumption"""
    
    @staticmethod
    async def backflush_production_order(db: AsyncIOMotorDatabase, 
                                        production_order_id: str,
                                        actual_quantity: float) -> List[Dict[str, Any]]:
        """
        Backflush materials based on BOM for actual production quantity
        Returns list of backflushed items
        """
        # Get production order
        po = await db.production_orders.find_one({"id": production_order_id})
        if not po:
            raise ValueError("Production order not found")
        
        # Get BOM
        bom = await db.boms.find_one({"id": po["bom_id"]})
        if not bom:
            raise ValueError("BOM not found")
        
        backflushed_items = []
        
        # Calculate consumption for each component
        for component in bom.get("components", []):
            component_id = component["product_id"]
            planned_qty_per_unit = component["quantity"]
            total_planned = planned_qty_per_unit * actual_quantity
            
            # Record backflush
            backflush_record = {
                "id": str(uuid.uuid4()),
                "production_order_id": production_order_id,
                "product_id": po["product_id"],
                "component_id": component_id,
                "planned_quantity": total_planned,
                "actual_quantity": total_planned,  # Can be adjusted for scrap
                "scrap_quantity": 0.0,
                "variance": 0.0,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            await db.backflush_records.insert_one(backflush_record)
            backflushed_items.append(backflush_record)
            
            # Issue inventory (with costing)
            # This would call inventory update and costing service
        
        return backflushed_items


class WIPService:
    """Handles Work-in-Progress tracking"""
    
    @staticmethod
    async def add_wip_cost(db: AsyncIOMotorDatabase,
                          production_order_id: str,
                          cost_category: str,
                          amount: float,
                          quantity: Optional[float] = None,
                          notes: Optional[str] = None):
        """Add cost to WIP"""
        wip_transaction = {
            "id": str(uuid.uuid4()),
            "production_order_id": production_order_id,
            "transaction_type": cost_category,
            "cost_category": cost_category,
            "amount": amount,
            "quantity": quantity,
            "notes": notes,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.wip_transactions.insert_one(wip_transaction)
        
        # Update production order WIP cost
        await db.production_orders.update_one(
            {"id": production_order_id},
            {"$inc": {"wip_cost": amount}}
        )
        
        return wip_transaction
    
    @staticmethod
    async def close_production_order(db: AsyncIOMotorDatabase, production_order_id: str):
        """Close production order and move WIP to finished goods"""
        po = await db.production_orders.find_one({"id": production_order_id})
        if not po:
            raise ValueError("Production order not found")
        
        # Calculate total WIP cost
        wip_transactions = await db.wip_transactions.find({
            "production_order_id": production_order_id
        }).to_list(1000)
        
        total_wip = sum(t.get("amount", 0) for t in wip_transactions)
        
        # Update production order
        await db.production_orders.update_one(
            {"id": production_order_id},
            {"$set": {
                "actual_cost": total_wip,
                "state": "posted"
            }}
        )
        
        # Create finished goods receipt with WIP cost
        unit_cost = total_wip / po["quantity"] if po["quantity"] > 0 else 0
        
        return {
            "total_wip_cost": total_wip,
            "quantity_produced": po["quantity"],
            "unit_cost": unit_cost
        }


class PayrollService:
    """Handles payroll calculations with formula engine"""
    
    @staticmethod
    async def calculate_payroll(db: AsyncIOMotorDatabase,
                               employee_id: str,
                               period: str,
                               basic_salary: float,
                               formula_id: Optional[str] = None) -> Dict[str, Any]:
        """Calculate payroll using formula"""
        # Get attendance data for period
        year, month = period.split("-")
        attendance_records = await db.attendance.find({
            "employee_id": employee_id,
            "date": {"$regex": f"^{year}-{month}"}
        }).to_list(1000)
        
        present_days = sum(1 for a in attendance_records if a.get("status") == "present")
        overtime_hours = sum(a.get("overtime_hours", 0) for a in attendance_records)
        
        # Calculate based on formula if provided
        if formula_id:
            formula = await db.payroll_formulas.find_one({"id": formula_id})
            if formula:
                # Safe eval with limited scope
                variables = {
                    "basic_salary": basic_salary,
                    "present_days": present_days,
                    "working_days": len(attendance_records),
                    "overtime_hours": overtime_hours
                }
                try:
                    gross_salary = eval(formula["formula_expression"], {"__builtins__": {}}, variables)
                except Exception as e:
                    logger.error(f"Formula evaluation error: {e}")
                    gross_salary = basic_salary
            else:
                gross_salary = basic_salary
        else:
            # Default calculation
            gross_salary = basic_salary
        
        # Calculate deductions (simplified)
        deductions = gross_salary * 0.1  # 10% deduction
        net_salary = gross_salary - deductions
        
        return {
            "gross_salary": gross_salary,
            "deductions": deductions,
            "net_salary": net_salary,
            "present_days": present_days,
            "working_days": len(attendance_records),
            "overtime_hours": overtime_hours
        }


import uuid
