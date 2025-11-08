from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
import anthropic
import os
import logging
import json

logger = logging.getLogger(__name__)


class AIService:
    """AI-powered intelligence for ERP system using Emergent LLM key"""
    
    def __init__(self):
        self.api_key = os.environ.get("EMERGENT_LLM_KEY")
        if not self.api_key:
            logger.warning("EMERGENT_LLM_KEY not configured - AI features will be limited")
        self.client = anthropic.Anthropic(api_key=self.api_key) if self.api_key else None
    
    async def analyze_cost_variance(
        self, 
        db: AsyncIOMotorDatabase,
        production_order_id: str
    ) -> Dict[str, Any]:
        """
        Smart cost variance analysis with AI insights
        
        Analyzes material, labor, and overhead variances
        Provides root cause analysis and recommendations
        """
        
        # Get production order data
        po = await db.production_orders.find_one({"id": production_order_id})
        if not po:
            raise ValueError("Production order not found")
        
        # Get BOM for standard costs
        bom = await db.boms.find_one({"id": po["bom_id"]})
        
        # Get actual WIP costs
        wip_transactions = await db.wip_transactions.find({
            "production_order_id": production_order_id
        }).to_list(1000)
        
        # Calculate variances
        material_costs = sum(w["amount"] for w in wip_transactions if w["transaction_type"] == "material")
        labor_costs = sum(w["amount"] for w in wip_transactions if w["transaction_type"] == "labor")
        overhead_costs = sum(w["amount"] for w in wip_transactions if w["transaction_type"] == "overhead")
        
        # Get standard costs (simplified - would be calculated from BOM)
        standard_material = 1000  # Example
        standard_labor = 500
        standard_overhead = 300
        
        material_variance = material_costs - standard_material
        labor_variance = labor_costs - standard_labor
        overhead_variance = overhead_costs - standard_overhead
        total_variance = material_variance + labor_variance + overhead_variance
        
        # Build context for AI
        context = f"""
Production Order: {po['po_number']}
Product: {po['product_id']}
Quantity: {po['quantity']}

COST ANALYSIS:
Material Costs:
  Standard: ${standard_material}
  Actual: ${material_costs}
  Variance: ${material_variance} ({(material_variance/standard_material*100):.1f}%)

Labor Costs:
  Standard: ${standard_labor}
  Actual: ${labor_costs}
  Variance: ${labor_variance} ({(labor_variance/standard_labor*100):.1f}%)

Overhead Costs:
  Standard: ${standard_overhead}
  Actual: ${overhead_costs}
  Variance: ${overhead_variance} ({(overhead_variance/standard_overhead*100):.1f}%)

Total Variance: ${total_variance}
"""
        
        # Generate AI analysis
        if self.client:
            prompt = f"""
You are a manufacturing cost analyst. Analyze this cost variance data and provide:

{context}

Please provide:
1. ROOT CAUSE ANALYSIS: Why did variances occur? (3-4 specific reasons)
2. IMPACT ASSESSMENT: How significant is this variance?
3. RECOMMENDATIONS: What actions should be taken? (3-4 actionable items)
4. PREVENTIVE MEASURES: How to avoid similar variances in future?

Keep analysis concise, practical, and focused on manufacturing context.
"""
            
            try:
                message = self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                ai_analysis = message.content[0].text
            except Exception as e:
                logger.error(f"AI analysis failed: {e}")
                ai_analysis = "AI analysis unavailable"
        else:
            ai_analysis = "Configure EMERGENT_LLM_KEY for AI insights"
        
        return {
            "production_order_id": production_order_id,
            "variances": {
                "material": {
                    "standard": standard_material,
                    "actual": material_costs,
                    "variance": material_variance,
                    "variance_percentage": (material_variance/standard_material*100) if standard_material > 0 else 0
                },
                "labor": {
                    "standard": standard_labor,
                    "actual": labor_costs,
                    "variance": labor_variance,
                    "variance_percentage": (labor_variance/standard_labor*100) if standard_labor > 0 else 0
                },
                "overhead": {
                    "standard": standard_overhead,
                    "actual": overhead_costs,
                    "variance": overhead_variance,
                    "variance_percentage": (overhead_variance/standard_overhead*100) if standard_overhead > 0 else 0
                },
                "total": total_variance
            },
            "ai_analysis": ai_analysis,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    
    async def forecast_production(
        self,
        db: AsyncIOMotorDatabase,
        forecast_days: int = 30
    ) -> Dict[str, Any]:
        """
        AI-powered production forecasting
        
        Analyzes historical production data and predicts future needs
        """
        
        # Get historical production orders (last 90 days)
        cutoff = (datetime.now(timezone.utc) - timedelta(days=90)).isoformat()[:10]
        historical_orders = await db.production_orders.find({
            "created_at": {"$gte": cutoff}
        }).to_list(1000)
        
        # Aggregate by product
        product_demand = {}
        for order in historical_orders:
            product_id = order["product_id"]
            if product_id not in product_demand:
                product_demand[product_id] = []
            product_demand[product_id].append({
                "date": order["created_at"][:10],
                "quantity": order["quantity"]
            })
        
        # Build forecast context
        context_parts = []
        for product_id, orders in product_demand.items():
            product = await db.products.find_one({"id": product_id})
            total_qty = sum(o["quantity"] for o in orders)
            avg_qty = total_qty / len(orders) if orders else 0
            
            context_parts.append(f"""
Product: {product['name']}
  Historical Orders: {len(orders)} orders in 90 days
  Total Quantity: {total_qty}
  Average per Order: {avg_qty:.1f}
  Trend: {len(orders)/3:.1f} orders/month
""")
        
        context = "\n".join(context_parts)
        
        # Generate AI forecast
        if self.client:
            prompt = f"""
You are a production planning analyst. Based on this historical data, forecast production needs for the next {forecast_days} days.

HISTORICAL DATA (Last 90 days):
{context}

Provide forecast for next {forecast_days} days:
1. DEMAND FORECAST: Expected orders per product
2. PRODUCTION RECOMMENDATIONS: Suggested production quantities
3. CAPACITY PLANNING: Work center utilization estimates
4. RISK FACTORS: What could impact this forecast?

Format as practical production plan.
"""
            
            try:
                message = self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1500,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                forecast_text = message.content[0].text
            except Exception as e:
                logger.error(f"Forecast generation failed: {e}")
                forecast_text = "AI forecast unavailable"
        else:
            forecast_text = "Configure EMERGENT_LLM_KEY for AI forecasting"
        
        return {
            "forecast_period_days": forecast_days,
            "historical_period_days": 90,
            "products_analyzed": len(product_demand),
            "total_historical_orders": len(historical_orders),
            "forecast": forecast_text,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    
    async def inventory_reorder_recommendations(
        self,
        db: AsyncIOMotorDatabase
    ) -> Dict[str, Any]:
        """
        Smart inventory reorder recommendations using AI
        
        Analyzes consumption patterns, lead times, and forecasts
        """
        
        # Get current inventory levels
        inventory = await db.inventory_items.find({}).to_list(1000)
        
        # Get recent stock movements (last 30 days)
        cutoff = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()[:10]
        stock_moves = await db.stock_moves.find({
            "created_at": {"$gte": cutoff}
        }).to_list(1000)
        
        # Analyze consumption by product
        product_analysis = {}
        for item in inventory:
            product_id = item["product_id"]
            product = await db.products.find_one({"id": product_id})
            
            # Calculate consumption
            issues = [m for m in stock_moves if m["product_id"] == product_id and m["move_type"] == "issue"]
            total_issued = sum(m["quantity"] for m in issues)
            avg_daily_consumption = total_issued / 30 if issues else 0
            
            current_qty = item.get("quantity", 0)
            days_of_stock = current_qty / avg_daily_consumption if avg_daily_consumption > 0 else 999
            
            if days_of_stock < 30:  # Less than 30 days stock
                product_analysis[product_id] = {
                    "product_name": product["name"],
                    "current_quantity": current_qty,
                    "avg_daily_consumption": avg_daily_consumption,
                    "days_of_stock": days_of_stock,
                    "total_consumed_30d": total_issued
                }
        
        # Build context for AI
        context_parts = []
        for product_id, data in product_analysis.items():
            context_parts.append(f"""
Product: {data['product_name']}
  Current Stock: {data['current_quantity']}
  Avg Daily Consumption: {data['avg_daily_consumption']:.2f}
  Days of Stock Remaining: {data['days_of_stock']:.1f}
  Priority: {'URGENT' if data['days_of_stock'] < 7 else 'HIGH' if data['days_of_stock'] < 15 else 'MEDIUM'}
""")
        
        if not context_parts:
            context_parts.append("All products have adequate stock levels (30+ days)")
        
        context = "\n".join(context_parts)
        
        # Generate AI recommendations
        if self.client:
            prompt = f"""
You are an inventory management specialist. Based on consumption patterns, provide smart reorder recommendations.

CURRENT INVENTORY STATUS:
{context}

Provide recommendations:
1. IMMEDIATE ACTIONS: What to reorder now (within 7 days stock)
2. PLANNED ORDERS: What to reorder soon (7-15 days stock)
3. REORDER QUANTITIES: Suggested order quantities (consider MOQ, lead time)
4. SUPPLIER SELECTION: If multiple suppliers, which to prioritize
5. OPTIMIZATION TIPS: How to reduce stockouts and carrying costs

Format as actionable purchasing plan.
"""
            
            try:
                message = self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1500,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                recommendations = message.content[0].text
            except Exception as e:
                logger.error(f"Reorder recommendations failed: {e}")
                recommendations = "AI recommendations unavailable"
        else:
            recommendations = "Configure EMERGENT_LLM_KEY for AI recommendations"
        
        return {
            "products_analyzed": len(inventory),
            "products_needing_reorder": len(product_analysis),
            "analysis_period_days": 30,
            "product_details": list(product_analysis.values()),
            "recommendations": recommendations,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    
    async def chat_assistant(
        self,
        db: AsyncIOMotorDatabase,
        user_query: str,
        conversation_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        AI chat assistant for querying ERP data
        
        Natural language interface to ERP system
        """
        
        if not self.client:
            return {
                "response": "Chat assistant requires EMERGENT_LLM_KEY configuration",
                "data": None
            }
        
        # Gather relevant ERP data based on query keywords
        context_data = await self._build_context_for_query(db, user_query)
        
        # Build conversation
        messages = []
        if conversation_history:
            for msg in conversation_history[-5:]:  # Last 5 messages
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        # Add system context
        system_prompt = f"""
You are an AI assistant for a manufacturing ERP system. You help users query and understand their business data.

AVAILABLE DATA CONTEXT:
{context_data}

Guidelines:
- Answer questions about production, inventory, quality, HR, and finance
- Provide specific data when available
- Suggest actions based on data insights
- If data is not in context, ask user to be more specific
- Keep responses concise and actionable
"""
        
        messages.append({
            "role": "user",
            "content": user_query
        })
        
        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                system=system_prompt,
                messages=messages
            )
            
            assistant_response = response.content[0].text
        except Exception as e:
            logger.error(f"Chat assistant error: {e}")
            assistant_response = "I apologize, I encountered an error processing your request."
        
        return {
            "query": user_query,
            "response": assistant_response,
            "context_used": context_data[:500],  # First 500 chars
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def _build_context_for_query(
        self,
        db: AsyncIOMotorDatabase,
        query: str
    ) -> str:
        """Build relevant context based on user query"""
        
        query_lower = query.lower()
        context_parts = []
        
        # Production-related queries
        if any(word in query_lower for word in ["production", "order", "manufacturing", "output"]):
            recent_pos = await db.production_orders.find({}).sort("created_at", -1).to_list(10)
            if recent_pos:
                context_parts.append(f"Recent Production Orders: {len(recent_pos)} orders")
                completed = len([po for po in recent_pos if po.get("state") == "posted"])
                context_parts.append(f"Completed: {completed}, In Progress: {len(recent_pos) - completed}")
        
        # Inventory-related queries
        if any(word in query_lower for word in ["inventory", "stock", "warehouse", "material"]):
            inventory = await db.inventory_items.find({}).to_list(100)
            total_items = len(inventory)
            low_stock = len([i for i in inventory if i.get("quantity", 0) < 10])
            context_parts.append(f"Inventory: {total_items} items tracked, {low_stock} low stock items")
        
        # Quality-related queries
        if any(word in query_lower for word in ["quality", "qc", "defect", "inspection"]):
            qc_checks = await db.quality_checks.find({}).sort("inspection_date", -1).to_list(20)
            if qc_checks:
                passed = len([q for q in qc_checks if q.get("status") == "passed"])
                context_parts.append(f"Recent QC: {len(qc_checks)} checks, {passed} passed ({passed/len(qc_checks)*100:.1f}%)")
        
        # Employee/HR queries
        if any(word in query_lower for word in ["employee", "staff", "attendance", "payroll"]):
            employees = await db.employees.find({"is_active": True}).to_list(100)
            context_parts.append(f"Active Employees: {len(employees)}")
        
        # Supplier/Customer queries
        if "supplier" in query_lower:
            suppliers = await db.suppliers.find({"is_active": True}).to_list(50)
            context_parts.append(f"Active Suppliers: {len(suppliers)}")
        
        if "customer" in query_lower:
            customers = await db.customers.find({"is_active": True}).to_list(50)
            context_parts.append(f"Active Customers: {len(customers)}")
        
        # General metrics
        if any(word in query_lower for word in ["kpi", "metric", "performance", "summary"]):
            latest_kpi = await db.kpi_snapshots.find_one(sort=[("date", -1)])
            if latest_kpi:
                context_parts.append(f"Latest KPI Date: {latest_kpi['date']}")
                if "metrics" in latest_kpi:
                    context_parts.append(f"Metrics: {json.dumps(latest_kpi['metrics'])}")
        
        return "\n".join(context_parts) if context_parts else "No specific context data available for this query"


# Singleton instance
ai_service = AIService()
