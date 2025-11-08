from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid
from enum import Enum


# Approval Models
class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class ApprovalChain(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_type: str  # purchase_order, payroll, inventory_adjustment
    chain_steps: List[Dict[str, Any]]  # [{role, order, required}]
    is_active: bool = True
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ApprovalChainCreate(BaseModel):
    document_type: str
    chain_steps: List[Dict[str, Any]]


class ApprovalRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_type: str
    document_id: str
    chain_id: str
    current_step: int = 0
    status: ApprovalStatus = ApprovalStatus.PENDING
    approvals: List[Dict[str, Any]] = []  # [{step, approver_id, status, timestamp, notes}]
    requested_by: str
    requested_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ApprovalRequestCreate(BaseModel):
    document_type: str
    document_id: str
    chain_id: str
    requested_by: str


class ApprovalAction(BaseModel):
    status: ApprovalStatus
    notes: Optional[str] = None


# Notification Models
class NotificationType(str, Enum):
    LOW_STOCK = "low_stock"
    PO_PENDING = "po_pending"
    PRODUCTION_DELAY = "production_delay"
    PAYROLL_DUE = "payroll_due"
    MAINTENANCE_DUE = "maintenance_due"
    APPROVAL_REQUEST = "approval_request"
    APPROVAL_APPROVED = "approval_approved"
    APPROVAL_REJECTED = "approval_rejected"
    SYSTEM_ALERT = "system_alert"


class NotificationChannel(str, Enum):
    IN_APP = "in_app"
    EMAIL = "email"
    SMS = "sms"


class Notification(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: NotificationType
    channel: NotificationChannel
    recipient_id: str
    recipient_email: Optional[str] = None
    recipient_phone: Optional[str] = None
    title: str
    message: str
    data: Optional[Dict[str, Any]] = None
    is_read: bool = False
    sent_at: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class NotificationCreate(BaseModel):
    type: NotificationType
    channel: NotificationChannel
    recipient_id: str
    recipient_email: Optional[str] = None
    recipient_phone: Optional[str] = None
    title: str
    message: str
    data: Optional[Dict[str, Any]] = None


# KPI Models
class KPISnapshot(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    date: str  # YYYY-MM-DD
    kpi_type: str  # production, inventory, quality, finance, hr
    metrics: Dict[str, Any]
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# Scheduled Job Models
class ScheduledJob(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    job_name: str
    job_type: str  # daily_kpi, weekly_summary, month_end, quarterly_archive
    schedule: str  # cron expression
    last_run: Optional[str] = None
    next_run: Optional[str] = None
    is_active: bool = True
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# AI Summary Models
class AISummary(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    summary_type: str  # weekly, monthly, custom
    period_start: str
    period_end: str
    content: str
    metrics_used: List[str] = []
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# Purchase Order Models (for approval chain)
class PurchaseOrder(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    po_number: str
    supplier_id: str
    items: List[Dict[str, Any]]
    total_amount: float
    currency: str = "USD"
    state: str = "draft"  # draft, pending_approval, approved, posted, cancelled
    approval_request_id: Optional[str] = None
    requested_by: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class PurchaseOrderCreate(BaseModel):
    po_number: str
    supplier_id: str
    items: List[Dict[str, Any]]
    total_amount: float
    currency: str = "USD"
    requested_by: str


# Maintenance Models
class MaintenanceSchedule(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    asset_id: str  # work_center_id or machine_id
    asset_name: str
    maintenance_type: str  # preventive, corrective
    frequency_days: int
    last_maintenance: Optional[str] = None
    next_due: str
    responsible_person: Optional[str] = None
    is_active: bool = True
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class MaintenanceScheduleCreate(BaseModel):
    asset_id: str
    asset_name: str
    maintenance_type: str
    frequency_days: int
    last_maintenance: Optional[str] = None
    responsible_person: Optional[str] = None
