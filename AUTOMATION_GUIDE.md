# Automation & Workflow System - Complete Implementation Guide

## Overview
Complete automation system with scheduled jobs, multi-level approvals, intelligent notifications, and AI-powered insights.

## 1. SCHEDULED JOBS

### Daily Jobs

#### 1.1 KPI Sync (Midnight)
**Schedule:** Daily at 00:00
**Function:** `KPIService.generate_daily_kpi()`
**Purpose:** Capture daily snapshots of key metrics

**Metrics Captured:**
- Production: Orders created, completed, in-progress
- Inventory: Stock levels, low stock items, total value
- Quality: QC checks performed, pass rate
- Finance: Revenue, costs (when implemented)
- HR: Attendance, headcount

**Storage:** `kpi_snapshots` collection

**Example KPI Record:**
```json
{
  "date": "2025-01-15",
  "kpi_type": "daily",
  "metrics": {
    "production": {
      "total_orders": 45,
      "completed_orders": 38,
      "completion_rate": 84.4
    },
    "inventory": {
      "total_stock_value": 150000,
      "low_stock_items": 5
    },
    "quality": {
      "total_checks": 120,
      "passed_checks": 115,
      "quality_rate": 95.8
    }
  }
}
```

### Hourly Jobs

#### 1.2 Low Stock Monitoring
**Schedule:** Every hour
**Function:** `NotificationService.check_low_stock()`
**Triggers When:** Stock quantity < threshold (default: 10)
**Notifies:** Inventory Officers
**Channel:** In-app notification

#### 1.3 Pending Approval Reminders
**Schedule:** 9 AM and 2 PM daily
**Function:** `NotificationService.check_pending_approvals()`
**Notifies:** Users with approval permission for pending items
**Channel:** Email

#### 1.4 Production Delay Alerts
**Schedule:** 8 AM daily
**Function:** `NotificationService.check_production_delays()`
**Triggers When:** Production order past planned end date
**Notifies:** Production Managers
**Channel:** Email

### Weekly Jobs

#### 1.5 AI-Powered Summary Email
**Schedule:** Monday at 8 AM
**Function:** `AISummaryService.generate_weekly_summary()`
**Purpose:** Executive summary with insights

**Process:**
1. Gather KPI data from past 7 days
2. Compile production, quality, inventory metrics
3. Generate AI summary using Claude (via Emergent LLM key)
4. Email to Admin and CEO/Viewer roles

**AI Prompt Structure:**
```
Generate a concise weekly business summary based on:
- Production metrics (orders, completion rate)
- Inventory levels and movements
- Quality performance
- Key highlights (3-5 points)
- Areas of concern
- Recommendations

Keep under 200 words for executive email.
```

**Recipients:** Admin, CEO/Viewer

### Monthly Jobs

#### 1.6 Payroll Due Reminder
**Schedule:** 25th of each month at 9 AM
**Function:** `NotificationService.check_payroll_due()`
**Notifies:** HR Officer, Admin
**Message:** "Monthly payroll processing is due"

#### 1.7 Month-End Closing
**Schedule:** Last day of month at 11 PM
**Function:** `MonthEndService.run_month_end_close()`

**Process:**
1. **Auto-close completed production orders**
   - Find orders with actual_end date and state=approved
   - Change state to posted
   - Lock records from editing

2. **Run costing updates**
   - Recalculate moving average costs
   - Update FIFO layers
   - Generate variance reports

3. **Generate month-end reports**
   - P&L statement
   - Inventory valuation
   - Production summary
   - Payroll summary

### Quarterly Jobs

#### 1.8 Data Archival
**Schedule:** 1st day of quarter (Jan 1, Apr 1, Jul 1, Oct 1) at midnight
**Function:** `MonthEndService.quarterly_archive()`

**Archives:**
- Read notifications older than 90 days
- Completed production orders older than 90 days
- Posted payroll records older than 90 days

**Process:**
1. Move records to archive collections
2. Delete from main collections
3. Maintain referential integrity
4. Log archive summary

### Daily Maintenance

#### 1.9 Maintenance Due Alerts
**Schedule:** 7 AM daily
**Function:** `NotificationService.check_maintenance_due()`
**Checks:** `maintenance_schedules` for next_due <= today
**Notifies:** Responsible person for each asset
**Channel:** In-app

---

## 2. NOTIFICATION SYSTEM

### Notification Types

1. **LOW_STOCK** - Inventory below threshold
2. **PO_PENDING** - Purchase order awaiting approval
3. **PRODUCTION_DELAY** - Production behind schedule
4. **PAYROLL_DUE** - Payroll processing reminder
5. **MAINTENANCE_DUE** - Equipment maintenance due
6. **APPROVAL_REQUEST** - Action required for approval
7. **APPROVAL_APPROVED** - Document approved
8. **APPROVAL_REJECTED** - Document rejected
9. **SYSTEM_ALERT** - General system notifications

### Notification Channels

1. **In-App:** Stored in database, shown in UI notification center
2. **Email:** Sent via SMTP (configure in .env)
3. **SMS:** Sent via Twilio (already configured)

### Notification Storage

**Collection:** `notifications`

**Schema:**
```json
{
  "id": "notif_uuid",
  "type": "low_stock",
  "channel": "in_app",
  "recipient_id": "user_id",
  "recipient_email": "user@example.com",
  "title": "Low Stock Alert",
  "message": "Product ABC is running low. Current: 5",
  "data": {"product_id": "PROD123", "quantity": 5},
  "is_read": false,
  "sent_at": "2025-01-15T10:30:00Z",
  "created_at": "2025-01-15T10:30:00Z"
}
```

### Email Configuration

Add to `/app/backend/.env`:
```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMERGENT_LLM_KEY=your-emergent-key  # For AI summaries
```

---

## 3. APPROVAL CHAINS

### Pre-defined Chains

#### 3.1 Purchase Order Approval
**Flow:** PO → Supervisor → Accountant → Admin

```
Step 1: Production Manager (Supervisor)
  ↓ (approved)
Step 2: Accountant
  ↓ (approved)
Step 3: Admin (Final approval)
  ↓ (approved)
PO State: draft → approved → ready to post
```

#### 3.2 Payroll Approval
**Flow:** Payroll → HR → Accountant → CEO

```
Step 1: HR Officer
  ↓ (approved)
Step 2: Accountant
  ↓ (approved)
Step 3: CEO/Viewer (Final sign-off)
  ↓ (approved)
Payroll State: draft → approved → ready to process
```

#### 3.3 Inventory Adjustment Approval
**Flow:** Adjustment → Officer → Admin

```
Step 1: Inventory Officer
  ↓ (approved)
Step 2: Admin (Final approval)
  ↓ (approved)
Adjustment State: draft → approved → posted
```

### Approval Process

#### Create Approval Request
```python
approval = await ApprovalService.create_approval_request(
    db=db,
    document_type="purchase_order",
    document_id=po_id,
    requested_by=current_user.id
)
```

#### Approve
```python
result = await ApprovalService.approve(
    db=db,
    approval_id=approval_id,
    approver_id=current_user.id,
    notes="Approved - budget available"
)
```

#### Reject
```python
await ApprovalService.reject(
    db=db,
    approval_id=approval_id,
    approver_id=current_user.id,
    notes="Exceeds budget limits"
)
```

### Approval Rules

1. **Sequential:** Must approve in order (Step 1 before Step 2)
2. **Role-Based:** Only users with specific role can approve each step
3. **One Approval per Step:** Any user with the role can approve
4. **Rejection:** Any approver can reject, ending the chain
5. **Notifications:** Email sent to all users with approval role at each step

### API Endpoints

```
POST /api/approvals/request - Create approval request
POST /api/approvals/{id}/approve - Approve at current step
POST /api/approvals/{id}/reject - Reject approval
GET /api/approvals/pending - Get pending approvals for current user
GET /api/approvals/{id} - Get approval details with history
GET /api/approvals/{id}/history - Get approval chain history
```

---

## 4. AI SUMMARY GENERATION

### Weekly Summary

**Features:**
- Analyzes past week's KPI data
- Uses Claude AI (via Emergent LLM key)
- Generates executive-friendly summary
- Sent via email on Monday mornings

**Data Sources:**
- Daily KPI snapshots
- Production order completions
- Quality check results
- Inventory movements
- HR attendance (when implemented)

**Output Format:**
```
WEEKLY BUSINESS SUMMARY
Period: Jan 8-14, 2025

KEY HIGHLIGHTS:
• Production up 15% from previous week (45 orders completed)
• Quality pass rate maintained at 95.8%
• 5 products flagged for low stock - reorder initiated

AREAS OF CONCERN:
• 3 production orders delayed beyond planned dates
• Material costs increased 8% due to supplier price changes

RECOMMENDATIONS:
• Review production scheduling for delayed orders
• Consider alternative suppliers for high-cost materials
• Increase safety stock for fast-moving items

[Generated by AI on Monday, Jan 15, 2025 at 8:00 AM]
```

### Custom AI Queries

Can be extended to support:
- Custom date range summaries
- Specific department reports
- Variance analysis explanations
- Predictive insights

---

## 5. MONTH-END AUTOMATION

### Automatic Closing

**Production Orders:**
```python
# Find completed orders still in "approved" state
completed_pos = await db.production_orders.find({
    "state": "approved",
    "actual_end": {"$ne": None}
}).to_list(1000)

# Change to "posted" (locked)
for po in completed_pos:
    await db.production_orders.update_one(
        {"id": po["id"]},
        {"$set": {"state": "posted"}}
    )
```

**Work Orders:**
- Close associated work orders
- Finalize labor costs
- Update work center utilization

**Inventory:**
- Run physical count reconciliation
- Post pending adjustments
- Calculate inventory valuation

### Costing Updates

1. **FIFO Reconciliation:** Verify FIFO layers match physical inventory
2. **Moving Average Update:** Recalculate all product costs
3. **WIP to Finished Goods:** Transfer completed production costs
4. **Variance Analysis:** Generate material, labor, overhead variances

### Report Generation

Auto-generated reports:
- Inventory Valuation Report
- Production Performance Summary
- Quality Metrics Dashboard
- Payroll Summary
- Cost Variance Analysis

---

## 6. IMPLEMENTATION STATUS

### ✅ Completed

1. **Data Models**
   - Approval chains, requests, approvals
   - Notifications with multiple channels
   - KPI snapshots
   - AI summaries
   - Scheduled jobs tracking

2. **Services**
   - `ApprovalService` - Complete workflow engine
   - `NotificationService` - Multi-channel notifications
   - `KPIService` - Daily metric capture
   - `AISummaryService` - AI-powered insights
   - `MonthEndService` - Automated closing

3. **Scheduler**
   - APScheduler integration
   - All 9 scheduled jobs configured
   - Cron triggers set up

4. **Documentation**
   - Complete API specifications
   - Process flows
   - Configuration guide

### 📋 Requires Integration

1. **API Endpoints** - Add to server.py:
   ```python
   from models_automation import *
   from scheduler import init_scheduler, scheduler
   from approval_service import ApprovalService
   
   # Initialize approval chains
   @app.on_event("startup")
   async def startup():
       await ApprovalService.initialize_chains(db)
       init_scheduler(db)
   
   # Approval endpoints
   @api_router.post("/approvals/request")
   async def create_approval_request(...)
   
   @api_router.post("/approvals/{id}/approve")
   async def approve_request(...)
   
   # Notification endpoints
   @api_router.get("/notifications")
   async def get_notifications(...)
   
   @api_router.patch("/notifications/{id}/read")
   async def mark_notification_read(...)
   ```

2. **Frontend Pages:**
   - Notification Center component
   - Approval Queue page
   - Approval History page
   - KPI Dashboard
   - AI Summary viewer

3. **Environment Variables:**
   ```bash
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your-email@example.com
   SMTP_PASSWORD=your-app-password
   EMERGENT_LLM_KEY=your-emergent-llm-key
   ```

---

## 7. TESTING

### Test Scheduler Jobs Manually

```python
# In Python console or test file
from scheduler import KPIService, NotificationService
import asyncio

# Test KPI generation
asyncio.run(KPIService.generate_daily_kpi(db))

# Test notifications
asyncio.run(NotificationService.check_low_stock(db))
```

### Test Approval Flow

```python
# Create approval request
approval = await ApprovalService.create_approval_request(
    db, "purchase_order", "PO001", "user_id_1"
)

# Approve as first approver (Production Manager)
await ApprovalService.approve(db, approval["id"], "manager_user_id")

# Approve as second approver (Accountant)
await ApprovalService.approve(db, approval["id"], "accountant_user_id")

# Approve as final approver (Admin)
result = await ApprovalService.approve(db, approval["id"], "admin_user_id")
# result["status"] should be "approved"
```

### Test Notifications

```python
# Manually trigger notification check
await NotificationService.check_low_stock(db)

# Check notifications in database
notifications = await db.notifications.find({"recipient_id": "test_user_id"}).to_list(10)
```

---

## 8. DEPLOYMENT NOTES

1. **Scheduler Start:** Ensure scheduler is started when app starts
2. **Database Indexes:** Add indexes on commonly queried fields
3. **Email Credentials:** Configure SMTP settings
4. **AI Key:** Add Emergent LLM key for AI summaries
5. **Timezone:** Server should use UTC, convert for display
6. **Logging:** Monitor scheduler logs for job execution
7. **Error Handling:** Failed jobs should retry (configure in scheduler)

---

## 9. MONITORING

### Scheduled Job Status

```python
# Check next run times
jobs = scheduler.get_jobs()
for job in jobs:
    print(f"{job.id}: next run at {job.next_run_time}")
```

### Notification Delivery Status

```sql
-- Check notification delivery rates
SELECT type, channel, COUNT(*) as count,
       SUM(CASE WHEN sent_at IS NOT NULL THEN 1 ELSE 0 END) as sent
FROM notifications
WHERE created_at > DATE_SUB(NOW(), INTERVAL 7 DAY)
GROUP BY type, channel
```

### Approval Metrics

```sql
-- Average approval time by document type
SELECT document_type,
       AVG(TIMESTAMPDIFF(HOUR, requested_at, 
           (SELECT MAX(timestamp) FROM approvals WHERE approval_id = id))) as avg_hours
FROM approval_requests
WHERE status = 'approved'
GROUP BY document_type
```

---

## 10. FUTURE ENHANCEMENTS

1. **Predictive Alerts:** ML models for stock prediction
2. **Smart Scheduling:** AI-optimized production scheduling
3. **Voice Notifications:** Integration with phone systems
4. **Mobile App:** Push notifications
5. **Slack/Teams Integration:** Approval requests in chat
6. **Custom Workflows:** User-configurable approval chains
7. **Escalation Rules:** Auto-escalate after timeout
8. **Delegation:** Approve on behalf of others
9. **Bulk Approvals:** Approve multiple items at once
10. **Analytics Dashboard:** Approval bottleneck analysis

---

## Summary

**All 9 scheduled jobs + Approval chains + Notifications + AI summaries are architecturally complete.**

**Ready for:**
- API endpoint integration
- Frontend UI development
- Production deployment

**Total Collections Added:** 5
- notifications
- approval_chains
- approval_requests
- kpi_snapshots
- ai_summaries

**Total Services:** 5
- NotificationService
- KPIService  
- AISummaryService
- MonthEndService
- ApprovalService
