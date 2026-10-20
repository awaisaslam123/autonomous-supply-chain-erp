"""
Closed-Loop Automated Replenishment Engine for Textile Manufacturing.
Monitors fabric rolls, yarn cones, and chemical dyes, auto-generating supplier Purchase Orders
whenever warehouse stock breaches the dynamic Reorder Point.
"""

import time
import random
from src.database import (
    get_inventory_dataframe,
    get_purchase_orders_dataframe,
    insert_purchase_order,
    log_event,
)
from src.analytics import calculate_dynamic_reorder_points


def run_replenishment_automation():
    """
    Executes the automated replenishment pipeline for textile materials:
    1. Reads current inventory & calculates dynamic Reorder Points.
    2. Identifies raw yarn, fabric, or dyes below safety thresholds.
    3. Checks for existing open Purchase Orders to prevent duplicate ordering.
    4. Automatically drafts new Purchase Orders in the ERP database.
    5. Records the automation actions in the audit log.
    """
    raw_df = get_inventory_dataframe()
    analyzed_df = calculate_dynamic_reorder_points(raw_df)

    # Filter for items needing replenishment
    items_to_reorder = analyzed_df[analyzed_df["needs_reorder"] == True]

    # Check existing active Purchase Orders to prevent duplicate ordering
    existing_pos = get_purchase_orders_dataframe()
    active_po_skus = set()
    if not existing_pos.empty:
        active_pos = existing_pos[existing_pos["status"].isin(["DRAFT_AUTO", "APPROVED"])]
        active_po_skus = set(active_pos["sku"].tolist())

    created_orders = []
    skipped_orders = []

    for _, item in items_to_reorder.iterrows():
        sku = item["sku"]
        product_name = item["product_name"]
        uom = item.get("unit_of_measure", "Units")
        current_stock = item["current_stock"]
        dynamic_rop = item["dynamic_rop"]

        # Prevent duplicate orders if an active PO is already in flight
        if sku in active_po_skus:
            skipped_orders.append({
                "sku": sku,
                "product_name": product_name,
                "reason": "An active Mill Purchase Order is already in progress.",
            })
            continue

        # Generate unique PO number (e.g. PO-TX-849201)
        po_number = f"PO-TX-{int(time.time()) % 1000000:06d}-{random.randint(10, 99)}"
        order_qty = int(item["suggested_order_qty"])
        total_cost = round(order_qty * float(item["unit_cost"]), 2)

        # Write PO directly into ERP database
        insert_purchase_order(
            po_number=po_number,
            product_id=item["product_id"],
            supplier_id=item["supplier_id"],
            order_quantity=order_qty,
            total_cost=total_cost,
            status="DRAFT_AUTO",
        )

        # Log the automated event in the audit trail
        audit_msg = (
            f"MILL AUTOPILOT: '{product_name}' stock fell to {current_stock} {uom} (ROP: {dynamic_rop} {uom}). "
            f"Drafted PO {po_number} for {order_qty} {uom} with '{item['supplier_name']}' (${total_cost:,.2f})."
        )
        log_event("AUTO_PO_GENERATED", audit_msg)

        created_orders.append({
            "po_number": po_number,
            "sku": sku,
            "product_name": product_name,
            "unit_of_measure": uom,
            "supplier_name": item["supplier_name"],
            "order_quantity": order_qty,
            "total_cost": total_cost,
            "current_stock": current_stock,
            "reorder_point": dynamic_rop,
        })

    summary = {
        "orders_created_count": len(created_orders),
        "orders_skipped_count": len(skipped_orders),
        "total_replenishment_spend": sum(o["total_cost"] for o in created_orders),
        "created_orders": created_orders,
        "skipped_orders": skipped_orders,
    }
    return summary
