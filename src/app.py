import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
"""
TexFlow ERP — Enterprise Textile Supply Chain & Autonomous Replenishment System.
Engineered with Modern Enterprise UX Design (20+ Years Design Standard).
Built with Streamlit & Plotly.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.database import (
    get_inventory_dataframe,
    get_purchase_orders_dataframe,
    get_audit_logs_dataframe,
    approve_purchase_order,
    reset_demo_database,
)
from src.analytics import (
    compute_abc_classification,
    calculate_dynamic_reorder_points,
    get_executive_summary_metrics,
)
from src.automation import run_replenishment_automation

# ==============================================================
# Page Configuration & Executive Theme
# ==============================================================
st.set_page_config(
    page_title="TexFlow ERP | Autonomous Supply Chain",
    page_icon="🧵",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==============================================================
# Enterprise UI Design System (Modern 2026 SaaS / Fiori Standard)
# ==============================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #0f172a;
    }

    /* Top Command Header */
    .top-command-bar {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 18px 24px;
        margin-bottom: 24px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.04);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .brand-left {
        display: flex;
        flex-direction: column;
        gap: 4px;
    }
    .brand-title {
        font-size: 1.55rem;
        font-weight: 800;
        color: #0f172a;
        letter-spacing: -0.02em;
        display: flex;
        align-items: center;
        gap: 10px;
        white-space: nowrap;
        margin: 0;
    }
    .brand-title .accent {
        color: #0284c7;
    }
    .version-tag {
        background: #f1f5f9;
        color: #475569;
        border: 1px solid #cbd5e1;
        font-size: 0.72rem;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 6px;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }
    .brand-subtitle {
        font-size: 0.88rem;
        color: #64748b;
        font-weight: 500;
        margin: 0;
    }
    .system-status-chip {
        background: #ecfdf5;
        border: 1px solid #a7f3d0;
        color: #065f46;
        padding: 6px 14px;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        white-space: nowrap;
    }
    .pulse-dot {
        width: 8px;
        height: 8px;
        background-color: #10b981;
        border-radius: 50%;
        box-shadow: 0 0 8px #10b981;
    }

    /* Executive KPI Cards */
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 24px;
    }
    .kpi-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.04);
        position: relative;
        overflow: hidden;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px -2px rgba(0, 0, 0, 0.08);
    }
    .kpi-top {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
    }
    .kpi-label {
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #64748b;
    }
    .kpi-icon-pill {
        width: 36px;
        height: 36px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
    }
    .kpi-value {
        font-size: 1.85rem;
        font-weight: 800;
        color: #0f172a;
        line-height: 1.1;
        letter-spacing: -0.03em;
    }
    .kpi-footer {
        margin-top: 10px;
        font-size: 0.82rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .kpi-danger { color: #ef4444; }
    .kpi-success { color: #10b981; }
    .kpi-info { color: #0284c7; }

    /* Modern Table Card */
    .table-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
        margin-bottom: 24px;
    }
    .section-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 4px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .section-desc {
        font-size: 0.86rem;
        color: #64748b;
        margin-bottom: 18px;
    }

    /* Modern Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 1px solid #e2e8f0;
        padding-bottom: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        font-size: 0.92rem;
        color: #64748b;
        padding: 10px 18px;
        border-radius: 8px;
        transition: all 0.2s ease;
    }
    .stTabs [aria-selected="true"] {
        color: #0f172a !important;
        background-color: #f1f5f9 !important;
        border-bottom: 2px solid #0284c7 !important;
    }

    /* Buttons */
    .stButton>button {
        font-weight: 600;
        border-radius: 8px;
        padding: 10px 20px;
        transition: all 0.2s ease;
        letter-spacing: 0.01em;
    }
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }

    /* Sidebar Clean styling */
    section[data-testid="stSidebar"] {
        background-color: #f8fafc;
        border-right: 1px solid #e2e8f0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def load_textile_data():
    """Fetches textile stock and calculates dynamic ROP and ABC analysis."""
    raw_df = get_inventory_dataframe()
    rop_df = calculate_dynamic_reorder_points(raw_df)
    abc_df = compute_abc_classification(rop_df)
    return abc_df


# ==============================================================
# Top Navigation & Command Bar (Enterprise Header)
# ==============================================================
st.markdown(
    """
    <div class="top-command-bar">
        <div class="brand-left">
            <div class="brand-title">🧵 <span>Tex<span class="accent">Flow</span> ERP</span> <span class="version-tag">Textile Manufacturing Edition</span></div>
            <div class="brand-subtitle">Autonomous Textile Supply Chain & Mill Replenishment System</div>
        </div>
        <div class="system-status-chip">
            <span class="pulse-dot"></span>
            LIVE SYSTEM ONLINE
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ==============================================================
# Sidebar: Control Tower
# ==============================================================
st.sidebar.markdown("### 🎛️ Control Tower")
st.sidebar.caption("Autonomous replenishment & mill synchronization")
st.sidebar.markdown("---")

st.sidebar.markdown("#### ⚡ Autonomous Procurement")
st.sidebar.write("Scans live yarn cones, fabric rolls, and chemical stock against dynamic safety thresholds.")

if st.sidebar.button("⚡ Run Replenishment Check", type="primary", use_container_width=True):
    with st.spinner("Analyzing consumption rates & spinning mill lead times..."):
        result = run_replenishment_automation()
        if result["orders_created_count"] > 0:
            st.sidebar.success(
                f"Generated {result['orders_created_count']} Mill Purchase Orders (${result['total_replenishment_spend']:,.2f})!"
            )
        else:
            st.sidebar.info("All low-stock items already have active orders with spinning mills.")

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Sync ERP Data", use_container_width=True):
    st.rerun()

if st.sidebar.button("⏮️ Reset Demo Data (Day-1)", use_container_width=True, help="Clear all orders and restore factory demo snapshot"):
    reset_demo_database()
    st.sidebar.success("Database restored to clean Day-1 state!")
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("#### 🏭 Mill Telemetry")
st.sidebar.caption(
    """
    • **Spinning Mills**: Active (Indus)<br>
    • **Weaving / Denim**: Active (Sapphire)<br>
    • **Dye House**: Active (Kohinoor)<br>
    • **Idempotency Guard**: 🟢 Enforced
    """,
    unsafe_allow_html=True,
)

# ==============================================================
# Load & Compute Analytics
# ==============================================================
df = load_textile_data()
metrics = get_executive_summary_metrics(df)

# ==============================================================
# Executive Metric Cards (4 Tiles)
# ==============================================================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-top">
                <span class="kpi-label">Active Materials</span>
                <div class="kpi-icon-pill" style="background:#e0f2fe; color:#0284c7;">📦</div>
            </div>
            <div class="kpi-value">{metrics['total_skus']}</div>
            <div class="kpi-footer kpi-info">Across 4 Supply Categories</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-top">
                <span class="kpi-label">Stock Valuation</span>
                <div class="kpi-icon-pill" style="background:#ecfdf5; color:#059669;">💵</div>
            </div>
            <div class="kpi-value">${metrics['total_inventory_value']:,.2f}</div>
            <div class="kpi-footer kpi-success">Working Capital Deployed</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    status_color = "kpi-danger" if metrics["low_stock_count"] > 0 else "kpi-success"
    badge_bg = "#fef2f2" if metrics["low_stock_count"] > 0 else "#f0fdf4"
    icon_color = "#dc2626" if metrics["low_stock_count"] > 0 else "#16a34a"
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-top">
                <span class="kpi-label">Stockout Risk</span>
                <div class="kpi-icon-pill" style="background:{badge_bg}; color:{icon_color};">⚠️</div>
            </div>
            <div class="kpi-value">{metrics['stockout_risk_pct']}%</div>
            <div class="kpi-footer {status_color}">🚨 {metrics['low_stock_count']} Materials Below Reorder Threshold</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col4:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-top">
                <span class="kpi-label">Mill OTIF Score</span>
                <div class="kpi-icon-pill" style="background:#fef3c7; color:#d97706;">🎯</div>
            </div>
            <div class="kpi-value">{metrics['avg_supplier_reliability']}%</div>
            <div class="kpi-footer" style="color:#d97706;">On-Time In-Full Delivery Index</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")

# ==============================================================
# Navigation Tabs (Modern Professional Layout)
# ==============================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "🏭 Warehouse Stock Master",
    "📊 Consumption & ROP Analytics",
    "📋 Mill Procurement Queue",
    "🛡️ ERP Audit & Compliance",
])

# ==============================================================
# TAB 1: WAREHOUSE STOCK MASTER
# ==============================================================
with tab1:
    st.markdown(
        """
        <div class="table-card">
            <div class="section-title">📦 Real-Time Material Master</div>
            <div class="section-desc">Live warehouse telemetry tracking cotton yarn cones, fabric rolls, reactive dyes, and garment trims.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    filter_col1, filter_col2, filter_col3 = st.columns([2, 1, 1])
    with filter_col1:
        category_options = ["All Categories"] + sorted(df["category"].unique().tolist())
        selected_cat = st.selectbox("Filter by Category", category_options, label_visibility="collapsed")
    with filter_col2:
        status_filter = st.selectbox("Status Filter", ["All Items", "Reorder Required Only", "Adequate Stock Only"], label_visibility="collapsed")
    with filter_col3:
        search_query = st.text_input("Search Material", placeholder="🔍 Search material...", label_visibility="collapsed")

    view_df = df if selected_cat == "All Categories" else df[df["category"] == selected_cat]
    view_df = view_df.copy()
    if "unit_of_measure" not in view_df.columns:
        view_df["unit_of_measure"] = "Units"

    if status_filter == "Reorder Required Only":
        view_df = view_df[view_df["needs_reorder"] == True]
    elif status_filter == "Adequate Stock Only":
        view_df = view_df[view_df["needs_reorder"] == False]

    if search_query.strip():
        view_df = view_df[
            view_df["product_name"].str.contains(search_query, case=False, na=False) |
            view_df["sku"].str.contains(search_query, case=False, na=False)
        ]

    display_table = view_df[[
        "sku", "product_name", "category", "unit_of_measure",
        "current_stock", "dynamic_rop", "calculated_safety_stock",
        "days_of_supply", "supplier_name", "needs_reorder"
    ]].copy()

    display_table["Status"] = display_table["needs_reorder"].apply(
        lambda x: "🔴 CRITICAL REORDER" if x else "🟢 SAFE"
    )

    display_table = display_table.rename(columns={
        "sku": "Item Code",
        "product_name": "Material Description",
        "category": "Category",
        "unit_of_measure": "UOM",
        "current_stock": "Current Stock",
        "dynamic_rop": "Reorder Point (ROP)",
        "calculated_safety_stock": "Safety Buffer",
        "days_of_supply": "Days of Supply",
        "supplier_name": "Primary Vendor / Mill",
    })

    st.dataframe(
        display_table.drop(columns=["needs_reorder"]),
        use_container_width=True,
        hide_index=True,
    )

    # One-Click CSV Export for Inventory
    inv_csv = display_table.drop(columns=["needs_reorder"]).to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Export Inventory Report (CSV)",
        data=inv_csv,
        file_name="texflow_warehouse_inventory.csv",
        mime="text/csv",
        help="Download clean inventory records for warehouse management or finance audit."
    )

# ==============================================================
# TAB 2: CONSUMPTION & ROP ANALYTICS
# ==============================================================
with tab2:
    st.markdown(
        """
        <div class="table-card">
            <div class="section-title">📊 Consumption Modeling & Dynamic Reorder Points</div>
            <div class="section-desc">Comparing actual warehouse stock against calculated stochastic reorder boundaries (Z=1.65, 95% confidence).</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Sleek Plotly Comparison Chart
    fig_comp = go.Figure()
    fig_comp.add_trace(go.Bar(
        x=df["product_name"],
        y=df["current_stock"],
        name="Current Stock On-Hand",
        marker=dict(color="#0284c7", opacity=0.9),
    ))
    fig_comp.add_trace(go.Scatter(
        x=df["product_name"],
        y=df["dynamic_rop"],
        name="Safety Reorder Threshold (ROP)",
        mode="lines+markers",
        line=dict(color="#ef4444", width=3, dash="dash"),
        marker=dict(size=8, color="#ef4444"),
    ))
    fig_comp.update_layout(
        template="plotly_white",
        height=380,
        margin=dict(t=20, b=90, l=40, r=20),
        xaxis_tickangle=-30,
        yaxis=dict(gridcolor="#f1f5f9", title="Quantity (in UOM)"),
        xaxis=dict(gridcolor="rgba(0,0,0,0)"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        font=dict(family="Plus Jakarta Sans, sans-serif"),
    )
    st.plotly_chart(fig_comp, use_container_width=True)

    st.markdown("---")
    chart_c1, chart_c2 = st.columns(2)

    with chart_c1:
        st.subheader("Inventory Health Ratio")
        health_summary = pd.DataFrame({
            "Status": ["Stock Adequate", "Reorder Required"],
            "Count": [metrics["healthy_stock_count"], metrics["low_stock_count"]],
        })
        fig_pie = px.pie(
            health_summary,
            names="Status",
            values="Count",
            color="Status",
            color_discrete_map={"Stock Adequate": "#10b981", "Reorder Required": "#ef4444"},
            hole=0.6,
        )
        fig_pie.update_layout(
            template="plotly_white",
            margin=dict(t=10, b=20, l=10, r=10),
            height=280,
            font=dict(family="Plus Jakarta Sans, sans-serif"),
            legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5),
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with chart_c2:
        st.subheader("ABC Inventory Value (Pareto Contribution)")
        fig_abc = px.bar(
            df,
            x="product_name",
            y="annual_revenue",
            color="abc_class",
            labels={"annual_revenue": "Annual Consumption Value ($)", "product_name": "Material"},
            color_discrete_map={"Class A": "#0f172a", "Class B": "#f59e0b", "Class C": "#94a3b8"},
        )
        fig_abc.update_layout(
            template="plotly_white",
            margin=dict(t=10, b=90, l=30, r=10),
            height=280,
            xaxis_tickangle=-30,
            yaxis=dict(gridcolor="#f1f5f9"),
            font=dict(family="Plus Jakarta Sans, sans-serif"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig_abc, use_container_width=True)

    st.markdown("---")
    st.subheader("🔍 Material Deep-Dive & Consumption Inspector")
    st.caption("Select any raw material to inspect its consumption runway, lead time, and safety buffer calculations.")

    selected_material = st.selectbox(
        "Choose Material to Inspect:",
        df["product_name"].tolist(),
        label_visibility="collapsed"
    )

    mat_row = df[df["product_name"] == selected_material].iloc[0]
    uom = mat_row.get("unit_of_measure", "Units")

    d_col1, d_col2, d_col3, d_col4 = st.columns(4)
    with d_col1:
        st.metric("Current Stock", f"{mat_row['current_stock']} {uom}")
    with d_col2:
        st.metric("Daily Consumption", f"{mat_row['daily_demand_rate']} {uom} / day")
    with d_col3:
        st.metric("Estimated Supply Runway", f"{mat_row['days_of_supply']} Days", delta="Critical Buffer" if mat_row['needs_reorder'] else "Adequate", delta_color="inverse" if mat_row['needs_reorder'] else "normal")
    with d_col4:
        st.metric("Supplier Delivery Lead Time", f"{mat_row['lead_time_days']} Days", help=f"Vendor: {mat_row['supplier_name']}")

# ==============================================================
# TAB 3: MILL PROCUREMENT QUEUE
# ==============================================================
with tab3:
    st.markdown(
        """
        <div class="table-card">
            <div class="section-title">📋 Mill Procurement Queue (Official Purchase Orders)</div>
            <div class="section-desc">Automated, idempotent purchase orders generated by the replenishment engine for spinning and chemical vendors.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    po_df = get_purchase_orders_dataframe()
    if not po_df.empty and "unit_of_measure" not in po_df.columns:
        po_df["unit_of_measure"] = "Units"

    if po_df.empty:
        st.info("No Purchase Orders currently in the ERP system. Use '⚡ Run Replenishment Check' in the left sidebar to generate orders.")
    else:
        st.dataframe(po_df, use_container_width=True, hide_index=True)

        # One-Click CSV Export for Purchase Orders
        po_csv = po_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Export Purchase Orders (CSV)",
            data=po_csv,
            file_name="texflow_mill_purchase_orders.csv",
            mime="text/csv",
            help="Export official Purchase Orders for vendor dispatch or accounting."
        )

        st.markdown("---")
        st.markdown("#### ✍️ Mill Operations Approval Action")
        st.caption("Human-in-the-loop governance: review auto-drafted orders before final payment & delivery commitment.")

        draft_pos = po_df[po_df["status"] == "DRAFT_AUTO"]

        if not draft_pos.empty:
            review_col1, review_col2 = st.columns([3, 1])
            with review_col1:
                po_id_to_approve = st.selectbox(
                    "Select Order to Authorize:",
                    draft_pos["po_id"].tolist(),
                    format_func=lambda x: f"PO #{x} — {draft_pos[draft_pos['po_id'] == x]['product_name'].values[0]} ({draft_pos[draft_pos['po_id'] == x]['order_quantity'].values[0]} {draft_pos[draft_pos['po_id'] == x]['unit_of_measure'].values[0]}) • Total: ${draft_pos[draft_pos['po_id'] == x]['total_cost'].values[0]:,.2f}",
                )
            with review_col2:
                st.write("")
                st.write("")
                if st.button("✅ Authorize Purchase Order", type="primary", use_container_width=True):
                    approve_purchase_order(po_id_to_approve)
                    st.success(f"Order #{po_id_to_approve} authorized and dispatched to vendor!")
                    st.rerun()
        else:
            st.success("✨ All automated Purchase Orders have been reviewed and approved.")

# ==============================================================
# TAB 4: ERP AUDIT & COMPLIANCE
# ==============================================================
with tab4:
    st.markdown(
        """
        <div class="table-card">
            <div class="section-title">🛡️ System Governance & Immutable Audit Trail</div>
            <div class="section-desc">Traceable event history recording every automated replenishment decision, threshold breach, and manual approval.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    logs_df = get_audit_logs_dataframe(limit=50)

    if logs_df.empty:
        st.info("No audit logs recorded yet.")
    else:
        st.dataframe(logs_df, use_container_width=True, hide_index=True)

        # One-Click CSV Export for Audit Trail
        audit_csv = logs_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Export Compliance Audit Trail (CSV)",
            data=audit_csv,
            file_name="texflow_compliance_audit_trail.csv",
            mime="text/csv",
            help="Download timestamped audit log for factory governance."
        )
