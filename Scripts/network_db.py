#!/usr/bin/env python3
"""
Network Infrastructure Database Utility
Provides easy interface for working with the SQL database
"""

import sqlite3
import ipaddress
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

@dataclass
class SiteInfo:
    site_id: str
    site_name: str
    store_number: int
    address: str
    latitude: float
    longitude: float
    wireless_platform: str = "Mist"
    business_unit: str = "Store"

@dataclass
class VLANConfig:
    site_id: str
    vlan_number: int
    svi_name: str
    ip_address: str
    netmask: str
    gateway: str

@dataclass
class NetworkManagement:
    site_id: str
    wireless_platform: str
    switch_ips: List[str]
    firewall_ips: List[str]
    required_services: List[str]
    business_unit: str

class NetworkDatabase:
    def __init__(self, db_path: str = "../Data/network_infrastructure.db"):
        self.db_path = Path(db_path)
        
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def get_site_by_store_number(self, store_number: int) -> Optional[SiteInfo]:
        """Get site information by store number"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT s.site_id, s.site_name, s.store_number, s.address, 
                       s.latitude, s.longitude, nm.wireless_platform, nm.business_unit
                FROM sites s
                LEFT JOIN network_management nm ON s.site_id = nm.site_id
                WHERE s.store_number = ?
            """, (store_number,))
            
            row = cursor.fetchone()
            if row:
                return SiteInfo(
                    site_id=row[0],
                    site_name=row[1],
                    store_number=row[2],
                    address=row[3],
                    latitude=row[4],
                    longitude=row[5],
                    wireless_platform=row[6] or "Mist",
                    business_unit=row[7] or "Store"
                )
            return None
            
        finally:
            conn.close()
    
    def get_vlans_for_site(self, site_id: str) -> List[VLANConfig]:
        """Get all VLAN configurations for a site"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT site_id, vlan_number, svi_name, ip_address, netmask, gateway
                FROM vlan_configs
                WHERE site_id = ?
                ORDER BY vlan_number
            """, (site_id,))
            
            vlans = []
            for row in cursor.fetchall():
                vlans.append(VLANConfig(
                    site_id=row[0],
                    vlan_number=row[1],
                    svi_name=row[2],
                    ip_address=row[3],
                    netmask=row[4],
                    gateway=row[5]
                ))
            return vlans
            
        finally:
            conn.close()
    
    def get_network_management(self, site_id: str) -> Optional[NetworkManagement]:
        """Get network management info for a site"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Get network management record
            cursor.execute("""
                SELECT wireless_platform, business_unit
                FROM network_management
                WHERE site_id = ?
            """, (site_id,))
            
            nm_row = cursor.fetchone()
            if not nm_row:
                return None
                
            # Get switch IPs
            cursor.execute("""
                SELECT switch_ip FROM switch_ips WHERE site_id = ?
            """, (site_id,))
            switch_ips = [row[0] for row in cursor.fetchall()]
            
            # Get firewall IPs
            cursor.execute("""
                SELECT firewall_ip FROM firewall_ips WHERE site_id = ?
            """, (site_id,))
            firewall_ips = [row[0] for row in cursor.fetchall()]
            
            # Get required services
            cursor.execute("""
                SELECT service_name FROM required_services WHERE site_id = ?
            """, (site_id,))
            required_services = [row[0] for row in cursor.fetchall()]
            
            return NetworkManagement(
                site_id=site_id,
                wireless_platform=nm_row[0],
                switch_ips=switch_ips,
                firewall_ips=firewall_ips,
                required_services=required_services,
                business_unit=nm_row[1]
            )
            
        finally:
            conn.close()
    
    def get_complete_site_info(self, store_number: int) -> Optional[Dict]:
        """Get complete site information including VLANs and network management"""
        site = self.get_site_by_store_number(store_number)
        if not site:
            return None
            
        vlans = self.get_vlans_for_site(site.site_id)
        net_mgmt = self.get_network_management(site.site_id)
        
        return {
            'site': site,
            'vlans': vlans,
            'network_management': net_mgmt
        }
    
    def add_site(self, site_info: SiteInfo) -> bool:
        """Add a new site to the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO sites (
                    site_id, site_name, address, latitude, longitude,
                    country_code, timezone, created_time, modified_time,
                    rftemplate_id, networktemplate_id, tzoffset, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                site_info.site_id,
                site_info.site_name,
                site_info.address,
                site_info.latitude,
                site_info.longitude,
                'US',
                'America/Chicago',
                None,  # created_time
                None,  # modified_time
                None,  # rftemplate_id
                None,  # networktemplate_id
                1080,  # tzoffset
                ''     # notes
            ))
            
            # Add network management record
            cursor.execute("""
                INSERT INTO network_management (site_id, wireless_platform, business_unit)
                VALUES (?, ?, ?)
            """, (site_info.site_id, site_info.wireless_platform, site_info.business_unit))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Error adding site: {e}")
            return False
        finally:
            conn.close()
    
    def add_vlan_config(self, vlan_config: VLANConfig) -> bool:
        """Add VLAN configuration for a site"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO vlan_configs (
                    site_id, vlan_number, svi_name, ip_address, netmask, gateway
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                vlan_config.site_id,
                vlan_config.vlan_number,
                vlan_config.svi_name,
                vlan_config.ip_address,
                vlan_config.netmask,
                vlan_config.gateway
            ))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Error adding VLAN config: {e}")
            return False
        finally:
            conn.close()
    
    def add_switch_ip(self, site_id: str, switch_ip: str) -> bool:
        """Add switch IP for a site"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO switch_ips (site_id, switch_ip)
                VALUES (?, ?)
            """, (site_id, switch_ip))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Error adding switch IP: {e}")
            return False
        finally:
            conn.close()
    
    def generate_ip_for_store(self, store_number: int, vlan_number: int) -> str:
        """Generate IP address for store and VLAN based on schema"""
        vlan = vlan_number // 10  # VLAN 10 -> 1, VLAN 20 -> 2, etc.
        
        if store_number < 10:
            # Single digit: 10.0.{store}{vlan}.1
            return f"10.0.{store_number}{vlan}.1"
        elif store_number < 100:
            # Double digit: 10.{first_digit}.{second_digit}{vlan}.1
            first_digit = store_number // 10
            second_digit = store_number % 10
            return f"10.{first_digit}.{second_digit}{vlan}.1"
        else:
            # Triple digit: 10.{first_digit}{second_digit}.{third_digit}{vlan}.1
            first_digit = store_number // 100
            second_digit = (store_number // 10) % 10
            third_digit = store_number % 10
            return f"10.{first_digit}{second_digit}.{third_digit}{vlan}.1"
    
    def add_store_with_vlans(self, store_number: int, site_id: str, site_name: str, 
                            address: str, lat: float, lng: float) -> bool:
        """Add a complete store with all VLAN configurations"""
        # Create site info
        site_info = SiteInfo(
            site_id=site_id,
            site_name=site_name,
            store_number=store_number,
            address=address,
            latitude=lat,
            longitude=lng
        )
        
        # Add site
        if not self.add_site(site_info):
            return False
        
        # Add VLAN configurations (10, 20, 30, 40, 50, 60, 70, 80, 90)
        for vlan_num in [10, 20, 30, 40, 50, 60, 70, 80, 90]:
            ip_address = self.generate_ip_for_store(store_number, vlan_num)
            
            vlan_config = VLANConfig(
                site_id=site_id,
                vlan_number=vlan_num,
                svi_name=f"vlan{vlan_num}_svi",
                ip_address=ip_address,
                netmask="255.255.255.0",
                gateway=ip_address
            )
            
            if not self.add_vlan_config(vlan_config):
                return False
        
        # Add switch IPs (based on VLAN 60)
        switch_base_ip = self.generate_ip_for_store(store_number, 60)
        switch_ip_parts = switch_base_ip.split('.')
        switch_ip_parts[3] = '30'  # First switch
        switch_ip1 = '.'.join(switch_ip_parts)
        switch_ip_parts[3] = '41'  # Second switch
        switch_ip2 = '.'.join(switch_ip_parts)
        
        self.add_switch_ip(site_id, switch_ip1)
        self.add_switch_ip(site_id, switch_ip2)
        
        # Add required services
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            for service in ['DNS', 'DHCP', 'RADIUS1']:
                cursor.execute("""
                    INSERT OR REPLACE INTO required_services (site_id, service_name)
                    VALUES (?, ?)
                """, (site_id, service))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Error adding services: {e}")
            return False
        finally:
            conn.close()
    
    def list_all_stores(self) -> List[Tuple[int, str]]:
        """List all stores with their numbers and names"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT store_number, site_name FROM sites 
                ORDER BY store_number
            """)
            
            return cursor.fetchall()
            
        finally:
            conn.close()
    
    def search_stores(self, search_term: str) -> List[Tuple[int, str]]:
        """Search stores by name or address"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT store_number, site_name FROM sites 
                WHERE site_name LIKE ? OR address LIKE ?
                ORDER BY store_number
            """, (f"%{search_term}%", f"%{search_term}%"))
            
            return cursor.fetchall()
            
        finally:
            conn.close()

def main():
    """Example usage"""
    db = NetworkDatabase()
    
    # List all stores
    stores = db.list_all_stores()
    print("All stores:")
    for store_num, store_name in stores:
        print(f"  Store {store_num}: {store_name}")
    
    # Get complete info for Store 25
    store_25_info = db.get_complete_site_info(25)
    if store_25_info:
        print(f"\nStore 25 info:")
        print(f"  Site: {store_25_info['site'].site_name}")
        print(f"  Address: {store_25_info['site'].address}")
        print(f"  VLANs: {len(store_25_info['vlans'])}")
        if store_25_info['network_management']:
            print(f"  Switch IPs: {store_25_info['network_management'].switch_ips}")

if __name__ == "__main__":
    main() 