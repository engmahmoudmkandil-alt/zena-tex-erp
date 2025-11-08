from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


class ApprovalService:
    """Handles multi-level approval workflows"""
    
    # Define approval chains
    APPROVAL_CHAINS = {
        "purchase_order": [
            {"role": "Production Manager", "order": 0, "required": True},
            {"role": "Accountant", "order": 1, "required": True},
            {"role": "Admin", "order": 2, "required": True}
        ],
        "payroll": [
            {"role": "HR Officer", "order": 0, "required": True},
            {"role": "Accountant", "order": 1, "required": True},
            {"role": "CEO/Viewer", "order": 2, "required": True}
        ],
        "inventory_adjustment": [
            {"role": "Inventory Officer", "order": 0, "required": True},
            {"role": "Admin", "order": 1, "required": True}
        ]
    }
    
    @staticmethod
    async def initialize_chains(db: AsyncIOMotorDatabase):
        """Initialize approval chains in database"""
        for doc_type, chain_steps in ApprovalService.APPROVAL_CHAINS.items():
            existing = await db.approval_chains.find_one({"document_type": doc_type})
            if not existing:
                chain = {
                    "id": f"chain_{doc_type}",
                    "document_type": doc_type,
                    "chain_steps": chain_steps,
                    "is_active": True,
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
                await db.approval_chains.insert_one(chain)
                logger.info(f"Initialized approval chain for {doc_type}")
    
    @staticmethod
    async def create_approval_request(
        db: AsyncIOMotorDatabase,
        document_type: str,
        document_id: str,
        requested_by: str
    ) -> Dict[str, Any]:
        """Create new approval request"""
        
        # Get approval chain
        chain = await db.approval_chains.find_one({"document_type": document_type, "is_active": True})
        if not chain:
            raise ValueError(f"No approval chain found for {document_type}")
        
        # Create approval request
        approval_request = {
            "id": f"apr_{document_id}",
            "document_type": document_type,
            "document_id": document_id,
            "chain_id": chain["id"],
            "current_step": 0,
            "status": "pending",
            "approvals": [],
            "requested_by": requested_by,
            "requested_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.approval_requests.insert_one(approval_request)
        
        # Notify first approver
        await ApprovalService._notify_approvers(db, approval_request, chain)
        
        return approval_request
    
    @staticmethod
    async def _notify_approvers(db: AsyncIOMotorDatabase, approval_request: Dict, chain: Dict):
        """Notify users who can approve at current step"""
        current_step = approval_request["current_step"]
        step_info = chain["chain_steps"][current_step]
        required_role = step_info["role"]
        
        # Get users with this role
        users = await db.users.find({"role": required_role, "is_active": True}).to_list(100)
        
        for user in users:
            notification = {
                "type": "approval_request",
                "channel": "email",
                "recipient_id": user["id"],
                "recipient_email": user.get("email"),
                "title": f"Approval Required: {approval_request['document_type']}",
                "message": f"Please review and approve {approval_request['document_type']} (ID: {approval_request['document_id']})",
                "data": {
                    "approval_id": approval_request["id"],
                    "document_type": approval_request["document_type"],
                    "document_id": approval_request["document_id"]
                },
                "is_read": False,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await db.notifications.insert_one(notification)
    
    @staticmethod
    async def approve(
        db: AsyncIOMotorDatabase,
        approval_id: str,
        approver_id: str,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Approve at current step"""
        
        # Get approval request
        approval_request = await db.approval_requests.find_one({"id": approval_id})
        if not approval_request:
            raise ValueError("Approval request not found")
        
        if approval_request["status"] != "pending":
            raise ValueError("Approval request is not pending")
        
        # Verify approver has the right role
        approver = await db.users.find_one({"id": approver_id})
        chain = await db.approval_chains.find_one({"id": approval_request["chain_id"]})
        current_step_info = chain["chain_steps"][approval_request["current_step"]]
        
        if approver["role"] != current_step_info["role"]:
            raise ValueError(f"User does not have required role: {current_step_info['role']}")
        
        # Record approval
        approval_entry = {
            "step": approval_request["current_step"],
            "approver_id": approver_id,
            "approver_name": approver["name"],
            "status": "approved",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "notes": notes
        }
        
        approvals = approval_request.get("approvals", [])
        approvals.append(approval_entry)
        
        # Check if this was the last step
        if approval_request["current_step"] >= len(chain["chain_steps"]) - 1:
            # All approvals complete
            await db.approval_requests.update_one(
                {"id": approval_id},
                {"$set": {
                    "status": "approved",
                    "approvals": approvals
                }}
            )
            
            # Update document state
            await ApprovalService._finalize_approval(db, approval_request)
            
            status = "approved"
        else:
            # Move to next step
            next_step = approval_request["current_step"] + 1
            await db.approval_requests.update_one(
                {"id": approval_id},
                {"$set": {
                    "current_step": next_step,
                    "approvals": approvals
                }}
            )
            
            # Notify next approvers
            approval_request["current_step"] = next_step
            approval_request["approvals"] = approvals
            await ApprovalService._notify_approvers(db, approval_request, chain)
            
            status = "pending"
        
        return {"status": status, "current_step": approval_request["current_step"]}
    
    @staticmethod
    async def reject(
        db: AsyncIOMotorDatabase,
        approval_id: str,
        approver_id: str,
        notes: Optional[str] = None
    ):
        """Reject approval"""
        
        approval_request = await db.approval_requests.find_one({"id": approval_id})
        if not approval_request:
            raise ValueError("Approval request not found")
        
        # Record rejection
        rejection_entry = {
            "step": approval_request["current_step"],
            "approver_id": approver_id,
            "status": "rejected",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "notes": notes
        }
        
        approvals = approval_request.get("approvals", [])
        approvals.append(rejection_entry)
        
        await db.approval_requests.update_one(
            {"id": approval_id},
            {"$set": {
                "status": "rejected",
                "approvals": approvals
            }}
        )
        
        # Update document state to cancelled
        collection_map = {
            "purchase_order": "purchase_orders",
            "payroll": "payroll",
            "inventory_adjustment": "adjustments"
        }
        
        collection_name = collection_map.get(approval_request["document_type"])
        if collection_name:
            await db[collection_name].update_one(
                {"id": approval_request["document_id"]},
                {"$set": {"state": "cancelled"}}
            )
    
    @staticmethod
    async def _finalize_approval(db: AsyncIOMotorDatabase, approval_request: Dict):
        """Finalize document after all approvals"""
        
        collection_map = {
            "purchase_order": "purchase_orders",
            "payroll": "payroll",
            "inventory_adjustment": "adjustments"
        }
        
        collection_name = collection_map.get(approval_request["document_type"])
        if collection_name:
            await db[collection_name].update_one(
                {"id": approval_request["document_id"]},
                {"$set": {"state": "approved"}}
            )
