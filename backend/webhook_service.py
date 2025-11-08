from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import httpx
import logging
from pydantic import BaseModel, HttpUrl
import uuid
import json

logger = logging.getLogger(__name__)

webhook_router = APIRouter(prefix="/api/webhooks")


class WebhookSubscription(BaseModel):
    id: str = None
    url: HttpUrl
    events: List[str]  # ["production_order.created", "inventory.low_stock", etc.]
    is_active: bool = True
    secret: Optional[str] = None
    created_at: str = None


class WebhookEvent(BaseModel):
    event_type: str
    data: Dict[str, Any]
    timestamp: str


class WebhookService:
    """Manage webhook subscriptions and deliveries"""
    
    SUPPORTED_EVENTS = [
        "production_order.created",
        "production_order.completed",
        "work_order.created",
        "work_order.completed",
        "inventory.low_stock",
        "inventory.adjusted",
        "quality_check.failed",
        "approval.requested",
        "approval.approved",
        "approval.rejected",
        "payroll.processed",
        "attendance.marked",
        "maintenance.due"
    ]
    
    @staticmethod
    async def subscribe(db: AsyncIOMotorDatabase, subscription: WebhookSubscription) -> Dict:
        """Create webhook subscription"""
        # Validate events
        for event in subscription.events:
            if event not in WebhookService.SUPPORTED_EVENTS:
                raise ValueError(f"Unsupported event: {event}")
        
        subscription_data = {
            "id": str(uuid.uuid4()),
            "url": str(subscription.url),
            "events": subscription.events,
            "is_active": subscription.is_active,
            "secret": subscription.secret,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.webhook_subscriptions.insert_one(subscription_data)
        
        return subscription_data
    
    @staticmethod
    async def trigger_event(
        db: AsyncIOMotorDatabase,
        event_type: str,
        data: Dict[str, Any],
        background_tasks: BackgroundTasks
    ):
        """Trigger webhook event to all subscribers"""
        # Get active subscriptions for this event
        subscriptions = await db.webhook_subscriptions.find({
            "is_active": True,
            "events": event_type
        }).to_list(100)
        
        event = {
            "event_type": event_type,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Deliver to all subscribers (async in background)
        for subscription in subscriptions:
            background_tasks.add_task(
                WebhookService._deliver_webhook,
                subscription["url"],
                event,
                subscription.get("secret")
            )
    
    @staticmethod
    async def _deliver_webhook(url: str, event: Dict, secret: Optional[str] = None):
        """Deliver webhook to subscriber"""
        headers = {"Content-Type": "application/json"}
        
        if secret:
            # Add signature for verification
            import hmac
            import hashlib
            
            payload = json.dumps(event)
            signature = hmac.new(
                secret.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()
            headers["X-Webhook-Signature"] = signature
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=event, headers=headers)
                
                if response.status_code >= 200 and response.status_code < 300:
                    logger.info(f"Webhook delivered to {url}: {response.status_code}")
                else:
                    logger.warning(f"Webhook failed to {url}: {response.status_code}")
        except Exception as e:
            logger.error(f"Webhook delivery error to {url}: {e}")


class RESTAPIDocumentation:
    """Generate REST API documentation"""
    
    @staticmethod
    def generate_openapi_spec(app) -> Dict:
        """Generate OpenAPI 3.0 specification"""
        return app.openapi()
    
    @staticmethod
    def generate_postman_collection(base_url: str) -> Dict:
        """Generate Postman collection"""
        return {
            "info": {
                "name": "ERP System API",
                "description": "Complete Manufacturing ERP REST API",
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
            },
            "item": [
                {
                    "name": "Authentication",
                    "item": [
                        {
                            "name": "Login",
                            "request": {
                                "method": "POST",
                                "header": [{"key": "Content-Type", "value": "application/json"}],
                                "url": f"{base_url}/api/auth/login",
                                "body": {
                                    "mode": "raw",
                                    "raw": json.dumps({"email": "user@example.com", "password": "password"})
                                }
                            }
                        }
                    ]
                },
                {
                    "name": "Products",
                    "item": [
                        {
                            "name": "Get Products",
                            "request": {
                                "method": "GET",
                                "url": f"{base_url}/api/products"
                            }
                        },
                        {
                            "name": "Create Product",
                            "request": {
                                "method": "POST",
                                "url": f"{base_url}/api/products",
                                "body": {
                                    "mode": "raw",
                                    "raw": json.dumps({"code": "PROD001", "name": "Product 1", "unit": "pcs"})
                                }
                            }
                        }
                    ]
                }
                # Add more endpoints...
            ]
        }
