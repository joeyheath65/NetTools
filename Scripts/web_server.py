#!/usr/bin/env python3
"""
H-E-B Network Infrastructure Web Server
Provides API endpoints for the HTML frontend
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
import sqlite3
import uuid
from pathlib import Path
from network_db import NetworkDatabase
import os

app = Flask(__name__)

# Database path
DB_PATH = Path("../Data/network_infrastructure.db")

@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_from_directory('../Data', 'network_manager.html')

@app.route('/api/dashboard')
def dashboard():
    """Get dashboard statistics"""
    try:
        db = NetworkDatabase()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Get statistics
        cursor.execute("SELECT COUNT(*) FROM sites")
        total_stores = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM vlan_configs")
        total_vlans = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM switch_ips")
        total_switches = cursor.fetchone()[0]
        
        cursor.execute("SELECT MIN(store_number), MAX(store_number) FROM sites")
        min_store, max_store = cursor.fetchone()
        
        # Get recent stores
        cursor.execute("""
            SELECT store_number, site_name, address 
            FROM sites 
            ORDER BY store_number DESC 
            LIMIT 5
        """)
        recent_stores = []
        for row in cursor.fetchall():
            recent_stores.append({
                'store_number': row[0],
                'site_name': row[1],
                'address': row[2]
            })
        
        conn.close()
        
        return jsonify({
            'totalStores': total_stores,
            'totalVLANs': total_vlans,
            'totalSwitches': total_switches,
            'minStore': min_store or 0,
            'maxStore': max_store or 0,
            'recentStores': recent_stores
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stores', methods=['GET'])
def get_stores():
    """Get all stores"""
    try:
        db = NetworkDatabase()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT s.store_number, s.site_name, s.address, s.latitude, s.longitude,
                   nm.wireless_platform, nm.business_unit
            FROM sites s
            LEFT JOIN network_management nm ON s.site_id = nm.site_id
            ORDER BY s.store_number
        """)
        
        stores = []
        for row in cursor.fetchall():
            stores.append({
                'store_number': row[0],
                'site_name': row[1],
                'address': row[2],
                'latitude': row[3],
                'longitude': row[4],
                'wireless_platform': row[5] or 'Mist',
                'business_unit': row[6] or 'Store'
            })
        
        conn.close()
        return jsonify(stores)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stores', methods=['POST'])
def add_store():
    """Add a new store"""
    try:
        data = request.json
        db = NetworkDatabase()
        
        # Generate site_id
        site_id = str(uuid.uuid4())
        
        # Add store with VLANs
        success = db.add_store_with_vlans(
            store_number=data['store_number'],
            site_id=site_id,
            site_name=data['site_name'],
            address=data['address'],
            lat=data['latitude'],
            lng=data['longitude']
        )
        
        if success:
            return jsonify({'message': 'Store added successfully'}), 201
        else:
            return jsonify({'error': 'Failed to add store'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/vlans')
def get_vlans():
    """Get all VLAN configurations"""
    try:
        db = NetworkDatabase()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT s.store_number, v.vlan_number, v.ip_address, v.netmask, v.gateway
            FROM vlan_configs v
            JOIN sites s ON v.site_id = s.site_id
            ORDER BY s.store_number, v.vlan_number
        """)
        
        vlans = []
        for row in cursor.fetchall():
            vlans.append({
                'store_number': row[0],
                'vlan_number': row[1],
                'ip_address': row[2],
                'netmask': row[3],
                'gateway': row[4]
            })
        
        conn.close()
        return jsonify(vlans)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stores/<int:store_number>')
def get_store_details(store_number):
    """Get detailed information for a specific store"""
    try:
        db = NetworkDatabase()
        store_info = db.get_complete_site_info(store_number)
        
        if store_info and store_info['site']:
            site = store_info['site']
            return jsonify({
                'store_number': site.store_number,
                'site_name': site.site_name,
                'address': site.address,
                'latitude': site.latitude,
                'longitude': site.longitude,
                'wireless_platform': site.wireless_platform,
                'business_unit': site.business_unit,
                'timezone': 'America/Chicago'  # Default timezone
            })
        else:
            return jsonify({'error': 'Store not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/search')
def search():
    """Advanced search"""
    try:
        store_num = request.args.get('store')
        vlan_num = request.args.get('vlan')
        ip_addr = request.args.get('ip')
        city = request.args.get('city')
        
        db = NetworkDatabase()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Build search query
        query = """
            SELECT DISTINCT s.store_number, s.site_name, s.address
            FROM sites s
            LEFT JOIN vlan_configs v ON s.site_id = v.site_id
            WHERE 1=1
        """
        params = []
        
        if store_num:
            query += " AND s.store_number = ?"
            params.append(int(store_num))
        
        if vlan_num:
            query += " AND v.vlan_number = ?"
            params.append(int(vlan_num))
        
        if ip_addr:
            query += " AND v.ip_address LIKE ?"
            params.append(f"%{ip_addr}%")
        
        if city:
            query += " AND s.address LIKE ?"
            params.append(f"%{city}%")
        
        cursor.execute(query, params)
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'store_number': row[0],
                'site_name': row[1],
                'address': row[2]
            })
        
        conn.close()
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stores/<int:store_number>/vlans')
def get_store_vlans(store_number):
    """Get VLAN configurations for a specific store"""
    try:
        db = NetworkDatabase()
        store_info = db.get_complete_site_info(store_number)
        
        if store_info and store_info['vlans']:
            vlans = []
            for vlan in store_info['vlans']:
                vlans.append({
                    'vlan_number': vlan.vlan_number,
                    'svi_name': vlan.svi_name,
                    'ip_address': vlan.ip_address,
                    'netmask': vlan.netmask,
                    'gateway': vlan.gateway
                })
            return jsonify(vlans)
        else:
            return jsonify([])
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/vlans/<int:store_number>/<int:vlan_number>')
def get_vlan_details(store_number, vlan_number):
    """Get specific VLAN configuration"""
    try:
        db = NetworkDatabase()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT v.vlan_number, v.svi_name, v.ip_address, v.netmask, v.gateway
            FROM vlan_configs v
            JOIN sites s ON v.site_id = s.site_id
            WHERE s.store_number = ? AND v.vlan_number = ?
        """, (store_number, vlan_number))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return jsonify({
                'vlan_number': row[0],
                'svi_name': row[1],
                'ip_address': row[2],
                'netmask': row[3],
                'gateway': row[4]
            })
        else:
            return jsonify({'error': 'VLAN not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/vlans', methods=['POST'])
def add_vlan():
    """Add a new VLAN configuration"""
    try:
        data = request.json
        db = NetworkDatabase()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Get site_id for the store
        cursor.execute("SELECT site_id FROM sites WHERE store_number = ?", (data['store_number'],))
        result = cursor.fetchone()
        
        if result:
            site_id = result[0]
            
            # Add VLAN configuration
            cursor.execute("""
                INSERT OR REPLACE INTO vlan_configs (
                    site_id, vlan_number, svi_name, ip_address, netmask, gateway
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                site_id,
                data['vlan_number'],
                data['svi_name'],
                data['ip_address'],
                data['netmask'],
                data['gateway']
            ))
            
            conn.commit()
            conn.close()
            return jsonify({'message': 'VLAN added successfully'}), 201
        else:
            conn.close()
            return jsonify({'error': 'Store not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/vlans/<int:store_number>/<int:vlan_number>', methods=['PUT'])
def update_vlan(store_number, vlan_number):
    """Update VLAN configuration"""
    try:
        data = request.json
        db = NetworkDatabase()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Update VLAN configuration
        cursor.execute("""
            UPDATE vlan_configs 
            SET svi_name = ?, ip_address = ?, netmask = ?, gateway = ?
            WHERE site_id = (SELECT site_id FROM sites WHERE store_number = ?) 
            AND vlan_number = ?
        """, (
            data['svi_name'],
            data['ip_address'],
            data['netmask'],
            data['gateway'],
            store_number,
            vlan_number
        ))
        
        if cursor.rowcount > 0:
            conn.commit()
            conn.close()
            return jsonify({'message': 'VLAN updated successfully'})
        else:
            conn.close()
            return jsonify({'error': 'VLAN not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stores/<int:store_number>', methods=['PUT'])
def update_store(store_number):
    """Update store information"""
    try:
        data = request.json
        db = NetworkDatabase()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Update site information
        cursor.execute("""
            UPDATE sites 
            SET site_name = ?, address = ?, latitude = ?, longitude = ?
            WHERE store_number = ?
        """, (
            data['site_name'],
            data['address'],
            data['latitude'],
            data['longitude'],
            store_number
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Store updated successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stores/<int:store_number>', methods=['DELETE'])
def delete_store(store_number):
    """Delete a store and all its configurations"""
    try:
        db = NetworkDatabase()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Get site_id for the store
        cursor.execute("SELECT site_id FROM sites WHERE store_number = ?", (store_number,))
        result = cursor.fetchone()
        
        if result:
            site_id = result[0]
            
            # Delete all related data (cascade will handle most)
            cursor.execute("DELETE FROM sites WHERE site_id = ?", (site_id,))
            
            conn.commit()
            conn.close()
            
            return jsonify({'message': 'Store deleted successfully'})
        else:
            conn.close()
            return jsonify({'error': 'Store not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stores/<int:store_number>/details')
def get_store_complete_details(store_number):
    """Get complete store information including all VLANs, switch IPs, and network management"""
    try:
        db = NetworkDatabase()
        store_info = db.get_complete_site_info(store_number)
        
        if store_info and store_info['site']:
            site = store_info['site']
            vlans = store_info['vlans'] or []
            net_mgmt = store_info['network_management']
            
            # Format VLANs for response
            vlans_data = []
            for vlan in vlans:
                vlans_data.append({
                    'vlan_number': vlan.vlan_number,
                    'svi_name': vlan.svi_name,
                    'ip_address': vlan.ip_address,
                    'netmask': vlan.netmask,
                    'gateway': vlan.gateway
                })
            
            # Get switch IPs
            switch_ips = []
            if net_mgmt:
                for ip in net_mgmt.switch_ips:
                    switch_ips.append({
                        'ip_address': ip,
                        'ip_type': 'switch'
                    })
            
            return jsonify({
                'store_number': site.store_number,
                'site_name': site.site_name,
                'address': site.address,
                'latitude': site.latitude,
                'longitude': site.longitude,
                'timezone': 'America/Chicago',
                'wireless_platform': site.wireless_platform,
                'business_unit': site.business_unit,
                'vlans': vlans_data,
                'switch_ips': switch_ips
            })
        else:
            return jsonify({'error': 'Store not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stores/<int:store_number>/switch-ips')
def get_store_switch_ips(store_number):
    """Get switch IPs for a specific store"""
    try:
        db = NetworkDatabase()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Get site_id for the store
        cursor.execute("SELECT site_id FROM sites WHERE store_number = ?", (store_number,))
        result = cursor.fetchone()
        
        if result:
            site_id = result[0]
            
            # Get switch IPs
            cursor.execute("""
                SELECT switch_ip, switch_type
                FROM switch_ips 
                WHERE site_id = ?
                ORDER BY switch_ip
            """, (site_id,))
            
            switch_ips = []
            for row in cursor.fetchall():
                switch_ips.append({
                    'ip_address': row[0],
                    'ip_type': row[1] or 'access'
                })
            
            conn.close()
            return jsonify(switch_ips)
        else:
            conn.close()
            return jsonify({'error': 'Store not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stores/<int:store_number>/switch-ips', methods=['POST'])
def add_switch_ip(store_number):
    """Add a new switch IP for a store"""
    try:
        data = request.json
        db = NetworkDatabase()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Get site_id for the store
        cursor.execute("SELECT site_id FROM sites WHERE store_number = ?", (store_number,))
        result = cursor.fetchone()
        
        if result:
            site_id = result[0]
            
            # Add switch IP
            cursor.execute("""
                INSERT INTO switch_ips (site_id, switch_ip, switch_type)
                VALUES (?, ?, ?)
            """, (site_id, data['ip_address'], data.get('switch_type', 'access')))
            
            conn.commit()
            conn.close()
            return jsonify({'message': 'Switch IP added successfully'}), 201
        else:
            conn.close()
            return jsonify({'error': 'Store not found'}), 404
            
    except sqlite3.OperationalError as e:
        return jsonify({'error': f'Database operation failed: {str(e)}'}), 500
    except sqlite3.IntegrityError as e:
        return jsonify({'error': f'Data integrity error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@app.route('/api/stores/<int:store_number>/switch-ips/<ip_address>')
def get_switch_ip_details(store_number, ip_address):
    """Get specific switch IP details"""
    try:
        db = NetworkDatabase()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT si.switch_ip, si.switch_type
            FROM switch_ips si
            JOIN sites s ON si.site_id = s.site_id
            WHERE s.store_number = ? AND si.switch_ip = ?
        """, (store_number, ip_address))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return jsonify({
                'ip_address': row[0],
                'ip_type': row[1] or 'access'
            })
        else:
            return jsonify({'error': 'Switch IP not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stores/<int:store_number>/switch-ips/<ip_address>', methods=['PUT'])
def update_switch_ip(store_number, ip_address):
    """Update a switch IP for a store"""
    try:
        data = request.json
        db = NetworkDatabase()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Update switch IP
        cursor.execute("""
            UPDATE switch_ips 
            SET switch_ip = ?, switch_type = ?
            WHERE site_id = (SELECT site_id FROM sites WHERE store_number = ?) 
            AND switch_ip = ?
        """, (
            data['ip_address'],
            data.get('switch_type', 'access'),
            store_number,
            ip_address
        ))
        
        if cursor.rowcount > 0:
            conn.commit()
            conn.close()
            return jsonify({'message': 'Switch IP updated successfully'})
        else:
            conn.close()
            return jsonify({'error': 'Switch IP not found'}), 404
            
    except sqlite3.OperationalError as e:
        return jsonify({'error': f'Database operation failed: {str(e)}'}), 500
    except sqlite3.IntegrityError as e:
        return jsonify({'error': f'Data integrity error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@app.route('/api/stores/<int:store_number>/switch-ips/<ip_address>', methods=['DELETE'])
def delete_switch_ip(store_number, ip_address):
    """Delete a switch IP for a store"""
    try:
        db = NetworkDatabase()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Delete switch IP
        cursor.execute("""
            DELETE FROM switch_ips 
            WHERE site_id = (SELECT site_id FROM sites WHERE store_number = ?) 
            AND switch_ip = ?
        """, (store_number, ip_address))
        
        if cursor.rowcount > 0:
            conn.commit()
            conn.close()
            return jsonify({'message': 'Switch IP deleted successfully'})
        else:
            conn.close()
            return jsonify({'error': 'Switch IP not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/switch-ips/all')
def get_all_switch_ips():
    """Get all switch IPs across all stores"""
    try:
        db = NetworkDatabase()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT s.store_number, si.switch_ip, si.switch_type
            FROM switch_ips si
            JOIN sites s ON si.site_id = s.site_id
            ORDER BY s.store_number, si.switch_ip
        """)
        
        switch_ips = []
        for row in cursor.fetchall():
            switch_ips.append({
                'store_number': row[0],
                'ip_address': row[1],
                'ip_type': row[2] or 'access'
            })
        
        conn.close()
        return jsonify(switch_ips)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting H-E-B Network Infrastructure Web Server...")
    print("Open your browser to: http://localhost:5002")
    print("Press Ctrl+C to stop the server")
    
    app.run(debug=True, host='0.0.0.0', port=5002) 