# H-E-B Network Infrastructure SQL Database

## Overview

This SQLite database consolidates the network infrastructure data from the YAML files into a proper relational database structure. This provides better data integrity, easier querying, and more efficient data management.

## Database Schema

### Tables

1. **`sites`** - Primary site information
   - `site_id` (VARCHAR(36)) - Primary key
   - `site_name` (VARCHAR(100)) - Store name
   - `store_number` (INTEGER) - Extracted store number
   - `address` (TEXT) - Physical address
   - `latitude`/`longitude` (REAL) - GPS coordinates
   - Additional metadata fields

2. **`vlan_configs`** - VLAN SVI configurations
   - `id` (INTEGER) - Auto-increment primary key
   - `site_id` (VARCHAR(36)) - Foreign key to sites
   - `vlan_number` (INTEGER) - VLAN number (10, 20, 30, etc.)
   - `svi_name` (VARCHAR(20)) - SVI interface name
   - `ip_address` (VARCHAR(15)) - SVI IP address
   - `netmask` (VARCHAR(15)) - Subnet mask
   - `gateway` (VARCHAR(15)) - Gateway IP

3. **`network_management`** - Network infrastructure management
   - `site_id` (VARCHAR(36)) - Primary key, foreign key to sites
   - `wireless_platform` (VARCHAR(50)) - Wireless platform (Mist)
   - `grafana_dash` (VARCHAR(100)) - Grafana dashboard
   - `business_unit` (VARCHAR(50)) - Business unit (Store)

4. **`switch_ips`** - Switch IP addresses
   - `id` (INTEGER) - Auto-increment primary key
   - `site_id` (VARCHAR(36)) - Foreign key to sites
   - `switch_ip` (VARCHAR(15)) - Switch IP address
   - `switch_type` (VARCHAR(50)) - Switch type (access)

5. **`required_services`** - Required network services
   - `id` (INTEGER) - Auto-increment primary key
   - `site_id` (VARCHAR(36)) - Foreign key to sites
   - `service_name` (VARCHAR(50)) - Service name (DNS, DHCP, RADIUS1)

6. **`site_groups`** - Site group associations
   - `id` (INTEGER) - Auto-increment primary key
   - `site_id` (VARCHAR(36)) - Foreign key to sites
   - `group_id` (VARCHAR(36)) - Group ID

## IP Addressing Schema

The database follows the established IP addressing schema:

### Single-digit stores (1-9)
- Format: `10.0.{store}{vlan}.1`
- Example: Store 6, VLAN 10 = `10.0.61.1`

### Double-digit stores (10-99)
- Format: `10.{first_digit}.{second_digit}{vlan}.1`
- Example: Store 19, VLAN 10 = `10.1.91.1`

### Triple-digit stores (100+)
- Format: `10.{first_digit}.{second_digit}{third_digit}{vlan}.1`
- Example: Store 125, VLAN 10 = `10.1.251.1`

## Usage

### Python Interface

Use the `NetworkDatabase` class in `Scripts/network_db.py`:

```python
from network_db import NetworkDatabase

# Initialize database
db = NetworkDatabase()

# Get store information
store_info = db.get_complete_site_info(25)
if store_info:
    print(f"Store: {store_info['site'].site_name}")
    print(f"VLANs: {len(store_info['vlans'])}")
    print(f"Switch IPs: {store_info['network_management'].switch_ips}")

# List all stores
stores = db.list_all_stores()
for store_num, store_name in stores:
    print(f"Store {store_num}: {store_name}")

# Search stores
results = db.search_stores("Floresville")
```

### SQL Queries

Direct SQL queries can be performed:

```sql
-- Get all VLANs for Store 25
SELECT v.* FROM vlan_configs v 
JOIN sites s ON v.site_id = s.site_id 
WHERE s.store_number = 25;

-- Get complete network info for a store
SELECT s.*, nm.wireless_platform, nm.business_unit,
       GROUP_CONCAT(DISTINCT si.switch_ip) as switch_ips,
       GROUP_CONCAT(DISTINCT rs.service_name) as required_services
FROM sites s
LEFT JOIN network_management nm ON s.site_id = nm.site_id
LEFT JOIN switch_ips si ON s.site_id = si.site_id
LEFT JOIN required_services rs ON s.site_id = rs.site_id
WHERE s.store_number = 25
GROUP BY s.site_id, nm.wireless_platform, nm.business_unit;
```

## Migration

### From YAML to SQL

Run the migration script to convert existing YAML data:

```bash
cd Scripts
python3 simple_migration.py
```

This will:
1. Create the SQLite database with proper schema
2. Add all existing stores (6, 9, 19, 25)
3. Generate VLAN configurations with correct IP addressing
4. Add network management data
5. Verify data integrity

### Adding New Stores

Use the `NetworkDatabase` class to add new stores:

```python
from network_db import NetworkDatabase

db = NetworkDatabase()

# Add a new store with all configurations
success = db.add_store_with_vlans(
    store_number=42,
    site_id="new-site-id",
    site_name="Store - 00042",
    address="123 Main St, City, TX 12345",
    lat=30.123456,
    lng=-98.123456
)
```

## Advantages Over YAML

1. **Data Integrity**: Foreign key constraints prevent orphaned records
2. **Better Queries**: Complex joins and aggregations
3. **Performance**: Indexed lookups are much faster
4. **Atomic Operations**: Update one record without touching others
5. **Data Validation**: Constraints ensure data quality
6. **Scalability**: Handles large datasets efficiently

## File Structure

```
Data/
├── network_infrastructure.db    # SQLite database
├── site_records_sqlite.sql     # SQLite schema
├── site_master.yaml            # Original YAML (backup)
├── vlan_data.yaml             # Original YAML (backup)
├── net_manage.yaml            # Original YAML (backup)
└── README_SQL.md              # This file
```

## Backup Strategy

- Keep original YAML files as backup/reference
- Use SQL database for all new operations
- Regular database backups recommended
- Migration scripts available for data recovery

## Future Enhancements

1. **Web Interface**: Build web UI for database management
2. **API Endpoints**: REST API for database access
3. **Automated Backups**: Scheduled database backups
4. **Data Validation**: Enhanced validation rules
5. **Reporting**: Built-in reporting capabilities 