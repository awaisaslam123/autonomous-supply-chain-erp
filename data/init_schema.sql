-- ==============================================================
-- Textile Enterprise ERP - Database Schema & Seed Data
-- Models a Textile Mill / Garment Manufacturing ERP System
-- ==============================================================

-- 1. Textile Suppliers Table (Spinning Mills, Dye Houses, Trims)
CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id SERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    contact_email VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL, -- Spinning Mill, Dye Manufacturer, Trims Vendor
    lead_time_days INT NOT NULL DEFAULT 5,
    reliability_score NUMERIC(3, 2) NOT NULL DEFAULT 0.95,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Textile Products / Raw Materials Master
CREATE TABLE IF NOT EXISTS products (
    product_id SERIAL PRIMARY KEY,
    sku VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(150) NOT NULL,
    category VARCHAR(50) NOT NULL, -- Yarn, Fabric, Dyes & Chemicals, Trims
    unit_of_measure VARCHAR(20) NOT NULL, -- Lbs, Meters, Kg, Gross
    unit_cost NUMERIC(10, 2) NOT NULL,
    unit_price NUMERIC(10, 2) NOT NULL,
    primary_supplier_id INT REFERENCES suppliers(supplier_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Warehouse Inventory Levels
CREATE TABLE IF NOT EXISTS inventory_levels (
    inventory_id SERIAL PRIMARY KEY,
    product_id INT UNIQUE REFERENCES products(product_id) ON DELETE CASCADE,
    current_stock INT NOT NULL DEFAULT 0,
    daily_demand_rate NUMERIC(8, 2) NOT NULL DEFAULT 10.0, -- Consumption per day
    lead_time_days INT NOT NULL DEFAULT 5,
    safety_stock INT NOT NULL DEFAULT 20,
    reorder_point INT NOT NULL DEFAULT 50,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Purchase Orders (Mill Procurement Transactions)
CREATE TABLE IF NOT EXISTS purchase_orders (
    po_id SERIAL PRIMARY KEY,
    po_number VARCHAR(50) UNIQUE NOT NULL,
    product_id INT REFERENCES products(product_id),
    supplier_id INT REFERENCES suppliers(supplier_id),
    order_quantity INT NOT NULL,
    total_cost NUMERIC(12, 2) NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'DRAFT_AUTO',
    created_by VARCHAR(50) DEFAULT 'AUTO_TEXTILE_REPLENISHMENT',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Audit & Automation Logs
CREATE TABLE IF NOT EXISTS audit_logs (
    log_id SERIAL PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    details TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==============================================================
-- Seed Data: Authentic Textile Industry Vendors & Materials
-- ==============================================================

-- Suppliers: Textile Mills & Dye Chemical Manufacturers
INSERT INTO suppliers (name, contact_email, category, lead_time_days, reliability_score) VALUES
('Indus Spinning Mills Ltd', 'orders@indusspinning.com', 'Spinning Mill', 6, 0.97),
('Sapphire Textile Mills', 'sales@sapphiremills.com', 'Weaving & Knit Mill', 8, 0.94),
('Kohinoor Dyes & Chemicals', 'supply@kohinoordyes.com', 'Dyes & Chemicals', 4, 0.98),
('Apex Apparel Trims Co.', 'b2b@apextrims.com', 'Trims & Packaging', 3, 0.99)
ON CONFLICT DO NOTHING;

-- Products: Authentic Textile Raw Materials, Greige & Finished Fabrics, Dyes, Trims
INSERT INTO products (sku, name, category, unit_of_measure, unit_cost, unit_price, primary_supplier_id) VALUES
('YRN-CTN-30S', '100% Combed Cotton Yarn (30/1 Count)', 'Yarn', 'Lbs', 3.80, 5.20, 1),
('YRN-POLY-SPN', 'Polyester Spun Yarn (20/1 Count)', 'Yarn', 'Lbs', 2.10, 3.10, 1),
('FAB-DNM-12OZ', 'Indigo Blue Denim Fabric (12 oz Heavy)', 'Fabric', 'Meters', 6.50, 9.80, 2),
('FAB-PIQ-220', '100% Cotton Pique Knit Fabric (Polo)', 'Fabric', 'Kg', 7.20, 11.00, 2),
('FAB-TWL-CTN', 'Cotton Twill Fabric (Chino / Pants)', 'Fabric', 'Meters', 4.90, 7.50, 2),
('DYE-RCT-BLU', 'Reactive Royal Blue Dye (Novacron)', 'Dyes & Chemicals', 'Kg', 18.50, 27.00, 3),
('CHM-SFT-SIL', 'Silicone Fabric Softener Finishing Agent', 'Dyes & Chemicals', 'Kg', 12.00, 18.50, 3),
('TRM-YKK-ZIP', 'YKK Brass Metal Zippers (5-inch Denim)', 'Trims & Accessories', 'Gross', 28.00, 42.00, 4),
('TRM-BTN-4HL', '4-Hole Horn Polyester Buttons', 'Trims & Accessories', 'Gross', 8.50, 14.00, 4),
('PKG-GAR-BAG', 'Export Polyethylene Garment Cover Bags', 'Packaging', 'Cartons', 22.00, 35.00, 4)
ON CONFLICT (sku) DO NOTHING;

-- Initial Stock Levels (Some items intentionally low to demonstrate automated mill reordering)
INSERT INTO inventory_levels (product_id, current_stock, daily_demand_rate, lead_time_days, safety_stock, reorder_point) VALUES
(1, 450,  120.0, 6, 250, 970),   -- Critically Low Cotton Yarn! 450 < 970 (Mill order needed)
(2, 1800, 80.0,  6, 150, 630),   -- Healthy Yarn Stock
(3, 210,  65.0,  8, 180, 700),   -- Low Denim Fabric! 210 < 700
(4, 950,  50.0,  8, 120, 520),   -- Healthy Pique Fabric
(5, 120,  40.0,  8, 100, 420),   -- Low Twill Fabric! 120 < 420
(6, 35,   15.0,  4, 20,  80),    -- Low Reactive Dye! 35 < 80
(7, 180,  12.0,  4, 15,  63),    -- Healthy Softener Stock
(8, 25,   8.0,   3, 10,  34),    -- Low YKK Zippers! 25 < 34
(9, 210,  20.0,  3, 15,  75),    -- Healthy Buttons Stock
(10, 45,  18.0,  3, 15,  69)     -- Low Packaging Bags! 45 < 69
ON CONFLICT (product_id) DO NOTHING;

-- Initial Seed Log
INSERT INTO audit_logs (event_type, details) VALUES
('SYSTEM_INIT', 'Textile ERP Database initialized with spinning mills, fabric rolls, dyes, and trims.');
