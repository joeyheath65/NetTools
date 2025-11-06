# H-E-B Network Infrastructure Web Interface

## Overview

A modern, responsive web interface for managing H-E-B network infrastructure data. This provides an easy-to-use GUI for viewing, adding, and updating store information, VLAN configurations, and network management data.

## Features

### 🎯 **Dashboard**
- **Real-time statistics** - Total stores, VLANs, switches
- **Store range** - Shows min/max store numbers
- **Recent stores** - Latest additions to the database

### 🏪 **Store Management**
- **View all stores** - Complete store listing with details
- **Search stores** - Find stores by number, name, or address
- **Add new stores** - Form-based store creation with automatic VLAN generation
- **Edit stores** - Update store information
- **Delete stores** - Remove stores and all associated data

### 🌐 **VLAN Management**
- **View VLAN configurations** - All VLAN SVI configurations
- **Search VLANs** - Find by store number
- **IP addressing** - Automatic IP generation based on store schema
- **VLAN details** - IP, netmask, gateway information

### 🔍 **Advanced Search**
- **Multi-criteria search** - Store number, VLAN, IP address, city
- **Flexible queries** - Combine multiple search parameters
- **Real-time results** - Instant search results

## Quick Start

### 1. **Start the Web Server**
```bash
cd Scripts
python3 start_web_interface.py
```

### 2. **Open Your Browser**
Navigate to: `http://localhost:5000`

### 3. **Start Managing**
- Click **Dashboard** to see overview
- Click **Stores** to view all stores
- Click **Add Store** to add new stores
- Click **VLANs** to view VLAN configurations
- Click **Search** for advanced queries

## Interface Guide

### **Dashboard Tab**
- **Statistics Cards** - Shows total counts and ranges
- **Recent Stores** - Latest 5 stores added
- **Quick Actions** - Links to common tasks

### **Stores Tab**
- **Search Box** - Filter stores by number, name, or address
- **Store Cards** - Each store displayed as a card
- **Action Buttons** - View details, edit, or delete stores

### **VLANs Tab**
- **Store Grouping** - VLANs grouped by store
- **VLAN Grid** - Visual display of VLAN configurations
- **IP Information** - Shows SVI IP addresses

### **Add Store Tab**
- **Form Fields** - Store number, name, address, coordinates
- **Auto-Generation** - Automatically creates VLAN configurations
- **Validation** - Ensures data integrity

### **Search Tab**
- **Advanced Filters** - Multiple search criteria
- **Flexible Queries** - Combine parameters
- **Results Display** - Clean results presentation

## API Endpoints

The web interface uses these REST API endpoints:

### **Dashboard**
- `GET /api/dashboard` - Get statistics and recent stores

### **Stores**
- `GET /api/stores` - Get all stores
- `POST /api/stores` - Add new store
- `GET /api/stores/{id}` - Get store details
- `PUT /api/stores/{id}` - Update store
- `DELETE /api/stores/{id}` - Delete store

### **VLANs**
- `GET /api/vlans` - Get all VLAN configurations
- `GET /api/stores/{id}/vlans` - Get store VLANs

### **Search**
- `GET /api/search` - Advanced search with parameters

## Data Management

### **Adding Stores**
1. Click **Add Store** tab
2. Fill in store information:
   - Store Number (required)
   - Store Name (required)
   - Address (required)
   - Latitude/Longitude (required)
   - Timezone (optional)
3. Click **Add Store**
4. System automatically:
   - Generates VLAN configurations (10, 20, 30, 40, 50, 60, 70, 80, 90)
   - Creates switch IPs based on VLAN 60
   - Adds required services (DNS, DHCP, RADIUS1)
   - Sets up network management

### **IP Addressing Schema**
The system automatically generates IP addresses:

| Store Type | Format | Example |
|------------|--------|---------|
| **Single-digit** (1-9) | `10.0.{store}{vlan}.1` | Store 6, VLAN 10 = `10.0.61.1` |
| **Double-digit** (10-99) | `10.{first}.{second}{vlan}.1` | Store 19, VLAN 10 = `10.1.91.1` |
| **Triple-digit** (100+) | `10.{first}{second}.{third}{vlan}.1` | Store 720, VLAN 10 = `10.72.1.1` |

### **Editing Stores**
1. Click **Stores** tab
2. Find the store you want to edit
3. Click **Edit** button
4. Modify information
5. Save changes

### **Searching Data**
1. Click **Search** tab
2. Enter search criteria:
   - Store Number
   - VLAN Number
   - IP Address
   - City
3. Click **Search**
4. View results

## Technical Details

### **Architecture**
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Backend**: Python Flask
- **Database**: SQLite
- **API**: RESTful JSON endpoints

### **Dependencies**
- `flask` - Web framework
- `sqlite3` - Database (built-in)
- `network_db.py` - Database utilities

### **File Structure**
```
Data/
├── network_manager.html      # Web interface
├── network_infrastructure.db # SQLite database
└── README_Web_Interface.md  # This file

Scripts/
├── web_server.py            # Flask server
├── start_web_interface.py   # Startup script
└── network_db.py           # Database utilities
```

## Troubleshooting

### **Server Won't Start**
1. Check if Flask is installed: `pip install flask`
2. Verify database exists: `Data/network_infrastructure.db`
3. Check port 5000 is available

### **Database Issues**
1. Run migration scripts:
   ```bash
   python3 simple_migration.py
   python3 populate_all_stores.py
   ```

### **Browser Issues**
1. Clear browser cache
2. Try different browser
3. Check JavaScript is enabled

### **API Errors**
1. Check server logs for error messages
2. Verify database connection
3. Ensure proper JSON format in requests

## Security Notes

- **Development Server** - This uses Flask's development server
- **No Authentication** - Add authentication for production use
- **Local Access** - Server runs on localhost only
- **Database Backup** - Regular backups recommended

## Future Enhancements

1. **User Authentication** - Login system
2. **Role-based Access** - Different permission levels
3. **Audit Logging** - Track changes
4. **Bulk Operations** - Import/export data
5. **Real-time Updates** - WebSocket connections
6. **Mobile App** - Native mobile interface
7. **Advanced Reporting** - Custom reports and analytics
8. **Integration** - Connect with other H-E-B systems

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review server logs for error messages
3. Verify database integrity
4. Test with a simple store addition 