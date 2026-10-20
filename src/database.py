"""
Database connection, query helpers, and ERP transaction handlers for the Textile ERP.
Supports PostgreSQL (default in Docker) and SQLite (automatic fallback for zero-setup local runs).
"""

import os
import sqlite3
import pandas as pd
from sqlalchemy import create_engine, text

# Database connection credentials from environment variables or sensible defaults
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "inventory_erp")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "postgres")

# Build connection string
POSTGRES_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
SQLITE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "local_erp.db")


def get_engine():
    """
    Attempts to connect to PostgreSQL.
    If PostgreSQL is unavailable, seamlessly falls back to local SQLite.
    """
    try:
        engine = create_engine(POSTGRES_URL, pool_pre_ping=True)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return engine
    except Exception:
        sqlite_url = f"sqlite:///{os.path.abspath(SQLITE_PATH)}"
        sqlite_engine = create_engine(sqlite_url)
        _ensure_sqlite_initialized(sqlite_engine)
        return sqlite_engine


def _ensure_sqlite_initialized(engine):
    """Initializes schema and textile seed data in SQLite if empty."""
    schema_path = os.path.join(os.path.dirname(__file__), "..", "data", "init_schema.sql")
    if not os.path.exists(schema_path):
        return

    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM products")).scalar()
            if result and result > 0:
                return  # Already seeded
    except Exception:
        pass  # Tables don't exist yet

    with open(schema_path, "r", encoding="utf-8") as f:
        sql_content = f.read()

    clean_sql = (
        sql_content.replace("SERIAL PRIMARY KEY", "INTEGER PRIMARY KEY AUTOINCREMENT")
        .replace("NUMERIC(10, 2)", "REAL")
        .replace("NUMERIC(12, 2)", "REAL")
        .replace("NUMERIC(8, 2)", "REAL")
        .replace("NUMERIC(3, 2)", "REAL")
        .replace("ON CONFLICT (sku) DO NOTHING", "")
        .replace("ON CONFLICT (product_id) DO NOTHING", "")
        .replace("ON CONFLICT DO NOTHING", "")
        .replace("INSERT INTO", "INSERT OR IGNORE INTO")
    )

    with engine.begin() as conn:
        for statement in clean_sql.split(";"):
            stmt = statement.strip()
            if stmt:
                try:
                    conn.execute(text(stmt))
                except Exception:
                    pass


def reset_demo_database():
    """Wipes all purchase orders and resets inventory levels back to clean factory initial state."""
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM purchase_orders;"))
        conn.execute(text("DELETE FROM audit_logs;"))
        conn.execute(text("INSERT INTO audit_logs (event_type, details) VALUES ('SYSTEM_RESET', 'ERP database reset to factory initial state.');"))
        # Reset inventory levels back to initial seed levels
        conn.execute(text("UPDATE inventory_levels SET current_stock = 450 WHERE product_id = 1;"))
        conn.execute(text("UPDATE inventory_levels SET current_stock = 1800 WHERE product_id = 2;"))
        conn.execute(text("UPDATE inventory_levels SET current_stock = 210 WHERE product_id = 3;"))
        conn.execute(text("UPDATE inventory_levels SET current_stock = 950 WHERE product_id = 4;"))
        conn.execute(text("UPDATE inventory_levels SET current_stock = 120 WHERE product_id = 5;"))
        conn.execute(text("UPDATE inventory_levels SET current_stock = 35 WHERE product_id = 6;"))
        conn.execute(text("UPDATE inventory_levels SET current_stock = 180 WHERE product_id = 7;"))
        conn.execute(text("UPDATE inventory_levels SET current_stock = 25 WHERE product_id = 8;"))
        conn.execute(text("UPDATE inventory_levels SET current_stock = 210 WHERE product_id = 9;"))
        conn.execute(text("UPDATE inventory_levels SET current_stock = 45 WHERE product_id = 10;"))


def get_inventory_dataframe():
    """
    Fetches textile products, warehouse stock levels, unit of measure, and suppliers.
    """
    engine = get_engine()
    query = """
    SELECT 
        p.product_id,
        p.sku,
        p.name AS product_name,
        p.category,
        p.unit_of_measure,
        p.unit_cost,
        p.unit_price,
        i.current_stock,
        i.daily_demand_rate,
        i.lead_time_days,
        i.safety_stock,
        i.reorder_point,
        s.supplier_id,
        s.name AS supplier_name,
        s.category AS supplier_category,
        s.reliability_score
    FROM products p
    JOIN inventory_levels i ON p.product_id = i.product_id
    JOIN suppliers s ON p.primary_supplier_id = s.supplier_id
    ORDER BY p.product_id;
    """
    return pd.read_sql(query, engine)


def get_purchase_orders_dataframe():
    """Fetches all Purchase Orders generated for textile suppliers."""
    engine = get_engine()
    query = """
    SELECT 
        po.po_id,
        po.po_number,
        p.name AS product_name,
        p.sku,
        p.unit_of_measure,
        s.name AS supplier_name,
        po.order_quantity,
        po.total_cost,
        po.status,
        po.created_by,
        po.created_at
    FROM purchase_orders po
    JOIN products p ON po.product_id = p.product_id
    JOIN suppliers s ON po.supplier_id = s.supplier_id
    ORDER BY po.created_at DESC;
    """
    return pd.read_sql(query, engine)


def get_audit_logs_dataframe(limit=30):
    """Fetches the latest audit and automation logs."""
    engine = get_engine()
    query = f"""
    SELECT log_id, event_type, details, created_at
    FROM audit_logs
    ORDER BY created_at DESC
    LIMIT {limit};
    """
    return pd.read_sql(query, engine)


def insert_purchase_order(po_number, product_id, supplier_id, order_quantity, total_cost, status="DRAFT_AUTO"):
    """Inserts a new Purchase Order directly into the ERP database."""
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(
            text("""
            INSERT INTO purchase_orders (po_number, product_id, supplier_id, order_quantity, total_cost, status)
            VALUES (:po_num, :prod_id, :supp_id, :qty, :cost, :status)
            """),
            {
                "po_num": po_number,
                "prod_id": int(product_id),
                "supp_id": int(supplier_id),
                "qty": int(order_quantity),
                "cost": float(total_cost),
                "status": status,
            },
        )


def log_event(event_type, details):
    """Appends an event to the audit log."""
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(
            text("""
            INSERT INTO audit_logs (event_type, details)
            VALUES (:evt, :det)
            """),
            {"evt": event_type, "det": details},
        )


def approve_purchase_order(po_id):
    """Updates a Purchase Order status to APPROVED and logs the action."""
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(
            text("UPDATE purchase_orders SET status = 'APPROVED' WHERE po_id = :id"),
            {"id": int(po_id)},
        )
    log_event("PO_APPROVED", f"Purchase Order #{po_id} approved by Mill Operations Manager.")
