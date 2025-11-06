# Data Structure Documentation

## Overview
This directory contains structured YAML files that manage network infrastructure data for H-E-B stores and facilities. The data has been optimized to reduce duplication while maintaining clear cross-references between related information.

## File Structure

### 1. `site_master.yaml` (32 lines)
**Purpose**: Primary source of truth for site information.

**Key Fields**:
- `site_id`: Unique site identifier (primary key)
- `site_name`: Site name (e.g., "Store - 00025")
- `address`: Physical address
- `latlng`: Geographic coordinates
- `country_code`: Country code (US)
- `timezone`: Timezone (America/Chicago)
- `sitegroup_ids`: List of site group identifiers
- `created_time` / `modified_time`: Timestamps
- `rftemplate_id`: RF template identifier
- `networktemplate_id`: Network template identifier
- `tzoffset`: Timezone offset
- `notes`: Additional notes

**Cross-References**:
- Links to `vlan_data.yaml` via `site_id`
- Links to `net_manage.yaml` via `site_id`

### 2. `vlan_data.yaml` (54 lines)
**Purpose**: VLAN SVI configurations for network sites.

**Key Fields**:
- `site_id`: Links to site_master.yaml
- `site_name`: Site name for reference
- `vlans`: VLAN SVI configurations
  - `vlan10_svi`, `vlan20_svi`, etc.
  - Each VLAN has `ip`, `netmask`, `gateway`

**Cross-References**:
- Links to `site_master.yaml` via `site_id`
- Links to `net_manage.yaml` via `site_id`

### 3. `net_manage.yaml` (29 lines)
**Purpose**: Network infrastructure management data.

**Key Fields**:
- `site_id`: Links to site_master.yaml
- `site_name`: Site name for reference
- `wireless_platform`: Wireless platform (Mist)
- `switch_ips`: List of switch IP addresses
- `firewall_ips`: List of firewall IP addresses
- `grafana_dash`: Grafana dashboard reference
- `circuits`: Circuit information
- `business_unit`: Business unit classification
- `required_services`: List of required network services

**Cross-References**:
- Links to `site_master.yaml` via `site_id`
- Links to `vlan_data.yaml` via `site_id`

## Cross-Referencing Strategy

### Primary Key: `site_id`
All files use the same `site_id` as the primary key for linking records:
- `c9f13839-adaa-4cd9-964f-71a69928fb86` (Store - 00025)

### Metadata Structure
Each file contains metadata that defines:
- `file_type`: Type of data contained
- `linked_files`: List of related files
- `primary_key`: Key field for linking
- `description`: Purpose of the file

### Cross-Reference Comments
Each record includes inline comments showing cross-references:
```yaml
# Cross-reference: site_master.yaml#c9f13839-adaa-4cd9-964f-71a69928fb86
# Cross-reference: vlan_data.yaml#c9f13839-adaa-4cd9-964f-71a69928fb86
```

## Benefits of This Structure

1. **Reduced File Sizes**: Each file contains only relevant data
2. **No Duplication**: Data is stored once and referenced
3. **Clear Relationships**: Cross-references make relationships explicit
4. **Maintainable**: Changes to one file don't affect others
5. **Scalable**: Easy to add new sites or data types

## Example: Store 25 Data Distribution

**site_master.yaml**:
- Site information, address, coordinates, timestamps

**vlan_data.yaml**:
- All VLAN SVI configurations (10, 20, 30, 40, 50, 60, 70, 80, 90)

**net_manage.yaml**:
- Network infrastructure (switches, wireless platform, required services)

All linked via `site_id: c9f13839-adaa-4cd9-964f-71a69928fb86` 