#!/usr/bin/env python3
"""
+======================================================================+
|                      SYSTEM INFO SCANNER                            |
|                 Comprehensive Network Information                    |
+======================================================================+

Author: Joe Heath
Email: joe@joeheath.com
GitHub: https://github.com/joeheath
Location: Floresville, TX

Created: 2025-06-27
Version: 1.0

Description:
    Comprehensive system network information scanner that gathers
    IP configuration, WLAN details, signal strength (RSSI), interface
    statistics, routing tables, DNS configuration, and system info.

Requirements:
    - Python 3.6+
    - psutil library (pip install psutil)
    - iwconfig/iwlist (Linux wireless tools)
    - Root/sudo privileges for some wireless info

Usage:
    python system_scanner.py [options]

Examples:
    python system_scanner.py --full-scan
    python system_scanner.py --export-json
    python system_scanner.py --interface wlan0

License: MIT License
+======================================================================+
"""

import psutil
import socket
import subprocess
import platform
import os
import sys
import json
import argparse
import time
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
import ipaddress

class SystemInfoScanner:
    """Comprehensive system and network information scanner"""
    
    def __init__(self, interface: Optional[str] = None, full_scan: bool = False, 
                 export_format: Optional[str] = None):
        self.interface = interface
        self.full_scan = full_scan
        self.export_format = export_format
        self.scan_data = {}
        self.scan_time = datetime.now()
        
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('clear' if os.name != 'nt' else 'cls')
        
    def show_header(self):
        """Display main header"""
        print("""
+----------------------------------------------------------------------+
|                      SYSTEM INFO SCANNER                            |
|                 Comprehensive Network Information                    |
+----------------------------------------------------------------------+
| Author: Joe [Your Last Name] | Floresville, TX | Version 1.0        |
+----------------------------------------------------------------------+
        """)
        
    def print_status(self, message: str, status_type: str = "INFO"):
        """Print formatted status messages"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        symbols = {
            "INFO": "ℹ",
            "SUCCESS": "✓",
            "WARNING": "⚠",
            "ERROR": "✗",
            "SCANNING": "🔍",
            "NETWORK": "🌐",
            "WIRELESS": "📶",
            "SYSTEM": "💻"
        }
        symbol = symbols.get(status_type, "•")
        print(f"[{timestamp}] {symbol} {message}")
        
    def show_section_header(self, title: str):
        """Display section header"""
        print(f"\n╔{'═' * (len(title) + 4)}╗")
        print(f"║ {title.upper()} ║")
        print(f"╚{'═' * (len(title) + 4)}╝")
        
    def run_command(self, cmd: List[str], timeout: int = 10) -> Optional[str]:
        """Run system command and return output"""
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, 
                                  timeout=timeout, check=False)
            return result.stdout.strip() if result.returncode == 0 else None
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return None
            
    def get_system_info(self) -> Dict[str, Any]:
        """Get basic system information"""
        self.print_status("Gathering system information", "SYSTEM")
        
        system_info = {
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
            "system": platform.system(),
            "processor": platform.processor(),
            "architecture": platform.architecture(),
            "python_version": platform.python_version(),
            "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat(),
            "uptime": str(datetime.now() - datetime.fromtimestamp(psutil.boot_time())).split('.')[0]
        }
        
        # CPU and Memory info
        system_info.update({
            "cpu_count": psutil.cpu_count(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_total": psutil.virtual_memory().total,
            "memory_available": psutil.virtual_memory().available,
            "memory_percent": psutil.virtual_memory().percent
        })
        
        return system_info
        
    def get_network_interfaces(self) -> Dict[str, Any]:
        """Get detailed network interface information"""
        self.print_status("Scanning network interfaces", "NETWORK")
        
        interfaces = {}
        
        # Get interface addresses
        for interface_name, addresses in psutil.net_if_addrs().items():
            interface_info = {
                "addresses": [],
                "stats": None,
                "is_up": False
            }
            
            # Process addresses
            for addr in addresses:
                addr_info = {
                    "family": str(addr.family),
                    "address": addr.address,
                    "netmask": addr.netmask,
                    "broadcast": addr.broadcast
                }
                interface_info["addresses"].append(addr_info)
                
            # Get interface statistics
            try:
                stats = psutil.net_if_stats()[interface_name]
                interface_info["stats"] = {
                    "is_up": stats.isup,
                    "duplex": str(stats.duplex),
                    "speed": stats.speed,
                    "mtu": stats.mtu
                }
                interface_info["is_up"] = stats.isup
            except KeyError:
                pass
                
            # Get I/O counters
            try:
                io_counters = psutil.net_io_counters(pernic=True)[interface_name]
                interface_info["io_counters"] = {
                    "bytes_sent": io_counters.bytes_sent,
                    "bytes_recv": io_counters.bytes_recv,
                    "packets_sent": io_counters.packets_sent,
                    "packets_recv": io_counters.packets_recv,
                    "errin": io_counters.errin,
                    "errout": io_counters.errout,
                    "dropin": io_counters.dropin,
                    "dropout": io_counters.dropout
                }
            except KeyError:
                pass
                
            interfaces[interface_name] = interface_info
            
        return interfaces
        
    def get_wireless_info(self) -> Dict[str, Any]:
        """Get detailed wireless information"""
        self.print_status("Gathering wireless information", "WIRELESS")
        
        wireless_info = {}
        
        # Try to get wireless interfaces
        wireless_interfaces = []
        
        # Check for wireless interfaces using iwconfig
        iwconfig_output = self.run_command(["iwconfig"])
        if iwconfig_output:
            for line in iwconfig_output.split('\n'):
                if 'IEEE 802.11' in line or 'ESSID:' in line:
                    interface = line.split()[0]
                    if interface and interface not in wireless_interfaces:
                        wireless_interfaces.append(interface)
                        
        # Get detailed info for each wireless interface
        for interface in wireless_interfaces:
            interface_info = self.get_wireless_interface_details(interface)
            if interface_info:
                wireless_info[interface] = interface_info
                
        return wireless_info
        
    def get_wireless_interface_details(self, interface: str) -> Optional[Dict[str, Any]]:
        """Get detailed information for a specific wireless interface"""
        interface_info = {}
        
        # Get iwconfig information
        iwconfig_output = self.run_command(["iwconfig", interface])
        if iwconfig_output:
            interface_info.update(self.parse_iwconfig(iwconfig_output))
            
        # Get iwlist scan information
        iwlist_output = self.run_command(["iwlist", interface, "scan"])
        if iwlist_output:
            interface_info["scan_results"] = self.parse_iwlist_scan(iwlist_output)
            
        # Get signal information
        signal_info = self.get_signal_strength(interface)
        if signal_info:
            interface_info.update(signal_info)
            
        return interface_info if interface_info else None
        
    def parse_iwconfig(self, output: str) -> Dict[str, Any]:
        """Parse iwconfig output"""
        info = {}
        
        # Extract ESSID
        essid_match = re.search(r'ESSID:"([^"]*)"', output)
        if essid_match:
            info["essid"] = essid_match.group(1)
            
        # Extract Access Point MAC
        ap_match = re.search(r'Access Point: ([A-Fa-f0-9:]{17})', output)
        if ap_match:
            info["access_point"] = ap_match.group(1)
            
        # Extract Frequency
        freq_match = re.search(r'Frequency:([0-9.]+) GHz', output)
        if freq_match:
            info["frequency"] = f"{freq_match.group(1)} GHz"
            
        # Extract Bit Rate
        rate_match = re.search(r'Bit Rate=([0-9.]+) Mb/s', output)
        if rate_match:
            info["bit_rate"] = f"{rate_match.group(1)} Mb/s"
            
        # Extract Signal Level
        signal_match = re.search(r'Signal level=(-?[0-9]+) dBm', output)
        if signal_match:
            info["signal_level"] = f"{signal_match.group(1)} dBm"
            
        # Extract Link Quality
        quality_match = re.search(r'Link Quality=([0-9]+/[0-9]+)', output)
        if quality_match:
            info["link_quality"] = quality_match.group(1)
            
        return info
        
    def parse_iwlist_scan(self, output: str) -> List[Dict[str, Any]]:
        """Parse iwlist scan output"""
        networks = []
        current_network = {}
        
        for line in output.split('\n'):
            line = line.strip()
            
            # New cell (network)
            if line.startswith('Cell'):
                if current_network:
                    networks.append(current_network)
                current_network = {}
                
                # Extract MAC address
                mac_match = re.search(r'Address: ([A-Fa-f0-9:]{17})', line)
                if mac_match:
                    current_network["mac_address"] = mac_match.group(1)
                    
            elif 'ESSID:' in line:
                essid_match = re.search(r'ESSID:"([^"]*)"', line)
                if essid_match:
                    current_network["essid"] = essid_match.group(1)
                    
            elif 'Signal level=' in line:
                signal_match = re.search(r'Signal level=(-?[0-9]+) dBm', line)
                if signal_match:
                    current_network["signal_level"] = f"{signal_match.group(1)} dBm"
                    
            elif 'Frequency:' in line:
                freq_match = re.search(r'Frequency:([0-9.]+) GHz', line)
                if freq_match:
                    current_network["frequency"] = f"{freq_match.group(1)} GHz"
                    
            elif 'Encryption key:' in line:
                current_network["encryption"] = "on" if "on" in line else "off"
                
        # Add the last network
        if current_network:
            networks.append(current_network)
            
        return networks
        
    def get_signal_strength(self, interface: str) -> Optional[Dict[str, Any]]:
        """Get current signal strength information"""
        # Try different methods to get signal strength
        
        # Method 1: /proc/net/wireless
        try:
            with open('/proc/net/wireless', 'r') as f:
                lines = f.readlines()
                for line in lines:
                    if interface in line:
                        parts = line.split()
                        if len(parts) >= 4:
                            return {
                                "link_quality": parts[2],
                                "signal_level_raw": parts[3],
                                "noise_level": parts[4] if len(parts) > 4 else "N/A"
                            }
        except (FileNotFoundError, PermissionError):
            pass
            
        # Method 2: iw command
        iw_output = self.run_command(["iw", interface, "link"])
        if iw_output:
            signal_match = re.search(r'signal: (-?[0-9]+) dBm', iw_output)
            if signal_match:
                return {"signal_dbm": f"{signal_match.group(1)} dBm"}
                
        return None
        
    def get_routing_table(self) -> List[Dict[str, Any]]:
        """Get system routing table"""
        self.print_status("Reading routing table", "NETWORK")
        
        routes = []
        
        # Try netstat first
        netstat_output = self.run_command(["netstat", "-rn"])
        if netstat_output:
            routes.extend(self.parse_netstat_routes(netstat_output))
            
        # Try ip route as fallback
        if not routes:
            ip_output = self.run_command(["ip", "route"])
            if ip_output:
                routes.extend(self.parse_ip_routes(ip_output))
                
        return routes
        
    def parse_netstat_routes(self, output: str) -> List[Dict[str, Any]]:
        """Parse netstat routing output"""
        routes = []
        lines = output.split('\n')
        
        for line in lines:
            if re.match(r'^[0-9]', line):  # Routes start with numbers
                parts = line.split()
                if len(parts) >= 6:
                    routes.append({
                        "destination": parts[0],
                        "gateway": parts[1],
                        "flags": parts[2],
                        "refs": parts[3],
                        "use": parts[4],
                        "interface": parts[5]
                    })
                    
        return routes
        
    def parse_ip_routes(self, output: str) -> List[Dict[str, Any]]:
        """Parse ip route output"""
        routes = []
        
        for line in output.split('\n'):
            if line.strip():
                routes.append({"route": line.strip()})
                
        return routes
        
    def get_dns_info(self) -> Dict[str, Any]:
        """Get DNS configuration"""
        self.print_status("Gathering DNS configuration", "NETWORK")
        
        dns_info = {
            "nameservers": [],
            "search_domains": [],
            "resolv_conf": None
        }
        
        # Read /etc/resolv.conf
        try:
            with open('/etc/resolv.conf', 'r') as f:
                resolv_content = f.read()
                dns_info["resolv_conf"] = resolv_content
                
                for line in resolv_content.split('\n'):
                    line = line.strip()
                    if line.startswith('nameserver'):
                        dns_info["nameservers"].append(line.split()[1])
                    elif line.startswith('search'):
                        dns_info["search_domains"].extend(line.split()[1:])
                        
        except (FileNotFoundError, PermissionError):
            pass
            
        # Get system DNS (alternative method)
        try:
            import socket
            dns_info["system_dns"] = socket.getaddrinfo("google.com", 80)[0][4][0]
        except:
            pass
            
        return dns_info
        
    def get_connections(self) -> List[Dict[str, Any]]:
        """Get active network connections"""
        if not self.full_scan:
            return []
            
        self.print_status("Scanning active connections", "NETWORK")
        
        connections = []
        
        try:
            for conn in psutil.net_connections(kind='inet'):
                conn_info = {
                    "family": str(conn.family),
                    "type": str(conn.type),
                    "local_address": f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                    "remote_address": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                    "status": conn.status,
                    "pid": conn.pid
                }
                
                # Get process name if available
                if conn.pid:
                    try:
                        process = psutil.Process(conn.pid)
                        conn_info["process_name"] = process.name()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                        
                connections.append(conn_info)
                
        except psutil.AccessDenied:
            self.print_status("Permission denied for connection info (try running as root)", "WARNING")
            
        return connections
        
    def display_results(self):
        """Display comprehensive scan results"""
        
        # System Information
        self.show_section_header("System Information")
        system_info = self.scan_data.get("system_info", {})
        
        print(f"🖥️  Hostname: {system_info.get('hostname', 'Unknown')}")
        print(f"💻 Platform: {system_info.get('platform', 'Unknown')}")
        print(f"🏗️  Architecture: {' '.join(system_info.get('architecture', ['Unknown']))}")
        print(f"⏱️  Uptime: {system_info.get('uptime', 'Unknown')}")
        print(f"🧠 CPU: {system_info.get('cpu_count', 'Unknown')} cores @ {system_info.get('cpu_percent', 'Unknown')}%")
        print(f"💾 Memory: {system_info.get('memory_percent', 'Unknown')}% used")
        
        # Network Interfaces
        self.show_section_header("Network Interfaces")
        interfaces = self.scan_data.get("network_interfaces", {})
        
        for name, info in interfaces.items():
            print(f"\n📶 Interface: {name}")
            print(f"   Status: {'🟢 UP' if info.get('is_up') else '🔴 DOWN'}")
            
            # Display addresses
            for addr in info.get("addresses", []):
                if addr["address"] and not addr["address"].startswith("::"):
                    family = "IPv4" if "." in addr["address"] else "IPv6"
                    print(f"   {family}: {addr['address']}")
                    if addr.get("netmask"):
                        print(f"   Netmask: {addr['netmask']}")
                        
            # Display stats
            stats = info.get("stats", {})
            if stats:
                print(f"   Speed: {stats.get('speed', 'Unknown')} Mbps")
                print(f"   MTU: {stats.get('mtu', 'Unknown')}")
                
            # Display I/O counters
            io = info.get("io_counters", {})
            if io:
                print(f"   TX: {self.format_bytes(io.get('bytes_sent', 0))} "
                      f"({io.get('packets_sent', 0)} packets)")
                print(f"   RX: {self.format_bytes(io.get('bytes_recv', 0))} "
                      f"({io.get('packets_recv', 0)} packets)")
                      
        # Wireless Information
        wireless_info = self.scan_data.get("wireless_info", {})
        if wireless_info:
            self.show_section_header("Wireless Information")
            
            for interface, info in wireless_info.items():
                print(f"\n📡 Wireless Interface: {interface}")
                
                if info.get("essid"):
                    print(f"   📶 Connected to: {info['essid']}")
                if info.get("access_point"):
                    print(f"   🎯 Access Point: {info['access_point']}")
                if info.get("frequency"):
                    print(f"   📻 Frequency: {info['frequency']}")
                if info.get("signal_level"):
                    print(f"   📊 Signal Level: {info['signal_level']}")
                if info.get("link_quality"):
                    print(f"   🔗 Link Quality: {info['link_quality']}")
                if info.get("bit_rate"):
                    print(f"   ⚡ Bit Rate: {info['bit_rate']}")
                    
                # Show scan results
                scan_results = info.get("scan_results", [])
                if scan_results:
                    print(f"\n   📋 Available Networks ({len(scan_results)} found):")
                    for i, network in enumerate(scan_results[:5], 1):  # Show top 5
                        essid = network.get("essid", "Hidden")
                        signal = network.get("signal_level", "Unknown")
                        encryption = "🔒" if network.get("encryption") == "on" else "🔓"
                        print(f"      {i}. {encryption} {essid} ({signal})")
                        
        # DNS Information
        dns_info = self.scan_data.get("dns_info", {})
        if dns_info:
            self.show_section_header("DNS Configuration")
            
            nameservers = dns_info.get("nameservers", [])
            if nameservers:
                print("🌐 DNS Servers:")
                for ns in nameservers:
                    print(f"   • {ns}")
                    
            search_domains = dns_info.get("search_domains", [])
            if search_domains:
                print("🔍 Search Domains:")
                for domain in search_domains:
                    print(f"   • {domain}")
                    
        # Routing Table
        routes = self.scan_data.get("routing_table", [])
        if routes:
            self.show_section_header("Routing Table")
            
            print("🛤️  Routes (Top 10):")
            for i, route in enumerate(routes[:10], 1):
                if isinstance(route, dict) and "destination" in route:
                    print(f"   {i}. {route['destination']} via {route.get('gateway', 'N/A')} "
                          f"({route.get('interface', 'N/A')})")
                else:
                    print(f"   {i}. {route.get('route', 'Unknown route')}")
                    
        # Active Connections (if full scan)
        connections = self.scan_data.get("connections", [])
        if connections:
            self.show_section_header("Active Connections")
            
            print(f"🔗 Active connections ({len(connections)} total, showing first 10):")
            for i, conn in enumerate(connections[:10], 1):
                local = conn.get("local_address", "N/A")
                remote = conn.get("remote_address", "N/A")
                status = conn.get("status", "N/A")
                process = conn.get("process_name", "N/A")
                print(f"   {i}. {local} → {remote} [{status}] ({process})")
                
    def format_bytes(self, bytes_value: int) -> str:
        """Format bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024
        return f"{bytes_value:.1f} PB"
        
    def export_data(self):
        """Export scan data to file"""
        if not self.export_format:
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if self.export_format.lower() == "json":
            filename = f"system_scan_{timestamp}.json"
            try:
                with open(filename, 'w') as f:
                    json.dump(self.scan_data, f, indent=2, default=str)
                self.print_status(f"Data exported to {filename}", "SUCCESS")
            except Exception as e:
                self.print_status(f"Export failed: {e}", "ERROR")
                
        elif self.export_format.lower() == "txt":
            filename = f"system_scan_{timestamp}.txt"
            try:
                with open(filename, 'w') as f:
                    f.write(f"System Scan Report - {self.scan_time}\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(json.dumps(self.scan_data, indent=2, default=str))
                self.print_status(f"Data exported to {filename}", "SUCCESS")
            except Exception as e:
                self.print_status(f"Export failed: {e}", "ERROR")
                
    def run_scan(self):
        """Execute comprehensive system scan"""
        try:
            self.clear_screen()
            self.show_header()
            
            self.print_status("Starting comprehensive system scan", "SCANNING")
            print()
            
            # Gather all information
            self.scan_data["scan_time"] = self.scan_time.isoformat()
            self.scan_data["system_info"] = self.get_system_info()
            self.scan_data["network_interfaces"] = self.get_network_interfaces()
            self.scan_data["wireless_info"] = self.get_wireless_info()
            self.scan_data["dns_info"] = self.get_dns_info()
            self.scan_data["routing_table"] = self.get_routing_table()
            
            if self.full_scan:
                self.scan_data["connections"] = self.get_connections()
                
            # Display results
            print("\n" + "="*80)
            self.print_status("Scan completed! Displaying results:", "SUCCESS")
            print("="*80)
            
            self.display_results()
            
            # Export if requested
            if self.export_format:
                print("\n" + "="*80)
                self.export_data()
                
        except KeyboardInterrupt:
            self.print_status("\nScan interrupted by user", "WARNING")
            sys.exit(0)
        except Exception as e:
            self.print_status(f"Scan failed: {e}", "ERROR")
            sys.exit(1)

def main():
    """Main function with argument parsing"""
    parser = argparse.ArgumentParser(
        description="Comprehensive system and network information scanner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python system_scanner.py                    # Basic scan
  python system_scanner.py --full-scan        # Include active connections
  python system_scanner.py --export-json      # Export results to JSON
  python system_scanner.py --interface wlan0  # Focus on specific interface
        """
    )
    
    parser.add_argument("-i", "--interface", type=str,
                       help="Focus on specific network interface")
    parser.add_argument("--full-scan", action="store_true",
                       help="Include active connections and detailed analysis")
    parser.add_argument("--export-json", action="store_const", const="json",
                       dest="export_format", help="Export results to JSON file")
    parser.add_argument("--export-txt", action="store_const", const="txt",
                       dest="export_format", help="Export results to text file")
    
    args = parser.parse_args()
    
    # Check for required tools
    required_tools = ["iwconfig", "iwlist", "netstat"]
    missing_tools = []
    
    for tool in required_tools:
        if not subprocess.run(["which", tool], capture_output=True).returncode == 0:
            missing_tools.append(tool)
            
    if missing_tools:
        print(f"⚠️  Warning: Missing tools: {', '.join(missing_tools)}")
        print("   Some wireless information may not be available.")
        print("   Install with: sudo apt install wireless-tools net-tools")
        print()
        
    # Create and run scanner
    scanner = SystemInfoScanner(
        interface=args.interface,
        full_scan=args.full_scan,
        export_format=args.export_format
    )
    
    scanner.run_scan()

if __name__ == "__main__":
    main()