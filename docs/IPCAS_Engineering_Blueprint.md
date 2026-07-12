# IPCAS — Integrated Project Control Automation System

## Engineering Blueprint (Rev. 2)

> Converted from: طرح اولیه سیستم اتوماسیون یکپارچه کنترل پروژه‌های عمرانی

---

## 1. System Architecture

### 1.1 Architectural Overview

IPCAS is a **multi-tenant, project-scoped SaaS platform** for civil/construction project management. The architecture follows a clean layered model with offline-first edge nodes for field crews.

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                             │
│  Web Dashboard  │  Mobile PWA (offline)  │  Tablet (field)     │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTPS / WebSocket
┌────────────────────────────▼────────────────────────────────────┐
│                        API GATEWAY                              │
│  Auth (JWT/OAuth2)  │  Rate Limiting  │  Request Routing        │
└──┬──────────┬──────────┬──────────┬──────────┬──────────────────┘
   │          │          │          │          │
┌──▼──┐  ┌───▼──┐  ┌────▼──┐  ┌───▼──┐  ┌────▼──────────────────┐
│Core │  │Report│  │Finance│  │Field │  │   Economic Engine      │
│Svc  │  │Svc   │  │Svc    │  │Sync  │  │ (Inflation / Forecast) │
└──┬──┘  └───┬──┘  └────┬──┘  └───┬──┘  └────┬──────────────────┘
   │         │           │         │           │
┌──▼─────────▼───────────▼─────────▼───────────▼─────────────────┐
│                     MESSAGE BUS (Event Streaming)               │
│              daily-report.approved  ·  cost.recorded            │
│              ipc.submitted  ·  schedule.updated                 │
└──────────────────────────────┬──────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│                        DATA LAYER                               │
│  PostgreSQL (relational)  │  Redis (cache/queue)                │
│  S3-compatible (files)    │  TimeSeries DB (KPIs / indices)     │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Service Breakdown


| Service                  | Responsibility                                                                  |
| ------------------------ | ------------------------------------------------------------------------------- |
| **Core Service**         | Projects, WBS, Activities, Users, Roles, Permissions                            |
| **Field Sync Service**   | Daily report ingestion, offline queue, sync reconciliation                      |
| **Finance Service**      | Costs, Budgets, Cash Flow, IPCs, Contracts                                      |
| **Report Service**       | KPI aggregation, dashboards, PDF/Excel export                                   |
| **Economic Engine**      | Inflation adjustment, payment delay analysis, scenario simulation (Monte Carlo) |
| **Notification Service** | Automated alerts, webhook delivery, email/SMS                                   |
| **Document Service**     | File upload, versioning, access control                                         |


### 1.3 Offline-First Field Strategy

Field supervisors (سرپرست کارگاه) often lack reliable internet. The mobile PWA uses:

- **Local IndexedDB** to queue daily report entries offline
- Background sync via Service Worker — pushes when connectivity is restored
- Optimistic UI — form saves locally immediately, syncs silently
- Conflict resolution: server-side timestamp wins; client diff is flagged for supervisor review

---

## 2. Database Schema

The database is organized into **9 domains** (~70 core tables). Below are the definitive table definitions with columns, types, and key constraints.

### Domain 1: Master Data

```sql
-- Users
CREATE TABLE users (
    user_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name       VARCHAR(120) NOT NULL,
    username        VARCHAR(60)  UNIQUE NOT NULL,
    password_hash   TEXT         NOT NULL,
    email           VARCHAR(120),
    mobile          VARCHAR(20),
    organization    VARCHAR(120),
    status          VARCHAR(20)  DEFAULT 'active'
                    CHECK (status IN ('active','inactive','suspended')),
    created_at      TIMESTAMPTZ  DEFAULT now()
);

-- Roles (system-level)
CREATE TABLE roles (
    role_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role_name   VARCHAR(60) UNIQUE NOT NULL,
    description TEXT
);

-- Project-scoped membership (person + project + one-or-more roles)
CREATE TABLE project_members (
    member_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id      UUID NOT NULL REFERENCES projects(project_id),
    user_id         UUID NOT NULL REFERENCES users(user_id),
    status          VARCHAR(20) DEFAULT 'active',
    joined_at       TIMESTAMPTZ DEFAULT now(),
    UNIQUE (project_id, user_id)
);

CREATE TABLE project_member_roles (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    member_id       UUID NOT NULL REFERENCES project_members(member_id),
    role_id         UUID NOT NULL REFERENCES roles(role_id),
    UNIQUE (member_id, role_id)
);

-- Per-project custom positions (سمت) — may be project-scoped or global
CREATE TABLE project_positions (
    position_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id      UUID REFERENCES projects(project_id), -- NULL = global
    position_name   VARCHAR(120) NOT NULL,
    description     TEXT,
    is_active       BOOLEAN DEFAULT true
);

-- Units of measure
CREATE TABLE units (
    unit_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    unit_name   VARCHAR(40) NOT NULL,
    unit_symbol VARCHAR(10)
);
```

### Domain 2: Project & WBS

```sql
CREATE TABLE projects (
    project_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_code        VARCHAR(30) UNIQUE NOT NULL,
    project_name        VARCHAR(200) NOT NULL,
    employer            VARCHAR(120),
    contractor          VARCHAR(120),
    consultant          VARCHAR(120),
    project_manager_id  UUID REFERENCES users(user_id),
    location            TEXT,
    start_date          DATE,
    planned_finish_date DATE,
    contract_amount     NUMERIC(18,2),
    contract_type       VARCHAR(60),
    status              VARCHAR(30) DEFAULT 'active'
                        CHECK (status IN ('active','suspended','completed','handed_over')),
    cut_off_date        DATE,   -- for mid-project onboarding
    created_at          TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE wbs (
    wbs_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id      UUID NOT NULL REFERENCES projects(project_id),
    parent_wbs_id   UUID REFERENCES wbs(wbs_id),
    wbs_code        VARCHAR(30) NOT NULL,
    wbs_name        VARCHAR(200) NOT NULL,
    level           SMALLINT NOT NULL,
    weight_physical NUMERIC(8,4),   -- % of total physical weight
    weight_financial NUMERIC(8,4),
    description     TEXT,
    UNIQUE (project_id, wbs_code)
);

CREATE TABLE activities (
    activity_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id      UUID NOT NULL REFERENCES projects(project_id),
    wbs_id          UUID NOT NULL REFERENCES wbs(wbs_id),
    activity_code   VARCHAR(30) NOT NULL,
    activity_name   VARCHAR(200) NOT NULL,
    unit_id         UUID REFERENCES units(unit_id),
    total_quantity  NUMERIC(18,4),
    weight          NUMERIC(8,4),   -- % physical weight in project
    planned_start   DATE,
    planned_finish  DATE,
    actual_start    DATE,
    actual_finish   DATE,
    responsible_id  UUID REFERENCES users(user_id),
    status          VARCHAR(20) DEFAULT 'not_started'
                    CHECK (status IN ('not_started','in_progress','suspended','completed')),
    UNIQUE (project_id, activity_code)
);

-- Predecessor / successor links (FS, SS, FF, SF)
CREATE TABLE activity_relations (
    relation_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    predecessor_id  UUID NOT NULL REFERENCES activities(activity_id),
    successor_id    UUID NOT NULL REFERENCES activities(activity_id),
    relation_type   VARCHAR(4) CHECK (relation_type IN ('FS','SS','FF','SF')),
    lag_days        INT DEFAULT 0
);
```

### Domain 3: Schedule

```sql
CREATE TABLE baseline_schedules (
    baseline_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id          UUID NOT NULL REFERENCES projects(project_id),
    version_name        VARCHAR(60),
    approved_at         DATE,
    approved_by_id      UUID REFERENCES users(user_id),
    is_current          BOOLEAN DEFAULT false
);

CREATE TABLE baseline_activities (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    baseline_id         UUID NOT NULL REFERENCES baseline_schedules(baseline_id),
    activity_id         UUID NOT NULL REFERENCES activities(activity_id),
    planned_start       DATE,
    planned_finish      DATE,
    planned_duration    INT,        -- calendar days
    planned_quantity    NUMERIC(18,4),
    planned_progress    NUMERIC(6,3), -- % at this snapshot
    total_float         INT,
    free_float          INT,
    is_critical         BOOLEAN DEFAULT false
);

CREATE TABLE activity_progress (
    progress_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    activity_id         UUID NOT NULL REFERENCES activities(activity_id),
    report_date         DATE NOT NULL,
    planned_progress    NUMERIC(6,3),
    actual_progress     NUMERIC(6,3),
    cumulative_quantity NUMERIC(18,4),
    deviation           NUMERIC(6,3) GENERATED ALWAYS AS
                        (actual_progress - planned_progress) STORED,
    updated_by_id       UUID REFERENCES users(user_id),
    UNIQUE (activity_id, report_date)
);
```

### Domain 4: Daily Reports

```sql
CREATE TABLE daily_reports (
    report_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id      UUID NOT NULL REFERENCES projects(project_id),
    report_date     DATE NOT NULL,
    shift           VARCHAR(10) CHECK (shift IN ('day','night','full')),
    weather         VARCHAR(40),
    temperature_min NUMERIC(5,1),
    temperature_max NUMERIC(5,1),
    general_notes   TEXT,
    prepared_by_id  UUID REFERENCES users(user_id),
    approved_by_id  UUID REFERENCES users(user_id),
    status          VARCHAR(20) DEFAULT 'draft'
                    CHECK (status IN ('draft','submitted','approved','rejected')),
    submitted_at    TIMESTAMPTZ,
    approved_at     TIMESTAMPTZ,
    synced_from_offline BOOLEAN DEFAULT false,
    UNIQUE (project_id, report_date, shift)
);

CREATE TABLE daily_activities (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_id           UUID NOT NULL REFERENCES daily_reports(report_id),
    activity_id         UUID NOT NULL REFERENCES activities(activity_id),
    work_front          VARCHAR(120),
    executed_quantity   NUMERIC(18,4),
    notes               TEXT
);

CREATE TABLE daily_labor (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_id       UUID NOT NULL REFERENCES daily_reports(report_id),
    labor_type      VARCHAR(60),      -- engineer, technician, skilled, unskilled
    discipline      VARCHAR(60),      -- civil, mechanical, electrical
    headcount       INT,
    work_hours      NUMERIC(6,2),
    overtime_hours  NUMERIC(6,2),
    daily_rate      NUMERIC(12,2),
    activity_id     UUID REFERENCES activities(activity_id)
);

CREATE TABLE daily_equipment (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_id       UUID NOT NULL REFERENCES daily_reports(report_id),
    equipment_type  VARCHAR(80),
    equipment_code  VARCHAR(30),
    work_hours      NUMERIC(6,2),
    idle_hours      NUMERIC(6,2),
    idle_reason     TEXT,
    operator_id     UUID REFERENCES users(user_id),
    activity_id     UUID REFERENCES activities(activity_id),
    hourly_rate     NUMERIC(12,2),
    fuel_cost       NUMERIC(12,2)
);

CREATE TABLE daily_material_usage (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_id       UUID NOT NULL REFERENCES daily_reports(report_id),
    material_id     UUID NOT NULL REFERENCES materials(material_id),
    quantity_used   NUMERIC(18,4),
    activity_id     UUID REFERENCES activities(activity_id),
    notes           TEXT
);

CREATE TABLE daily_incidents (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_id       UUID NOT NULL REFERENCES daily_reports(report_id),
    incident_type   VARCHAR(40) CHECK (incident_type IN
                    ('safety','quality','environmental','stoppage','visitor')),
    description     TEXT,
    corrective_action TEXT
);
```

### Domain 5: Resources (Materials / Equipment)

```sql
CREATE TABLE materials (
    material_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    material_code   VARCHAR(30) UNIQUE NOT NULL,
    material_name   VARCHAR(120) NOT NULL,
    unit_id         UUID REFERENCES units(unit_id),
    category        VARCHAR(60),
    min_stock_level NUMERIC(18,4)
);

CREATE TABLE inventory_transactions (
    tx_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id      UUID NOT NULL REFERENCES projects(project_id),
    material_id     UUID NOT NULL REFERENCES materials(material_id),
    tx_date         DATE NOT NULL,
    tx_type         VARCHAR(10) CHECK (tx_type IN ('in','out','waste','adjust')),
    quantity        NUMERIC(18,4),
    unit_cost       NUMERIC(14,4),
    supplier_id     UUID REFERENCES suppliers(supplier_id),
    activity_id     UUID REFERENCES activities(activity_id),
    document_ref    VARCHAR(60),
    notes           TEXT
);

CREATE TABLE suppliers (
    supplier_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    supplier_name   VARCHAR(120) NOT NULL,
    contact_info    JSONB
);
```

### Domain 6: Cost Control

```sql
CREATE TABLE budgets (
    budget_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id      UUID NOT NULL REFERENCES projects(project_id),
    activity_id     UUID REFERENCES activities(activity_id),
    wbs_id          UUID REFERENCES wbs(wbs_id),
    cost_category   VARCHAR(40) CHECK (cost_category IN
                    ('labor','material','equipment','subcontract',
                     'site_overhead','hq_overhead','transport','other')),
    budget_amount   NUMERIC(18,2) NOT NULL
);

CREATE TABLE actual_costs (
    cost_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id      UUID NOT NULL REFERENCES projects(project_id),
    activity_id     UUID REFERENCES activities(activity_id),
    wbs_id          UUID REFERENCES wbs(wbs_id),
    cost_date       DATE NOT NULL,
    cost_category   VARCHAR(40),
    amount          NUMERIC(18,2) NOT NULL,
    description     TEXT,
    invoice_number  VARCHAR(60),
    supplier_id     UUID REFERENCES suppliers(supplier_id),
    approved_by_id  UUID REFERENCES users(user_id),
    cost_type       VARCHAR(20) DEFAULT 'direct'
                    CHECK (cost_type IN ('direct','allocated_historical',
                                        'estimated_historical','unallocated')),
    confidence_level VARCHAR(10) CHECK (confidence_level IN ('high','medium','low')),
    allocation_method TEXT,   -- for mid-project onboarding
    cost_pool_id    UUID REFERENCES cost_pools(pool_id)
);

-- For mid-project onboarding: lump-sum historical costs pending allocation
CREATE TABLE cost_pools (
    pool_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id      UUID NOT NULL REFERENCES projects(project_id),
    pool_name       VARCHAR(120),
    cost_category   VARCHAR(40),
    total_amount    NUMERIC(18,2),
    allocated_amount NUMERIC(18,2) DEFAULT 0,
    status          VARCHAR(20) DEFAULT 'unallocated'
                    CHECK (status IN ('unallocated','partially_allocated','fully_allocated')),
    data_source     VARCHAR(60),
    confidence_level VARCHAR(10)
);
```

### Domain 7: Contracts & IPCs

```sql
CREATE TABLE contracts (
    contract_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id          UUID NOT NULL REFERENCES projects(project_id),
    contract_number     VARCHAR(60) UNIQUE,
    contract_type       VARCHAR(40),  -- main, subcontract, purchase, equipment_rental
    counterparty        VARCHAR(120),
    start_date          DATE,
    finish_date         DATE,
    original_amount     NUMERIC(18,2),
    adjusted_amount     NUMERIC(18,2),
    advance_payment_pct NUMERIC(5,2),
    retention_pct       NUMERIC(5,2),
    insurance_pct       NUMERIC(5,2),
    tax_pct             NUMERIC(5,2),
    status              VARCHAR(20) DEFAULT 'active',
    file_url            TEXT
);

CREATE TABLE contract_items (
    item_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contract_id     UUID NOT NULL REFERENCES contracts(contract_id),
    activity_id     UUID REFERENCES activities(activity_id),
    boq_code        VARCHAR(30),
    description     TEXT,
    unit_id         UUID REFERENCES units(unit_id),
    unit_price      NUMERIC(14,4),
    quantity        NUMERIC(18,4)
);

CREATE TABLE ipcs (
    ipc_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id      UUID NOT NULL REFERENCES projects(project_id),
    contract_id     UUID NOT NULL REFERENCES contracts(contract_id),
    ipc_number      INT NOT NULL,
    period_start    DATE,
    period_end      DATE,
    prepared_date   DATE,
    submitted_date  DATE,
    approval_date   DATE,
    planned_payment_date DATE,
    actual_payment_date  DATE,
    gross_amount    NUMERIC(18,2),
    net_amount      NUMERIC(18,2),
    status          VARCHAR(20) DEFAULT 'draft'
                    CHECK (status IN ('draft','submitted','under_review',
                                      'approved','paid')),
    UNIQUE (project_id, contract_id, ipc_number)
);

CREATE TABLE ipc_items (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ipc_id          UUID NOT NULL REFERENCES ipcs(ipc_id),
    contract_item_id UUID REFERENCES contract_items(item_id),
    qty_previous    NUMERIC(18,4),
    qty_current     NUMERIC(18,4),
    qty_cumulative  NUMERIC(18,4),
    unit_price      NUMERIC(14,4),
    amount_current  NUMERIC(18,2),
    amount_cumulative NUMERIC(18,2)
);

CREATE TABLE ipc_deductions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ipc_id          UUID NOT NULL REFERENCES ipcs(ipc_id),
    deduction_type  VARCHAR(40) CHECK (deduction_type IN
                    ('retention','tax','insurance','advance_recovery',
                     'material_price_diff','other')),
    amount          NUMERIC(18,2)
);
```

### Domain 8: Cash Flow

```sql
CREATE TABLE cash_transactions (
    tx_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id      UUID NOT NULL REFERENCES projects(project_id),
    tx_date         DATE NOT NULL,
    tx_type         VARCHAR(10) CHECK (tx_type IN ('in','out')),
    category        VARCHAR(60),  -- ipc_receipt, subcontractor_payment, salary, etc.
    amount          NUMERIC(18,2),
    description     TEXT,
    ipc_id          UUID REFERENCES ipcs(ipc_id),
    contract_id     UUID REFERENCES contracts(contract_id),
    is_forecast     BOOLEAN DEFAULT false,
    due_date        DATE,
    actual_date     DATE
);

CREATE TABLE cash_flow_forecasts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id      UUID NOT NULL REFERENCES projects(project_id),
    month           DATE NOT NULL,   -- first day of month
    expected_inflow  NUMERIC(18,2),
    expected_outflow NUMERIC(18,2),
    confidence_pct  NUMERIC(5,2),
    UNIQUE (project_id, month)
);
```

### Domain 9: Economic Engine Tables

```sql
CREATE TABLE inflation_indices (
    index_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    index_name      VARCHAR(80) NOT NULL,   -- steel, cement, labor, cpi
    index_date      DATE NOT NULL,
    index_value     NUMERIC(12,4),
    UNIQUE (index_name, index_date)
);

CREATE TABLE economic_snapshots (
    snapshot_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id          UUID NOT NULL REFERENCES projects(project_id),
    snapshot_date       DATE NOT NULL,
    actual_cost         NUMERIC(18,2),
    inflation_adj_cost  NUMERIC(18,2),
    financing_cost      NUMERIC(18,2),
    revenue_to_date     NUMERIC(18,2),
    accounting_profit   NUMERIC(18,2),
    real_profit         NUMERIC(18,2),
    economic_profit     NUMERIC(18,2),
    working_capital     NUMERIC(18,2),
    avg_payment_delay_days INT
);

CREATE TABLE simulation_results (
    sim_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id      UUID NOT NULL REFERENCES projects(project_id),
    run_at          TIMESTAMPTZ DEFAULT now(),
    iterations      INT,
    p10_profit      NUMERIC(18,2),
    p50_profit      NUMERIC(18,2),
    p90_profit      NUMERIC(18,2),
    prob_of_loss    NUMERIC(6,4),
    max_working_capital NUMERIC(18,2),
    sensitivity_json JSONB   -- tornado chart data
);
```

### Domain 10: Risk & Delays

```sql
CREATE TABLE risk_events (
    event_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id      UUID NOT NULL REFERENCES projects(project_id),
    activity_id     UUID REFERENCES activities(activity_id),
    event_date      DATE,
    event_type      VARCHAR(20) CHECK (event_type IN
                    ('delay','barrier','risk','claim','change_order')),
    description     TEXT,
    responsible_party VARCHAR(80),
    time_impact_days INT,
    cost_impact     NUMERIC(18,2),
    probability     NUMERIC(4,2),
    severity        VARCHAR(10) CHECK (severity IN ('low','medium','high','critical')),
    status          VARCHAR(20) DEFAULT 'open',
    corrective_action TEXT,
    target_resolution_date DATE,
    owner_id        UUID REFERENCES users(user_id)
);
```

### Domain 11: Alerts / Notifications

```sql
CREATE TABLE alert_rules (
    rule_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id      UUID REFERENCES projects(project_id),  -- NULL = system-wide
    alert_type      VARCHAR(60),
    threshold       NUMERIC,
    condition       VARCHAR(20) CHECK (condition IN ('gt','lt','eq','gte','lte')),
    recipients      UUID[],  -- user_ids
    is_active       BOOLEAN DEFAULT true
);

CREATE TABLE alert_log (
    log_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_id         UUID REFERENCES alert_rules(rule_id),
    fired_at        TIMESTAMPTZ DEFAULT now(),
    message         TEXT,
    acknowledged_at TIMESTAMPTZ,
    acknowledged_by UUID REFERENCES users(user_id)
);
```

---

## 3. API Design

### 3.1 Conventions

- Base URL: `https://api.ipcas.io/v1`
- Auth: Bearer JWT (`Authorization: Bearer <token>`)
- Dates: ISO 8601 (`2025-01-15`)
- Amounts: always in the project's base currency as a numeric string to avoid float drift
- Pagination: `?page=1&per_page=50`; response includes `meta.total`, `meta.page`

### 3.2 Core Endpoints

#### Projects


| Method  | Path                     | Description                                                 |
| ------- | ------------------------ | ----------------------------------------------------------- |
| `GET`   | `/projects`              | List all projects the caller has access to                  |
| `POST`  | `/projects`              | Create project                                              |
| `GET`   | `/projects/{id}`         | Project detail                                              |
| `PATCH` | `/projects/{id}`         | Update project metadata                                     |
| `GET`   | `/projects/{id}/health`  | Dashboard KPI summary                                       |
| `GET`   | `/projects/{id}/members` | List project members + roles                                |
| `POST`  | `/projects/{id}/members` | Add member (userId + roleIds + optional custom permissions) |


#### WBS & Activities


| Method  | Path                                         | Description                                    |
| ------- | -------------------------------------------- | ---------------------------------------------- |
| `GET`   | `/projects/{id}/wbs`                         | Full WBS tree                                  |
| `POST`  | `/projects/{id}/wbs`                         | Create WBS node                                |
| `GET`   | `/projects/{id}/activities`                  | List activities (filterable by wbs_id, status) |
| `POST`  | `/projects/{id}/activities`                  | Create activity                                |
| `PATCH` | `/projects/{id}/activities/{actId}`          | Update activity                                |
| `GET`   | `/projects/{id}/activities/{actId}/progress` | Progress history                               |
| `POST`  | `/projects/{id}/activities/{actId}/progress` | Record progress update                         |


#### Daily Reports


| Method  | Path                                         | Description                               |
| ------- | -------------------------------------------- | ----------------------------------------- |
| `GET`   | `/projects/{id}/daily-reports`               | List reports (date range filter)          |
| `POST`  | `/projects/{id}/daily-reports`               | Create report (draft)                     |
| `GET`   | `/projects/{id}/daily-reports/{rId}`         | Report detail with all sub-entities       |
| `PATCH` | `/projects/{id}/daily-reports/{rId}`         | Update (while draft)                      |
| `POST`  | `/projects/{id}/daily-reports/{rId}/submit`  | Submit for review                         |
| `POST`  | `/projects/{id}/daily-reports/{rId}/approve` | Approve (triggers progress recalculation) |
| `POST`  | `/projects/{id}/daily-reports/{rId}/reject`  | Reject with reason                        |
| `POST`  | `/projects/{id}/daily-reports/sync-batch`    | Offline sync — array of reports           |


#### Cost Control


| Method | Path                                       | Description                         |
| ------ | ------------------------------------------ | ----------------------------------- |
| `GET`  | `/projects/{id}/budgets`                   | Budget by WBS / activity / category |
| `POST` | `/projects/{id}/budgets`                   | Upsert budget line                  |
| `GET`  | `/projects/{id}/costs`                     | Actual costs (filterable)           |
| `POST` | `/projects/{id}/costs`                     | Record actual cost                  |
| `GET`  | `/projects/{id}/costs/variance`            | Budget vs actual by WBS             |
| `GET`  | `/projects/{id}/cost-pools`                | Historical unallocated cost pools   |
| `POST` | `/projects/{id}/cost-pools/{pId}/allocate` | Allocate pool to activities         |


#### Contracts & IPCs


| Method | Path                                  | Description                                           |
| ------ | ------------------------------------- | ----------------------------------------------------- |
| `GET`  | `/projects/{id}/contracts`            | List contracts                                        |
| `POST` | `/projects/{id}/contracts`            | Create contract                                       |
| `GET`  | `/projects/{id}/ipcs`                 | List IPCs                                             |
| `POST` | `/projects/{id}/ipcs`                 | Create IPC (auto-populates from latest progress data) |
| `POST` | `/projects/{id}/ipcs/{ipcId}/submit`  | Submit to employer                                    |
| `POST` | `/projects/{id}/ipcs/{ipcId}/approve` | Mark approved                                         |
| `POST` | `/projects/{id}/ipcs/{ipcId}/pay`     | Record payment with actual date                       |


#### Cash Flow


| Method | Path                                        | Description                           |
| ------ | ------------------------------------------- | ------------------------------------- |
| `GET`  | `/projects/{id}/cash-flow`                  | Actual transactions + rolling balance |
| `POST` | `/projects/{id}/cash-flow/transactions`     | Record cash in/out                    |
| `GET`  | `/projects/{id}/cash-flow/forecast`         | Monthly forecast                      |
| `PUT`  | `/projects/{id}/cash-flow/forecast/{month}` | Update forecast month                 |
| `GET`  | `/projects/{id}/cash-flow/gap-analysis`     | Periods with projected cash deficit   |


#### Economic Engine


| Method | Path                                     | Description                             |
| ------ | ---------------------------------------- | --------------------------------------- |
| `GET`  | `/projects/{id}/economic/snapshot`       | Latest inflation-adjusted P&L           |
| `GET`  | `/projects/{id}/economic/cash-flow-real` | Economic (real) cash flow curve         |
| `GET`  | `/projects/{id}/economic/forecast`       | EAC adjusted for inflation + CPI        |
| `POST` | `/projects/{id}/economic/simulate`       | Run Monte Carlo (body: scenario params) |
| `GET`  | `/projects/{id}/economic/payment-delay`  | IPC delay analysis                      |
| `PUT`  | `/inflation-indices/{name}/{date}`       | Admin: update index value               |


#### KPIs & Dashboard


| Method | Path                          | Description                                         |
| ------ | ----------------------------- | --------------------------------------------------- |
| `GET`  | `/projects/{id}/kpis`         | All KPIs in one call (SPI, CPI, SV, CV, EV, PV, AC) |
| `GET`  | `/projects/{id}/s-curve`      | S-Curve data: planned vs actual progress over time  |
| `GET`  | `/projects/{id}/alerts`       | Active alerts                                       |
| `POST` | `/projects/{id}/alerts/rules` | Create alert rule                                   |


### 3.3 Key Response Shape Examples

`**GET /projects/{id}/kpis**`

```json
{
  "as_of": "2025-04-15",
  "physical_progress": {
    "planned": 0.45,
    "actual": 0.38,
    "variance": -0.07,
    "spi": 0.844
  },
  "cost": {
    "budget": "2800000000",
    "actual_cost": "1150000000",
    "earned_value": "1064000000",
    "cost_variance": "-86000000",
    "cpi": 0.925,
    "budget_consumption": 0.411
  },
  "cash": {
    "total_received": "800000000",
    "total_paid_out": "1100000000",
    "net_balance": "-300000000",
    "receivables": "350000000",
    "payables_to_subs": "120000000"
  },
  "schedule": {
    "critical_activities": 4,
    "behind_schedule": 7,
    "ahead_of_schedule": 2
  }
}
```

---

## 4. Feature Breakdown

### Module 1 — Project Foundation

- Project creation with full metadata (employer, contractor, consultant, dates, contract amount, type, location)
- Mid-project onboarding: cut-off date, Opening Snapshot (progress, cost, receivables, payables)
- Cost pool definition for historical unallocated costs; 3-level allocation methods (by quantity, budget weight, labor/equipment hours)

### Module 2 — WBS & Activities

- Hierarchical WBS tree (unlimited depth); drag-and-drop reorder
- Activity definitions with physical weight, planned quantities, BoQ linkage
- Predecessor/successor relationships (FS/SS/FF/SF with lag)
- Import from Primavera P6 (XER) and Microsoft Project (XML)

### Module 3 — Schedule Control

- Baseline versioning; compare two baselines
- Progress tracking per activity per reporting period
- Auto-computed: SPI, total float, free float, critical path highlighting
- Gantt chart view (read-only); export to PDF
- Delay analysis reports with schedule variance trending

### Module 4 — Daily Field Report

- Multi-discipline entry (civil, mechanical, electrical, HSE, QC, procurement)
- Offline-first mobile form; sync when online
- Attach photos, link to WBS activity, record weather
- Stop/barrier logging with cause coding
- Approval workflow: draft → submitted → reviewed → approved
- Auto-triggers: on approval, progress recalculated and cost booked

### Module 5 — Physical Progress Control

- Weighted average progress formula:
`Project Progress = Σ (Activity Progress × Weight)`
- Period and cumulative quantity tracking
- S-Curve generation (planned vs actual)
- Variance flagging: activities > 5% behind get auto-alert

### Module 6 — Cost & Budget Control

- Budget per WBS level, per cost category
- Actual cost entry with document reference
- Earned Value Management: EV, AC, PV → CPI, SPI, CV, SV
- Forecast-to-complete (EAC) = BAC / CPI
- Cost category analysis: labor, material, equipment, subcontract, overhead

### Module 7 — Cash Flow Management

- Record actual receipts (from employer) and disbursements (subs, suppliers, salaries)
- Monthly rolling forecast with confidence level
- Gap analysis: months where outflow > inflow
- Net Cash Flow = Cash In − Cash Out
- Cash balance history chart

### Module 8 — Contracts & IPCs

- Contract registry (main + subcontracts + purchase + equipment rental)
- Guarantee bond tracking with expiry alerts
- IPC generation: semi-automatic from approved progress data
- Deduction engine: retention, tax, insurance, advance recovery, material price differentials
- IPC status tracking with dates (submitted → approved → paid) and delay monitoring

### Module 9 — Human Resources

- Daily headcount log by discipline and role
- Planned vs actual labor-hours
- Labor productivity = executed quantity / labor hours
- Workforce reports by crew/subcontractor

### Module 10 — Equipment

- Equipment registry with ownership classification (own/rented)
- Daily utilization log: work hours, idle hours, idle reason
- Equipment productivity and utilization rate
- Maintenance & repair cost tracking

### Module 11 — Materials & Warehouse

- Inventory transactions (receipt, issue, waste, adjustment)
- Running balance per material per project
- Critical stock alerts (below minimum level)
- Material consumption vs planned (waste ratio analysis)

### Module 12 — Procurement

- Purchase request → approval → order → delivery workflow
- Supplier comparison (quotes side-by-side)
- Delivery delay tracking and impact on schedule
- Linkage: procurement item → WBS activity needed date

### Module 13 — Subcontractor Control

- Performance scorecard: progress, quality, HSE, payment compliance
- Financial status: billed, paid, outstanding per sub
- Non-conformance and warning log
- Risk flag for subs behind schedule > threshold

### Module 14 — Delays, Barriers & Risk

- Incident logging: delay / barrier / risk / claim / change order
- Responsibility attribution (employer, contractor, force majeure)
- Risk matrix: probability × severity
- Claim documentation (timestamped, linked to daily reports and correspondence)

### Module 15 — Document Control

- Versioned document store (drawings, contracts, correspondence, minutes)
- Document categories, access levels (public / project / restricted)
- Correspondence tracker with response-due-date and open/closed status
- RFI and submittal registers

### Module 16 — Economic Engine

- Inflation adjustment: per cost category, per month, using external indices (steel, cement, labor, CPI)
`Adjusted Cost = Nominal Cost × (Index_Current / Index_At_Cost_Date)`
- Payment delay cost: `Financing Cost = IPC Amount × Annual Rate × Delay Days / 365`
- Three P&L layers: accounting profit, real profit, economic profit
- Working capital forecast: `Max(Cumulative Cost − Cumulative Payment)`
- Monte Carlo simulation: 5,000–10,000 scenarios varying inflation, payment delay, productivity
- Output: P10/P50/P90 profit, probability of loss, tornado sensitivity chart

### Module 17 — Dashboard & Alerts

- Executive dashboard: 10 core KPIs at a glance
- Role-based dashboard variants (project manager, finance, field, executive)
- 15+ configurable alert rules (critical path delays, budget overruns, liquidity gaps, guarantee expiries, missing daily reports, IPC approval delays)
- Push notifications (email / SMS / in-app)

### Module 18 — Access Control

- Three-tier model: System Level → Project Level → Custom Override
- Per-project role assignment; one person can hold multiple roles
- Permission matrix by module + CRUD action
- Full audit trail (who changed what, when)
- Role templates per project type (building, road, industrial, EPC, small project)

---

## 5. Engineering Tasks

### 5.1 Foundation Layer


| #    | Task                                                        | Effort | Owner   |
| ---- | ----------------------------------------------------------- | ------ | ------- |
| F-01 | Design & migrate full DB schema (all 11 domains)            | 5d     | Backend |
| F-02 | Auth service: JWT issuance, refresh, revocation             | 2d     | Backend |
| F-03 | API gateway setup: routing, rate limiting, CORS             | 2d     | Infra   |
| F-04 | Multi-tenancy middleware (project-scoped data isolation)    | 3d     | Backend |
| F-05 | Role & permission engine with project-scoped overrides      | 3d     | Backend |
| F-06 | Audit log middleware (all write operations)                 | 2d     | Backend |
| F-07 | File storage service (S3-compatible, signed URLs)           | 2d     | Backend |
| F-08 | Message bus setup (Kafka / RabbitMQ) with topic definitions | 2d     | Infra   |


### 5.2 Core Business Logic


| #    | Task                                                          | Effort | Owner   |
| ---- | ------------------------------------------------------------- | ------ | ------- |
| C-01 | Project CRUD + membership management APIs                     | 3d     | Backend |
| C-02 | WBS tree API (insert, reorder, computed code propagation)     | 3d     | Backend |
| C-03 | Activity CRUD + relation graph validation                     | 3d     | Backend |
| C-04 | Baseline schedule import (P6 XER + MSPROJECT XML parsers)     | 5d     | Backend |
| C-05 | Daily report API + sub-entities (labor, equipment, materials) | 4d     | Backend |
| C-06 | Daily report approval workflow + event publish                | 2d     | Backend |
| C-07 | Progress recalculation engine (triggered on report approval)  | 3d     | Backend |
| C-08 | Physical progress API: weighted sum, S-curve data endpoint    | 2d     | Backend |
| C-09 | Budget ingestion + variance engine                            | 3d     | Backend |
| C-10 | Actual cost ledger + cost pool allocation logic               | 4d     | Backend |
| C-11 | Cash flow transaction API + gap analysis                      | 3d     | Backend |
| C-12 | Contract + IPC API with deduction engine                      | 5d     | Backend |
| C-13 | Inventory transaction ledger + running balance                | 3d     | Backend |
| C-14 | Equipment log API + utilization calculations                  | 2d     | Backend |
| C-15 | Procurement request workflow (PR → PO → delivery)             | 3d     | Backend |
| C-16 | Subcontractor scorecard & risk flag engine                    | 3d     | Backend |
| C-17 | Risk/delay register API + claim documentation linker          | 2d     | Backend |
| C-18 | Document version control + correspondence tracker             | 3d     | Backend |


### 5.3 Economic Engine


| #    | Task                                                               | Effort | Owner   |
| ---- | ------------------------------------------------------------------ | ------ | ------- |
| E-01 | Inflation index table + ingestion API                              | 1d     | Backend |
| E-02 | Cost-to-category inflation mapping (per project config)            | 2d     | Backend |
| E-03 | Historical cost inflation adjuster (batch + incremental)           | 3d     | Backend |
| E-04 | IPC payment delay calculator (planned vs actual dates)             | 2d     | Backend |
| E-05 | Financing cost engine                                              | 1d     | Backend |
| E-06 | Economic P&L snapshot generator (nightly cron)                     | 2d     | Backend |
| E-07 | Working capital forecast curve                                     | 2d     | Backend |
| E-08 | Monte Carlo simulation engine (Python, NumPy/SciPy, 5k iterations) | 5d     | Data/ML |
| E-09 | Scenario API (define scenario params, get simulation result)       | 2d     | Backend |
| E-10 | Sensitivity / tornado chart data endpoint                          | 1d     | Backend |


### 5.4 KPIs & Alerts


| #    | Task                                                     | Effort | Owner   |
| ---- | -------------------------------------------------------- | ------ | ------- |
| K-01 | EVM calculation service (EV, PV, AC → CPI, SPI, EAC)     | 3d     | Backend |
| K-02 | Unified KPI endpoint (`/kpis`) with caching              | 2d     | Backend |
| K-03 | Alert rule engine (threshold evaluation on event stream) | 3d     | Backend |
| K-04 | Notification delivery (email, SMS, push, in-app)         | 3d     | Backend |
| K-05 | Alert acknowledgement + log API                          | 1d     | Backend |


### 5.5 Offline Sync


| #    | Task                                                       | Effort | Owner    |
| ---- | ---------------------------------------------------------- | ------ | -------- |
| O-01 | Service Worker setup in PWA with offline queue (IndexedDB) | 3d     | Frontend |
| O-02 | Batch sync endpoint: validate, deduplicate, apply          | 3d     | Backend  |
| O-03 | Conflict detection logic + UI for supervisor review        | 3d     | Frontend |
| O-04 | Sync status indicator UI (offline badge, pending count)    | 1d     | Frontend |


### 5.6 Frontend


| #     | Task                                                         | Effort | Owner    |
| ----- | ------------------------------------------------------------ | ------ | -------- |
| UI-01 | Design system / component library (tokens, atoms)            | 4d     | Frontend |
| UI-02 | Project list + creation wizard                               | 2d     | Frontend |
| UI-03 | WBS tree editor (drag-and-drop, inline edit)                 | 4d     | Frontend |
| UI-04 | Daily report form (multi-discipline, photo attach)           | 5d     | Frontend |
| UI-05 | Progress dashboard with S-Curve chart                        | 3d     | Frontend |
| UI-06 | Cost control screens (budget vs actual, variance drill-down) | 3d     | Frontend |
| UI-07 | IPC wizard (auto-filled from progress, deduction table)      | 4d     | Frontend |
| UI-08 | Cash flow chart + gap analysis view                          | 3d     | Frontend |
| UI-09 | Gantt chart (read-only, baseline comparison)                 | 5d     | Frontend |
| UI-10 | Executive dashboard with 10-KPI panel                        | 3d     | Frontend |
| UI-11 | Economic dashboard (3 profit layers, Monte Carlo results)    | 4d     | Frontend |
| UI-12 | Alert center + rule configuration                            | 2d     | Frontend |
| UI-13 | Document archive + correspondence tracker                    | 3d     | Frontend |
| UI-14 | Risk register & matrix view                                  | 2d     | Frontend |
| UI-15 | Access control admin (members, roles, permissions)           | 3d     | Frontend |


---

## 6. Sprint Plan (13 Sprints × 2 Weeks)

> Assumes a team of 4 backend, 3 frontend, 1 data engineer, 1 DevOps, 1 QA.

### Sprint 1 — Infrastructure & Auth

F-01, F-02, F-03, F-04, F-06, F-07, F-08

**Goal:** DB migrated, auth works, API gateway live, S3 wired up, audit log on.

---

### Sprint 2 — Projects, WBS & Members

F-05, C-01, C-02, UI-01, UI-02, UI-15

**Goal:** Create projects, build WBS tree, assign members with roles. Design system initialized.

---

### Sprint 3 — Activities & Schedule Baseline

C-03, C-04, UI-03, partial O-01

**Goal:** Activities CRUD, P6/MSPROJECT import working, WBS tree editor shipped.

---

### Sprint 4 — Daily Report (Online)

C-05, C-06, C-07, UI-04

**Goal:** Field team can submit daily reports online. Approval workflow live. Progress auto-updates on approval.

---

### Sprint 5 — Offline Sync

O-01 (complete), O-02, O-03, O-04

**Goal:** Field supervisor can fill out daily report with no internet. Report syncs on next connection. Conflict UI working.

---

### Sprint 6 — Physical Progress & S-Curve

C-08, K-01 (partial), UI-05

**Goal:** SPI, planned vs actual progress, S-curve chart. Dashboard progress panel live.

---

### Sprint 7 — Budget & Cost Control

C-09, C-10, UI-06

**Goal:** Budget entry per WBS, actual costs logged, cost pools for mid-project onboarding, variance report.

---

### Sprint 8 — Contracts & IPC

C-12, UI-07

**Goal:** Contracts registered. IPC wizard auto-fills from progress. Deductions calculated. Status workflow complete.

---

### Sprint 9 — Cash Flow & Procurement

C-11, C-15, UI-08

**Goal:** Cash flow ledger and gap analysis. Procurement request-to-delivery workflow.

---

### Sprint 10 — Materials, Equipment & HR

C-13, C-14, UI-04 (equipment/labor tabs polish)

**Goal:** Inventory running balance, equipment utilization, labor productivity metrics.

---

### Sprint 11 — Subcontractors, Risks & Documents

C-16, C-17, C-18, UI-13, UI-14

**Goal:** Subcontractor scorecards. Risk/delay register. Document archive + correspondence with due-date tracking.

---

### Sprint 12 — Economic Engine & Simulation

E-01 through E-10, K-01 (complete), UI-11

**Goal:** Inflation-adjusted costs, payment delay costing, Monte Carlo simulation, economic dashboard live.

---

### Sprint 13 — Alerts, Executive Dashboard & Polish

K-02, K-03, K-04, K-05, UI-09, UI-10, UI-12, hardening, performance, E2E test pass

**Goal:** All 15+ alert rules configurable. Executive dashboard with all KPIs. Gantt chart (read-only). Load testing passed. UAT sign-off.

---

## Key Formulas Reference


| Metric              | Formula                                     |
| ------------------- | ------------------------------------------- |
| Activity Progress   | `Actual Qty / Total Qty`                    |
| Project Progress    | `Σ (Activity Progress × Weight)`            |
| Schedule Variance   | `Actual Progress − Planned Progress`        |
| SPI                 | `EV / PV`                                   |
| CPI                 | `EV / AC`                                   |
| Cost Variance       | `EV − AC`                                   |
| EAC                 | `BAC / CPI`                                 |
| Net Cash Flow       | `Cash In − Cash Out`                        |
| Cash Gap            | `Available Cash − Required Cash`            |
| Working Capital     | `Max(Cumulative Cost − Cumulative Payment)` |
| Labor Productivity  | `Executed Quantity / Labor Hours`           |
| Budget Consumption  | `Actual Cost / Budget`                      |
| Inflation Adj. Cost | `Nominal Cost × (Index_Now / Index_Then)`   |
| Financing Cost      | `IPC Amount × Rate × Delay Days / 365`      |
| Accounting Profit   | `Revenue − Actual Cost`                     |
| Real Profit         | `Revenue − Inflation Adjusted Cost`         |
| Economic Profit     | `Revenue − Actual Cost − Financing Cost`    |


---

*Generated from: طرح اولیه سیستم اتوماسیون یکپارچه کنترل پروژه‌های عمرانی — Rev 2*