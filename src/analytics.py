"""
Analytics Engine for Enterprise Inventory Optimization.
Calculates ABC Classification, Dynamic Reorder Points (ROP), and Stockout Risks.
"""

import pandas as pd
import numpy as np


def compute_abc_classification(df: pd.DataFrame) -> pd.DataFrame:
    """
    Performs ABC Inventory Analysis based on annual revenue value.
    - Class A: Top 70% of total revenue contribution (Crucial high-value items)
    - Class B: Next 20% of total revenue contribution (Moderate-value items)
    - Class C: Final 10% of total revenue contribution (Low-value bulk items)
    """
    df = df.copy()
    
    # Annual revenue potential = daily demand * unit selling price * 365
    df["annual_revenue"] = df["daily_demand_rate"] * df["unit_price"] * 365
    
    # Sort descending by annual revenue
    df = df.sort_values(by="annual_revenue", ascending=False).reset_index(drop=True)
    
    # Calculate cumulative percentage
    total_rev = df["annual_revenue"].sum()
    df["cumulative_revenue"] = df["annual_revenue"].cumsum()
    df["cumulative_pct"] = (df["cumulative_revenue"] / total_rev) * 100
    
    # Assign ABC Category
    def assign_abc(pct):
        if pct <= 70:
            return "Class A"
        elif pct <= 90:
            return "Class B"
        else:
            return "Class C"
            
    df["abc_class"] = df["cumulative_pct"].apply(assign_abc)
    return df


def calculate_dynamic_reorder_points(df: pd.DataFrame, service_level_z: float = 1.65) -> pd.DataFrame:
    """
    Calculates dynamic Reorder Points (ROP) and safety stock thresholds.
    Formula:
      Lead Time Demand = Daily Demand * Lead Time Days
      Safety Stock = Z * sqrt(Lead Time Days) * Demand Volatility Buffer
      Reorder Point (ROP) = Lead Time Demand + Safety Stock
      
    Flags items where Current Stock <= Reorder Point as requiring immediate replenishment.
    """
    df = df.copy()
    
    # Assume 15% standard deviation in daily customer demand
    demand_volatility = df["daily_demand_rate"] * 0.15
    
    # Safety stock based on statistical service level (Z = 1.65 corresponds to 95% service level)
    df["calculated_safety_stock"] = np.ceil(
        service_level_z * np.sqrt(df["lead_time_days"]) * demand_volatility
    ).astype(int)
    
    # Expected demand during supplier lead time
    df["lead_time_demand"] = np.ceil(df["daily_demand_rate"] * df["lead_time_days"]).astype(int)
    
    # Dynamic Reorder Point
    df["dynamic_rop"] = df["lead_time_demand"] + df["calculated_safety_stock"]
    
    # Days of inventory remaining on hand
    df["days_of_supply"] = (df["current_stock"] / df["daily_demand_rate"]).round(1)
    
    # Stockout risk flag: True if current stock has dipped at or below the dynamic ROP
    df["needs_reorder"] = df["current_stock"] <= df["dynamic_rop"]
    
    # Recommended order quantity (e.g. 14 days of supply + safety stock)
    df["suggested_order_qty"] = np.ceil(
        (df["daily_demand_rate"] * 14) + df["calculated_safety_stock"]
    ).astype(int)
    
    return df


def get_executive_summary_metrics(df: pd.DataFrame) -> dict:
    """
    Computes key executive KPIs for the management dashboard.
    """
    total_skus = len(df)
    total_inventory_value = (df["current_stock"] * df["unit_cost"]).sum()
    low_stock_count = int(df["needs_reorder"].sum())
    healthy_stock_count = total_skus - low_stock_count
    stockout_risk_pct = round((low_stock_count / total_skus) * 100, 1) if total_skus > 0 else 0
    avg_supplier_reliability = round(df["reliability_score"].mean() * 100, 1)

    return {
        "total_skus": total_skus,
        "total_inventory_value": total_inventory_value,
        "low_stock_count": low_stock_count,
        "healthy_stock_count": healthy_stock_count,
        "stockout_risk_pct": stockout_risk_pct,
        "avg_supplier_reliability": avg_supplier_reliability,
    }
