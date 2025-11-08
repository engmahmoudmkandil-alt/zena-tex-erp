from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid
from enum import Enum


# Enums
class DocumentState(str, Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    POSTED = "posted"
    CANCELLED = "cancelled"


class CostingMethod(str, Enum):
    FIFO = "fifo"
    MOVING_AVERAGE = "moving_average"


class QCStatus(str, Enum):
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    HOLD = "hold"


class AttendanceStatus(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    HALF_DAY = "half_day"
    LEAVE = "leave"
    HOLIDAY = "holiday"


# Production Order Models
class ProductionOrder(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    po_number: str
    product_id: str
    bom_id: str
    quantity: float
    planned_start: Optional[str] = None
    planned_end: Optional[str] = None
    actual_start: Optional[str] = None
    actual_end: Optional[str] = None
    state: DocumentState = DocumentState.DRAFT
    wip_cost: float = 0.0
    actual_cost: float = 0.0
    lot_number: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ProductionOrderCreate(BaseModel):
    po_number: str
    product_id: str
    bom_id: str
    quantity: float
    planned_start: Optional[str] = None
    planned_end: Optional[str] = None


# Work Order Models
class WorkOrder(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    wo_number: str
    production_order_id: str
    work_center_id: str
    operation_name: str
    planned_hours: float
    actual_hours: float = 0.0
    state: DocumentState = DocumentState.DRAFT
    qc_status: QCStatus = QCStatus.PENDING
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class WorkOrderCreate(BaseModel):
    wo_number: str
    production_order_id: str
    work_center_id: str
    operation_name: str
    planned_hours: float


# Lot/Batch Tracking
class LotBatch(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    lot_number: str
    product_id: str
    quantity: float
    production_date: Optional[str] = None
    expiry_date: Optional[str] = None
    supplier_id: Optional[str] = None
    production_order_id: Optional[str] = None
    is_active: bool = True
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class LotBatchCreate(BaseModel):
    lot_number: str
    product_id: str
    quantity: float
    production_date: Optional[str] = None
    expiry_date: Optional[str] = None
    supplier_id: Optional[str] = None
    production_order_id: Optional[str] = None


# Costing Models
class CostingTransaction(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_id: str
    warehouse_id: str
    transaction_type: str  # receipt, issue, adjustment
    quantity: float
    unit_cost: float
    total_cost: float
    lot_number: Optional[str] = None
    reference_id: Optional[str] = None
    transaction_date: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ProductCosting(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_id: str
    warehouse_id: str
    costing_method: CostingMethod
    current_average_cost: float = 0.0
    total_quantity: float = 0.0
    total_value: float = 0.0
    fifo_layers: List[Dict[str, Any]] = []  # [{quantity, cost, date, lot}]
    last_updated: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# WIP Tracking
class WIPTransaction(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    production_order_id: str
    transaction_type: str  # material, labor, overhead
    cost_category: str
    amount: float
    quantity: Optional[float] = None
    notes: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# Backflush Consumption
class BackflushRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    production_order_id: str
    work_order_id: Optional[str] = None
    product_id: str
    component_id: str
    planned_quantity: float
    actual_quantity: float
    scrap_quantity: float = 0.0
    variance: float = 0.0
    lot_number: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# Quality Control
class QualityCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    reference_type: str  # production_order, work_order, receipt
    reference_id: str
    product_id: str
    qc_gate: str  # receiving, in-process, final
    inspector_id: str
    inspection_date: str
    status: QCStatus
    defects: List[Dict[str, Any]] = []
    measurements: List[Dict[str, Any]] = []
    notes: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class QualityCheckCreate(BaseModel):
    reference_type: str
    reference_id: str
    product_id: str
    qc_gate: str
    inspector_id: str
    status: QCStatus
    defects: List[Dict[str, Any]] = []
    measurements: List[Dict[str, Any]] = []
    notes: Optional[str] = None


# Quality Specifications
class QualitySpec(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_id: str
    parameter_name: str
    target_value: float
    lower_tolerance: float
    upper_tolerance: float
    unit: str
    is_active: bool = True
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class QualitySpecCreate(BaseModel):
    product_id: str
    parameter_name: str
    target_value: float
    lower_tolerance: float
    upper_tolerance: float
    unit: str


# COQ (Cost of Quality)
class COQRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    category: str  # prevention, appraisal, internal_failure, external_failure
    description: str
    amount: float
    reference_type: Optional[str] = None
    reference_id: Optional[str] = None
    period: str  # YYYY-MM
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class COQRecordCreate(BaseModel):
    category: str
    description: str
    amount: float
    reference_type: Optional[str] = None
    reference_id: Optional[str] = None
    period: str


# Shift Models
class Shift(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    shift_code: str
    shift_name: str
    start_time: str  # HH:MM format
    end_time: str
    is_active: bool = True
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ShiftCreate(BaseModel):
    shift_code: str
    shift_name: str
    start_time: str
    end_time: str


# Attendance Models
class Attendance(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    employee_id: str
    date: str  # YYYY-MM-DD
    shift_id: Optional[str] = None
    check_in: Optional[str] = None
    check_out: Optional[str] = None
    status: AttendanceStatus
    hours_worked: float = 0.0
    overtime_hours: float = 0.0
    notes: Optional[str] = None
    approved_by: Optional[str] = None
    state: DocumentState = DocumentState.DRAFT
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class AttendanceCreate(BaseModel):
    employee_id: str
    date: str
    shift_id: Optional[str] = None
    check_in: Optional[str] = None
    check_out: Optional[str] = None
    status: AttendanceStatus
    hours_worked: float = 0.0
    overtime_hours: float = 0.0
    notes: Optional[str] = None


# Leave Models
class Leave(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    employee_id: str
    leave_type: str  # annual, sick, casual, unpaid
    start_date: str
    end_date: str
    days: float
    reason: Optional[str] = None
    state: DocumentState = DocumentState.DRAFT
    approved_by: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class LeaveCreate(BaseModel):
    employee_id: str
    leave_type: str
    start_date: str
    end_date: str
    days: float
    reason: Optional[str] = None


# Payroll Formula
class PayrollFormula(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    formula_code: str
    formula_name: str
    formula_expression: str  # Python expression
    variables: List[str] = []  # [basic_salary, allowances, deductions, overtime]
    is_active: bool = True
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class PayrollFormulaCreate(BaseModel):
    formula_code: str
    formula_name: str
    formula_expression: str
    variables: List[str] = []


# Payroll Models
class Payroll(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    employee_id: str
    period: str  # YYYY-MM
    basic_salary: float
    allowances: float = 0.0
    overtime_amount: float = 0.0
    deductions: float = 0.0
    gross_salary: float = 0.0
    net_salary: float = 0.0
    working_days: float = 0.0
    present_days: float = 0.0
    state: DocumentState = DocumentState.DRAFT
    formula_id: Optional[str] = None
    approved_by: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class PayrollCreate(BaseModel):
    employee_id: str
    period: str
    basic_salary: float
    allowances: float = 0.0
    overtime_amount: float = 0.0
    deductions: float = 0.0
    working_days: float = 0.0
    present_days: float = 0.0
    formula_id: Optional[str] = None


# Variance Analysis
class VarianceAnalysis(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    production_order_id: str
    variance_type: str  # material, labor, overhead
    standard_cost: float
    actual_cost: float
    variance_amount: float
    variance_percentage: float
    notes: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# Currency Models
class Currency(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    code: str  # USD, EUR, AED, SAR
    name: str
    symbol: str
    exchange_rate: float = 1.0
    is_base: bool = False
    is_active: bool = True
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class CurrencyCreate(BaseModel):
    code: str
    name: str
    symbol: str
    exchange_rate: float = 1.0
    is_base: bool = False


# MRP Planning
class MRPRun(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    run_number: str
    run_date: str
    status: str  # running, completed, failed
    total_orders: int = 0
    total_requirements: int = 0
    notes: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class MRPRequirement(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    mrp_run_id: str
    product_id: str
    required_quantity: float
    available_quantity: float
    shortage_quantity: float
    suggested_action: str  # purchase, produce
    due_date: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
