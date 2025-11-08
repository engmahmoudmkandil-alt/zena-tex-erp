# Advanced Manufacturing ERP - Implementation Guide

## Overview
This document outlines the complete implementation of 16 advanced manufacturing features covering Production, Quality, HR, and Finance.

## Features Implemented

### 1. PRODUCTION & COSTING (6 Features)

#### 1.1 MRP-lite Planning
**Collections:** `mrp_runs`, `mrp_requirements`
**Key Features:**
- Demand analysis from sales orders and production orders
- BOM explosion for material requirements
- Inventory availability checking
- Purchase/production suggestions
- Due date calculations

**API Endpoints:**
```
POST /api/mrp/run - Execute MRP run
GET /api/mrp/requirements - Get material requirements
GET /api/mrp/suggestions - Get purchase/production suggestions
```

**Logic:**
1. Gather all production orders in draft/approved state
2. Explode BOMs to get material requirements
3. Check current inventory levels
4. Calculate shortage = required - available
5. Generate suggestions (buy from supplier or produce internally)

#### 1.2 Backflush Consumption
**Collections:** `backflush_records`
**Service:** `BackflushService` in `services_advanced.py`

**Key Features:**
- Automatic material consumption based on BOM
- Scrap variance tracking
- Actual vs planned comparison
- Integrated with costing

**API Endpoints:**
```
POST /api/production-orders/{id}/backflush - Trigger backflush
GET /api/backflush-records - View backflush history
```

**Flow:**
1. Production order completed
2. Enter actual quantity produced
3. System calculates material consumption: component_qty = bom_qty_per_unit × actual_produced
4. Issue materials from inventory
5. Record scrap variance if any
6. Update WIP costs

#### 1.3 FIFO & Moving Average Costing
**Collections:** `product_costing`, `costing_transactions`
**Service:** `CostingService` in `services_advanced.py`

**Methods:**
- **FIFO:** Tracks inventory layers with purchase cost, consumes oldest first
- **Moving Average:** Recalculates average cost on every receipt

**Formulas:**
```python
# Moving Average
New Average = (Old Value + Receipt Value) / (Old Qty + Receipt Qty)

# FIFO
Issue Cost = Sum of (layer_qty × layer_cost) for oldest layers
```

**APIs:**
```
GET /api/costing/{product_id}/{warehouse_id} - Get current costing
GET /api/costing/transactions - View costing history
POST /api/costing/method - Change costing method
```

#### 1.4 WIP Tracking
**Collections:** `wip_transactions`, `production_orders.wip_cost`
**Service:** `WIPService` in `services_advanced.py`

**Cost Categories:**
- Material costs (from backflush)
- Labor costs (from work orders)
- Overhead costs (allocated)

**APIs:**
```
POST /api/wip/add - Add WIP cost
GET /api/wip/{production_order_id} - Get WIP details
POST /api/production-orders/{id}/close - Close and move to FG
```

**Flow:**
1. Materials issued → Add to WIP as material cost
2. Labor hours recorded → Add to WIP as labor cost
3. Overhead allocated → Add to WIP as overhead
4. Production completed → Move WIP to Finished Goods inventory

#### 1.5 Lot/Batch Traceability
**Collections:** `lot_batches`
**Features:**
- Unique lot numbers for production batches
- Supplier lot tracking for raw materials
- Expiry date management
- Full traceability chain

**APIs:**
```
POST /api/lots - Create lot
GET /api/lots/{lot_number}/trace - Full traceability
GET /api/lots/expiring - Get expiring lots
```

**Traceability Chain:**
```
Supplier Lot → Raw Material Receipt → Production Order → Finished Goods Lot → Sales Order → Customer
```

#### 1.6 Prevent Negative Stock
**Implementation:** In `CostingService` and all inventory transactions

**Rules:**
```python
if new_quantity < 0:
    raise ValueError("Insufficient inventory (negative stock prevented)")
```

**Applied to:**
- Stock issues
- Production consumption
- Sales orders
- Transfer out

### 2. QUALITY MANAGEMENT (4 Features)

#### 2.1 QC Gates + COQ Metrics
**Collections:** `quality_checks`, `coq_records`

**QC Gates:**
- **Receiving Inspection:** On material receipt from suppliers
- **In-Process Inspection:** During production at work centers
- **Final Inspection:** Before finished goods acceptance

**COQ Categories:**
- Prevention costs (training, quality planning)
- Appraisal costs (inspections, testing)
- Internal failure costs (scrap, rework)
- External failure costs (returns, warranty)

**APIs:**
```
POST /api/quality/check - Create QC record
GET /api/quality/checks - List all QC checks
GET /api/coq/summary - COQ dashboard
POST /api/coq/record - Add COQ cost
```

#### 2.2 Spec Tolerance Checks
**Collections:** `quality_specs`

**Features:**
- Define target value and tolerance range for each parameter
- Automatic pass/fail based on measurements
- Statistical process control ready

**Example:**
```json
{
  "product_id": "PROD001",
  "parameter_name": "Weight",
  "target_value": 100,
  "lower_tolerance": 98,
  "upper_tolerance": 102,
  "unit": "grams"
}
```

**APIs:**
```
POST /api/quality/specs - Create specification
GET /api/quality/specs/{product_id} - Get product specs
POST /api/quality/validate - Validate measurements against specs
```

#### 2.3 GSM & Embroidery Validation
**Special QC Parameters for Textile/Garment Manufacturing:**

**GSM (Grams per Square Meter):**
- Critical for fabric quality
- Tolerance: ±5% typically
- Measured at multiple points

**Embroidery Quality:**
- Stitch count validation
- Thread tension checks
- Design alignment
- Color matching

**Implementation:**
```json
{
  "product_id": "FABRIC001",
  "checks": [
    {"parameter": "GSM", "target": 180, "tolerance": 9},
    {"parameter": "Stitch Count", "target": 1000, "tolerance": 50},
    {"parameter": "Thread Tension", "target": 5, "tolerance": 0.5}
  ]
}
```

### 3. HR & PAYROLL (3 Features)

#### 3.1 Attendance Rules
**Collections:** `attendance`, `shifts`

**Features:**
- Multiple shifts support
- Automatic late calculation
- Overtime tracking (hours beyond shift)
- Half-day marking
- Leave integration

**Rules Engine:**
```python
if check_in > shift_start + grace_period:
    mark_late()

if (check_out - check_in) > shift_hours:
    overtime = (check_out - check_in) - shift_hours
```

**APIs:**
```
POST /api/attendance - Mark attendance
GET /api/attendance/{employee_id} - Get attendance history
POST /api/attendance/bulk - Bulk upload
GET /api/attendance/summary - Monthly summary
```

#### 3.2 Shift Planner
**Collections:** `shifts`, `shift_assignments`

**Features:**
- Multiple shift definitions (Morning, Evening, Night)
- Rotating shift schedules
- Shift-wise attendance tracking
- Capacity planning

**Shift Example:**
```json
{
  "shift_code": "MORNING",
  "shift_name": "Morning Shift",
  "start_time": "08:00",
  "end_time": "16:00",
  "is_active": true
}
```

**APIs:**
```
POST /api/shifts - Create shift
GET /api/shifts - List shifts
POST /api/shifts/assign - Assign employee to shift
GET /api/shifts/roster - Get shift roster
```

#### 3.3 Payroll Formula Engine
**Collections:** `payroll_formulas`, `payroll`
**Service:** `PayrollService` in `services_advanced.py`

**Formula Variables:**
- basic_salary
- present_days
- working_days
- overtime_hours
- allowances
- deductions

**Example Formulas:**
```python
# Simple proportional
"(basic_salary / working_days) * present_days"

# With overtime
"basic_salary + (overtime_hours * hourly_rate)"

# Complex with allowances
"basic_salary + allowances + (overtime_hours * 50) - deductions"
```

**APIs:**
```
POST /api/payroll/formulas - Create formula
GET /api/payroll/formulas - List formulas
POST /api/payroll/calculate - Calculate payroll
GET /api/payroll/{employee_id} - Get payroll history
POST /api/payroll/approve - Approve payroll
```

**Safety:**
- Formula execution in sandboxed environment
- Only whitelisted variables allowed
- No file system or network access

### 4. WORKFLOW & FINANCE (3 Features)

#### 4.1 Document States (Draft→Approved→Posted)
**Applied to:** Production Orders, Work Orders, Attendance, Leave, Payroll, Purchase Orders, Sales Orders

**State Machine:**
```
DRAFT → APPROVED → POSTED → CANCELLED
         ↑____________↓
```

**Rules:**
- Draft: Editable, not affecting inventory/costs
- Approved: Locked for editing, awaiting execution
- Posted: Executed, affects inventory/GL
- Cancelled: Voided, no effect

**APIs:**
```
POST /api/{entity}/{id}/approve - Approve document
POST /api/{entity}/{id}/post - Post document
POST /api/{entity}/{id}/cancel - Cancel document
GET /api/{entity}/{id}/history - State change history
```

**Implementation:**
```python
@api_router.post("/{entity}/{id}/approve")
async def approve_document(entity: str, id: str):
    if entity not in ALLOWED_ENTITIES:
        raise HTTPException(400)
    
    doc = await db[entity].find_one({"id": id})
    if doc["state"] != "draft":
        raise HTTPException(400, "Can only approve draft documents")
    
    await db[entity].update_one(
        {"id": id},
        {"$set": {"state": "approved", "approved_at": now()}}
    )
```

#### 4.2 Dual-Currency Reports
**Collections:** `currencies`, `exchange_rates`

**Features:**
- Multiple currency support
- Base currency setting
- Automatic conversion
- Historical rate tracking
- Gain/loss on exchange

**Example:**
```json
{
  "base_currency": "USD",
  "transaction_currency": "AED",
  "exchange_rate": 3.67,
  "amount_transaction": 1000,
  "amount_base": 272.48
}
```

**APIs:**
```
POST /api/currencies - Add currency
GET /api/currencies/rates - Get exchange rates
POST /api/currencies/rates - Update rates
GET /api/reports/{report_name}?currency=AED - Get report in currency
```

**Conversion Logic:**
```python
amount_in_base = amount_in_transaction / exchange_rate
amount_in_target = amount_in_base * target_exchange_rate
```

#### 4.3 Variance Analysis (Material, Labor, Overhead)
**Collections:** `variance_analysis`

**Types:**
1. **Material Variance**
   - Standard cost vs actual cost
   - Quantity variance (actual qty vs standard qty)
   - Price variance (actual price vs standard price)

2. **Labor Variance**
   - Efficiency variance (actual hours vs standard hours)
   - Rate variance (actual rate vs standard rate)

3. **Overhead Variance**
   - Volume variance
   - Spending variance

**Formulas:**
```python
# Material
material_variance = (actual_qty × actual_price) - (standard_qty × standard_price)
price_variance = (actual_price - standard_price) × actual_qty
quantity_variance = (actual_qty - standard_qty) × standard_price

# Labor
labor_variance = (actual_hours × actual_rate) - (standard_hours × standard_rate)
efficiency_variance = (actual_hours - standard_hours) × standard_rate
rate_variance = (actual_rate - standard_rate) × actual_hours

# Overhead
overhead_variance = actual_overhead - (standard_rate × actual_output)
```

**APIs:**
```
GET /api/variance/{production_order_id} - Get variance analysis
GET /api/variance/summary - Variance dashboard
POST /api/variance/analyze - Trigger variance calculation
```

**Report Structure:**
```json
{
  "production_order_id": "PO001",
  "variances": [
    {
      "type": "material",
      "component": "Steel Plate",
      "standard_cost": 1000,
      "actual_cost": 1100,
      "variance": 100,
      "variance_percentage": 10,
      "favorable": false
    },
    {
      "type": "labor",
      "work_center": "Assembly",
      "standard_cost": 500,
      "actual_cost": 450,
      "variance": -50,
      "variance_percentage": -10,
      "favorable": true
    }
  ],
  "total_variance": 50
}
```

## Database Collections Summary

**Total Collections: 30+**

1. products
2. boms
3. work_centers
4. employees
5. suppliers
6. customers
7. warehouses
8. bins
9. inventory_items
10. stock_moves
11. adjustments
12. production_orders
13. work_orders
14. lot_batches
15. product_costing
16. costing_transactions
17. wip_transactions
18. backflush_records
19. quality_checks
20. quality_specs
21. coq_records
22. attendance
23. shifts
24. leaves
25. payroll_formulas
26. payroll
27. currencies
28. mrp_runs
29. mrp_requirements
30. variance_analysis

## Implementation Priority

### Phase 1 (Already Done):
✅ Authentication & Authorization
✅ Masters (Products, BOMs, Work Centers, Employees, Suppliers, Customers)
✅ Inventory Management
✅ Multilingual Support

### Phase 2 (Core Manufacturing):
1. Production Orders & Work Orders
2. Backflush Consumption
3. FIFO/Moving Average Costing
4. WIP Tracking
5. Document States (Draft→Approved→Posted)

### Phase 3 (Quality & Compliance):
1. QC Gates & Quality Checks
2. Spec Tolerance Validation
3. GSM & Embroidery Checks
4. COQ Tracking

### Phase 4 (HR & Payroll):
1. Attendance & Shifts
2. Leave Management
3. Payroll Formula Engine
4. Payroll Processing

### Phase 5 (Advanced):
1. MRP Planning
2. Lot Traceability
3. Variance Analysis
4. Dual-Currency
5. Reports & Dashboards

## Technical Architecture

### Backend Stack:
- FastAPI
- MongoDB (30+ collections)
- Pydantic models
- Service layer for business logic
- Async/await for performance

### Frontend Stack:
- React 18
- i18next (multilingual)
- Tailwind CSS
- Shadcn/UI components
- React Router
- Axios for API calls

### Key Services:
- `CostingService` - FIFO/MA costing
- `BackflushService` - Material consumption
- `WIPService` - Production costing
- `PayrollService` - Salary calculation
- `QualityService` - QC validation
- `VarianceService` - Cost analysis

### Security:
- JWT session management
- RBAC (Role-Based Access Control)
- Audit logging
- State-based document control

## Testing Strategy

1. Unit tests for costing algorithms
2. Integration tests for workflows
3. E2E tests for key processes
4. Performance tests for MRP runs
5. Security tests for RBAC

## Performance Considerations

1. **Indexing:**
   - product_id, warehouse_id on costing tables
   - employee_id, date on attendance
   - production_order_id on WIP transactions

2. **Caching:**
   - Currency exchange rates
   - Active BOMs
   - Employee shifts

3. **Batch Processing:**
   - MRP runs (async)
   - Payroll calculation (bulk)
   - Variance analysis (scheduled)

## Deployment Notes

1. MongoDB indexes need to be created
2. Initial currency setup required
3. Default shifts configuration
4. Base payroll formulas
5. Quality specs for products

## Next Steps

To proceed with full implementation:
1. Choose which phase to implement next
2. Test and validate Phase 2 features
3. Build frontend for production workflows
4. Create reports and dashboards
5. Integrate with external systems (if any)
