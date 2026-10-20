# 🧵 Textile Manufacturing ERP & Autonomous Replenishment Engine

> An enterprise supply chain intelligence and automated procurement system for textile mills, garment manufacturing, and apparel export houses. Replaces manual warehouse spreadsheets with dynamic Reorder Point (ROP) modeling and automated vendor Purchase Order (PO) drafting.

---

## 🎯 Executive Summary & Industry Domain

In the **Textile & Apparel Manufacturing Industry**, production lines (spinning, weaving, dyeing, and garment assembly) cannot afford downtime:
- Running out of **Combed Cotton Yarn** halts spinning frames and knitting machines.
- Running out of **Reactive Dyes** or **Finishing Softeners** stops fabric dyeing batches, delaying export ship dates.
- Over-purchasing bulky yarn or heavy fabric rolls clogs warehouse capacity and locks up hundreds of thousands of dollars in working capital.

This project implements an **Autonomous Textile ERP Replenishment Engine**:
1. Connects to a transactional **ERP Database** tracking raw yarns, greige/finished fabrics, reactive dye chemicals, garment trims, and textile vendors.
2. Formulates **Dynamic Reorder Points (ROP)** and **ABC Inventory Classification** based on daily loom/dyeing consumption velocity and spinning mill lead-time variance.
3. Implements **Closed-Loop Automation**: when raw materials dip below safety thresholds, the system automatically drafts official Purchase Orders directly into the ERP database, selects the primary vendor (e.g., *Indus Spinning Mills*, *Sapphire Textiles*, *Kohinoor Dyes*), and logs the action in an audit trail.
4. Provides a **Textile Mill Operations Command Center (Streamlit)** for plant managers to track stockout risks, review consumption thresholds, and approve procurement with one click.

---

## 🏗️ System Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                        TEXTILE ERP ARCHITECTURE                        │
│                                                                        │
│   ┌───────────────────────────┐      ┌─────────────────────────────┐   │
│   │     Textile ERP DB        │      │    Mill Operations App      │   │
│   │  (Postgres / SQLite)      │◄────►│   (Python 3.12 + Streamlit) │   │
│   │                           │      │                             │   │
│   │  Tables:                  │      │  Modules:                   │   │
│   │  • products (Yarn, Fabric)│      │  • database.py (ERP Engine) │   │
│   │  • suppliers (Mills, Dyes)│      │  • analytics.py (ROP & ABC) │   │
│   │  • inventory_levels       │      │  • automation.py (Auto-PO)  │   │
│   │  • purchase_orders        │      │  • app.py (Mill Command UI) │   │
│   │  • audit_logs             │      │                             │   │
│   └─────────────┬─────────────┘      └──────────────┬──────────────┘   │
│                 │                                   │                  │
└─────────────────┼───────────────────────────────────┼──────────────────┘
                  ▼                                   ▼
             Port: 5432                          Port: 8501
         (PostgreSQL Engine)                 (Web Operations Portal)
```

---

## 🧵 Tracked Textile Materials & Units of Measure (UOM)

| Material | Category | Unit (UOM) | Primary Vendor |
| :--- | :--- | :--- | :--- |
| **100% Combed Cotton Yarn (30/1)** | Yarn | Lbs | Indus Spinning Mills Ltd |
| **Polyester Spun Yarn (20/1)** | Yarn | Lbs | Indus Spinning Mills Ltd |
| **Indigo Blue Denim Fabric (12 oz)** | Fabric | Meters | Sapphire Textile Mills |
| **100% Cotton Pique Knit (Polo)** | Fabric | Kg | Sapphire Textile Mills |
| **Cotton Twill Fabric (Chino)** | Fabric | Meters | Sapphire Textile Mills |
| **Reactive Royal Blue Dye** | Dyes & Chemicals | Kg | Kohinoor Dyes & Chemicals |
| **Silicone Softener Agent** | Dyes & Chemicals | Kg | Kohinoor Dyes & Chemicals |
| **YKK Brass Metal Zippers** | Trims & Accessories | Gross | Apex Apparel Trims Co. |
| **4-Hole Horn Poly Buttons** | Trims & Accessories | Gross | Apex Apparel Trims Co. |
| **Export Poly Garment Bags** | Packaging | Cartons | Apex Apparel Trims Co. |

---

## 🔬 Core Analytics & Industrial Engineering Formulas

### 1. Dynamic Safety Stock & Reorder Point (ROP)
$$\text{Safety Stock} = Z \times \sqrt{\text{Lead Time Days}} \times \sigma_{\text{daily demand}}$$
$$\text{Reorder Point (ROP)} = (\text{Daily Consumption Rate} \times \text{Lead Time Days}) + \text{Safety Stock}$$
- **$Z = 1.65$** ensures a **95% service level**, guarding against production downtime while minimizing dead capital.

### 2. Idempotent Automated PO Generation
- Scans inventory daily $\rightarrow$ Flags materials where $\text{Current Stock} \le \text{ROP}$.
- Evaluates existing active orders: prevents duplicate purchase orders if a shipment is already in progress.
- Writes official transactional records into the `purchase_orders` ERP table.

---

## 🚀 How to Run the Project

### Running Locally (Instant Launch):
```bash
cd enterprise-inventory-erp
pip install -r requirements.txt
streamlit run src/app.py
```
Open **`http://localhost:8501`** in your browser.

### Running with Docker Desktop:
```bash
docker compose up --build
```

---

## 💼 CV / Resume Bullet Points

> **Textile Supply Chain ERP & Autonomous Replenishment Engine** | *Python, PostgreSQL/SQLite, Streamlit, Plotly*
> - Engineered an enterprise supply chain intelligence engine for a textile manufacturing ERP, tracking yarn, greige/denim fabric, and chemical dyes across multi-vendor mills.
> - Formulated stochastic Reorder Point (ROP) models ($Z = 1.65$, 95% service level) and Pareto ABC value classification to prevent factory floor production downtime.
> - Built a closed-loop automation pipeline that detects inventory breaches, prevents duplicate mill orders through idempotency checks, and writes transactional Purchase Orders directly to the ERP database.
> - Developed an interactive executive command center featuring live stockout risk KPIs, material consumption curves, and an operations audit log.
