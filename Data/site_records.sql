-- H-E-B Network Infrastructure Database
-- Consolidated from YAML files: site_master.yaml, vlan_data.yaml, net_manage.yaml
-- Primary key relationships via site_id

-- Sites table (from site_master.yaml)
CREATE TABLE sites (
    site_id VARCHAR(36) PRIMARY KEY,
    site_name VARCHAR(100) NOT NULL,
    store_number INTEGER GENERATED ALWAYS AS (
        CAST(SUBSTRING(site_name FROM 'Store - (\d+)') AS INTEGER)
    ) STORED,
    address TEXT NOT NULL,
    latitude DECIMAL(10, 7),
    longitude DECIMAL(10, 7),
    country_code VARCHAR(2) DEFAULT 'US',
    timezone VARCHAR(50) DEFAULT 'America/Chicago',
    created_time BIGINT,
    modified_time BIGINT,
    rftemplate_id VARCHAR(36),
    networktemplate_id VARCHAR(36),
    tzoffset INTEGER DEFAULT 1080,
    notes TEXT
);

-- VLAN configurations table (from vlan_data.yaml)
CREATE TABLE vlan_configs (
    id SERIAL PRIMARY KEY,
    site_id VARCHAR(36) REFERENCES sites(site_id) ON DELETE CASCADE,
    vlan_number INTEGER NOT NULL,
    svi_name VARCHAR(20) NOT NULL,
    ip_address INET NOT NULL,
    netmask INET NOT NULL,
    gateway INET NOT NULL,
    UNIQUE(site_id, vlan_number)
);

-- Network management table (from net_manage.yaml)
CREATE TABLE network_management (
    site_id VARCHAR(36) PRIMARY KEY REFERENCES sites(site_id) ON DELETE CASCADE,
    wireless_platform VARCHAR(50) DEFAULT 'Mist',
    grafana_dash VARCHAR(100),
    business_unit VARCHAR(50) DEFAULT 'Store'
);

-- Switch IPs table (many-to-many relationship)
CREATE TABLE switch_ips (
    id SERIAL PRIMARY KEY,
    site_id VARCHAR(36) REFERENCES sites(site_id) ON DELETE CASCADE,
    switch_ip INET NOT NULL,
    switch_type VARCHAR(50) DEFAULT 'access'
);

-- Firewall IPs table (many-to-many relationship)
CREATE TABLE firewall_ips (
    id SERIAL PRIMARY KEY,
    site_id VARCHAR(36) REFERENCES sites(site_id) ON DELETE CASCADE,
    firewall_ip INET NOT NULL
);

-- Required services table (many-to-many relationship)
CREATE TABLE required_services (
    id SERIAL PRIMARY KEY,
    site_id VARCHAR(36) REFERENCES sites(site_id) ON DELETE CASCADE,
    service_name VARCHAR(50) NOT NULL
);

-- Circuits table (many-to-many relationship)
CREATE TABLE circuits (
    id SERIAL PRIMARY KEY,
    site_id VARCHAR(36) REFERENCES sites(site_id) ON DELETE CASCADE,
    circuit_name VARCHAR(100) NOT NULL,
    circuit_type VARCHAR(50),
    bandwidth VARCHAR(50)
);

-- Site groups table (many-to-many relationship)
CREATE TABLE site_groups (
    id SERIAL PRIMARY KEY,
    site_id VARCHAR(36) REFERENCES sites(site_id) ON DELETE CASCADE,
    group_id VARCHAR(36) NOT NULL
);

-- Indexes for performance
CREATE INDEX idx_sites_store_number ON sites(store_number);
CREATE INDEX idx_sites_site_name ON sites(site_name);
CREATE INDEX idx_vlan_configs_site_id ON vlan_configs(site_id);
CREATE INDEX idx_vlan_configs_vlan_number ON vlan_configs(vlan_number);
CREATE INDEX idx_switch_ips_site_id ON switch_ips(site_id);
CREATE INDEX idx_required_services_site_id ON required_services(site_id);

-- Sample data insertion (Store 25)
INSERT INTO sites (site_id, site_name, address, latitude, longitude, created_time, modified_time, rftemplate_id, networktemplate_id) VALUES
('c9f13839-adaa-4cd9-964f-71a69928fb86', 'Store - 00025', '925 10th St, Floresville, TX 78114, USA', 29.1443053, -98.1566883, 1674589269, 1717127329, 'ed497897-bc46-48aa-a0bc-e6ee15623c9e', NULL);

-- VLAN configurations for Store 25
INSERT INTO vlan_configs (site_id, vlan_number, svi_name, ip_address, netmask, gateway) VALUES
('c9f13839-adaa-4cd9-964f-71a69928fb86', 10, 'vlan10_svi', '10.2.51.1', '255.255.255.0', '10.2.51.1'),
('c9f13839-adaa-4cd9-964f-71a69928fb86', 20, 'vlan20_svi', '10.2.52.1', '255.255.255.0', '10.2.52.1'),
('c9f13839-adaa-4cd9-964f-71a69928fb86', 30, 'vlan30_svi', '10.2.53.1', '255.255.255.0', '10.2.53.1'),
('c9f13839-adaa-4cd9-964f-71a69928fb86', 40, 'vlan40_svi', '10.2.54.1', '255.255.255.0', '10.2.54.1'),
('c9f13839-adaa-4cd9-964f-71a69928fb86', 50, 'vlan50_svi', '10.2.55.1', '255.255.255.0', '10.2.55.1'),
('c9f13839-adaa-4cd9-964f-71a69928fb86', 60, 'vlan60_svi', '10.2.56.1', '255.255.255.0', '10.2.56.1'),
('c9f13839-adaa-4cd9-964f-71a69928fb86', 70, 'vlan70_svi', '10.2.57.1', '255.255.255.0', '10.2.57.1'),
('c9f13839-adaa-4cd9-964f-71a69928fb86', 80, 'vlan80_svi', '10.2.58.1', '255.255.255.0', '10.2.58.1'),
('c9f13839-adaa-4cd9-964f-71a69928fb86', 90, 'vlan90_svi', '10.2.59.1', '255.255.255.0', '10.2.59.1');

-- Network management for Store 25
INSERT INTO network_management (site_id, wireless_platform, business_unit) VALUES
('c9f13839-adaa-4cd9-964f-71a69928fb86', 'Mist', 'Store');

-- Switch IPs for Store 25
INSERT INTO switch_ips (site_id, switch_ip) VALUES
('c9f13839-adaa-4cd9-964f-71a69928fb86', '10.2.59.30'),
('c9f13839-adaa-4cd9-964f-71a69928fb86', '10.2.59.41');

-- Required services for Store 25
INSERT INTO required_services (site_id, service_name) VALUES
('c9f13839-adaa-4cd9-964f-71a69928fb86', 'DNS'),
('c9f13839-adaa-4cd9-964f-71a69928fb86', 'DHCP'),
('c9f13839-adaa-4cd9-964f-71a69928fb86', 'RADIUS1');

-- Site groups for Store 25
INSERT INTO site_groups (site_id, group_id) VALUES
('c9f13839-adaa-4cd9-964f-71a69928fb86', '67cb1765-171c-4104-b833-0aadfc0c1bd4'),
('c9f13839-adaa-4cd9-964f-71a69928fb86', '7c715094-665b-4f8d-bb44-88ac07bab34a');

-- Useful queries
-- Get all VLANs for a specific store
-- SELECT v.* FROM vlan_configs v 
-- JOIN sites s ON v.site_id = s.site_id 
-- WHERE s.store_number = 25;

-- Get all network info for a store
-- SELECT s.*, nm.wireless_platform, nm.business_unit,
--        array_agg(DISTINCT si.switch_ip) as switch_ips,
--        array_agg(DISTINCT rs.service_name) as required_services
-- FROM sites s
-- LEFT JOIN network_management nm ON s.site_id = nm.site_id
-- LEFT JOIN switch_ips si ON s.site_id = si.site_id
-- LEFT JOIN required_services rs ON s.site_id = rs.site_id
-- WHERE s.store_number = 25
-- GROUP BY s.site_id, nm.wireless_platform, nm.business_unit;
