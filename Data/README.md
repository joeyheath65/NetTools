# Data Structure Documentation

## Overview

This directory contains structured YAML files that manage network infrastructure data for H-E-B stores and facilities. The data has been optimized to reduce duplication while maintaining cross-references between related information.

## File Structure

### 1. `store_sites.yaml` (6,345 lines, 395 records)
**Purpose**: Primary store location database with basic information for all sites.

**Key Fields**:
- `id`: Unique site identifier
- `name`: Site name (e.g., "Store - 00720")
- `address`: Physical address
- `latlng`: Geographic coordinates
- `country_code`: Country code (US)
- `timezone`: Timezone (America/Chicago)
- `sitegroup_ids`: List of site group identifiers
- `created_time` / `modified_time`: Timestamps
- `rftemplate_id`: RF template identifier
- `networktemplate_id`: Network template identifier
- `tzoffset`: Timezone offset
- `network_config_ref`: **NEW** - Reference to detailed network configuration (if available)

**Cross-References**:
- Sites with detailed network configurations have a `network_config_ref` field pointing to `detailed_network_configs.yaml`

### 2. `detailed_network_configs.yaml` (63 lines, 2 records)
**Purpose**: Detailed network configurations for sites that require specific network setup.

**Key Fields**:
- `site_id`: References the site ID from `store_sites.yaml`
- `site_name`: Human-readable site name
- `wireless_platform`: Wireless platform (e.g., "Mist")
- `business_unit`: Business unit classification (e.g., "Store", "MWTA")
- `switch_ips`: List of switch IP addresses
- `vlans`: VLAN configurations with SVI details
- `required_services`: List of required network services

**Cross-References**:
- `site_id` links back to `store_sites.yaml`
- `required_services` references services in `service_endpoints.yaml`

### 3. `service_endpoints.yaml` (35 lines, 3 services)
**Purpose**: Global network service configurations used across all sites.

**Key Fields**:
- `service`: Service name (e.g., "RADIUS1", "DNS", "DHCP")
- `endpoint(s)`: Service endpoint IP addresses
- `ports`: Service ports
- `protocol`: Network protocol (e.g., "udp")
- `type`: Service type
- `secret`: Authentication secret (if applicable)

## Data Relationships

```
store_sites.yaml
    ↓ (network_config_ref)
detailed_network_configs.yaml
    ↓ (required_services)
service_endpoints.yaml
```

## Optimization Benefits

### Before Restructuring:
- **Duplication**: Store 00025 appeared in both `store_sites.yaml` and `site_info.yaml`
- **Inconsistent Structure**: Different files had different field sets
- **No Cross-References**: No way to link related data
- **File Size**: 8,714 lines total

### After Restructuring:
- **Eliminated Duplication**: Each site appears only once in `store_sites.yaml`
- **Consistent Structure**: Clear separation of basic vs. detailed data
- **Cross-References**: Easy to link related information
- **Reduced File Size**: 6,345 lines total (27% reduction)
- **Service Integration**: Sites can reference required services

## Usage Examples

### Finding a Site's Network Configuration
```python
# Load store sites
with open('store_sites.yaml', 'r') as f:
    sites = yaml.safe_load(f)

# Find site by name
site = next(s for s in sites if s['name'] == 'Store - 00025')

# Check if detailed network config exists
if 'network_config_ref' in site:
    config_file, site_id = site['network_config_ref'].split('#')
    # Load detailed network configuration
    with open(config_file, 'r') as f:
        configs = yaml.safe_load(f)
    network_config = next(c for c in configs if c['site_id'] == site_id)
```

### Finding Required Services for a Site
```python
# Get required services from network config
required_services = network_config.get('required_services', [])

# Load service endpoints
with open('service_endpoints.yaml', 'r') as f:
    services = yaml.safe_load(f)

# Find service configurations
site_services = [s for s in services if s['service'] in required_services]
```

## Maintenance

### Adding a New Site with Detailed Network Config:
1. Add basic info to `store_sites.yaml`
2. Add detailed network config to `detailed_network_configs.yaml`
3. Add `network_config_ref` to the site in `store_sites.yaml`

### Adding a New Service:
1. Add service configuration to `service_endpoints.yaml`
2. Update `required_services` in relevant `detailed_network_configs.yaml` entries

### Backup Files:
- `site_info.yaml.backup`: Original site info before restructuring 