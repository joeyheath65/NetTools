#!/usr/bin/env python3
"""
+======================================================================+
|                       NETWORK MONITOR                                |
|                   Real-Time Traffic Analyzer                         |
+======================================================================+

Author: Joe Heath
Email: joe@lawndart.dev, joseph.r.heath@gmail.com
GitHub: https://github.com/joeyheath65

Created: 2021-10-11
Version: 3.5

Description:
    Real-time network traffic monitoring tool that displays current
    upload/download speeds, total bandwidth usage, and network
    interface statistics with a professional dashboard interface.

Requirements:
    - Python 3.6+
    - psutil library (pip install psutil)

Usage:
    python network_monitor.py [options]
    Or you can just run it with no options and it will run on all interfaces.

Examples:
    python network_monitor.py --interface eth0
    python network_monitor.py --update-rate 0.5
    python network_monitor.py --log-traffic

License: MIT License
+======================================================================+
"""

import psutil
import time
import os
import sys
import argparse
import signal
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

class NetworkMonitor:
    """Real-time host machine network traffic monitoring class"""
    
    def __init__(self, interface: Optional[str] = None, update_delay: float = 1.0, 
                 log_enabled: bool = False, show_interfaces: bool = False):
        self.interface = interface
        self.update_delay = update_delay
        self.log_enabled = log_enabled
        self.show_interfaces = show_interfaces
        self.start_time = datetime.now()
        self.log_data = []
        self.peak_upload = 0
        self.peak_download = 0
        
        # Setup signal handler for clean exit
        signal.signal(signal.SIGINT, self.signal_handler)
        
    def signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        self.print_final_stats()
        sys.exit(0)
        
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('clear' if os.name != 'nt' else 'cls')
        
    def show_header(self):
        """Display main header"""
        print("""
+----------------------------------------------------------------------+
|                        NETWORK MONITOR                               |
|                   Real-Time Traffic Analyzer                         |
+----------------------------------------------------------------------+
| Author: Joe Heath - joseph.r.heath@gmail.com  |   Version 3.5        |
+----------------------------------------------------------------------+
        """)
        
    def print_status(self, message: str, status_type: str = "INFO"):
        """Print prettyformatted status messages"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        symbols = {
            "INFO": "ℹ",
            "SUCCESS": "✓",
            "WARNING": "⚠",
            "ERROR": "✗",
            "NETWORK": "🌐",
            "STATS": "📊"
        }
        symbol = symbols.get(status_type, "•")
        print(f"[{timestamp}] {symbol} {message}")
        
    def get_size(self, bytes_value: float) -> str:
        """Convert bytes to human readable format"""
        for unit in ['', 'K', 'M', 'G', 'T', 'P']:
            if bytes_value < 1024:
                return f"{bytes_value:.2f}{unit}B"
            bytes_value /= 1024
        return f"{bytes_value:.2f}EB"
        
    def get_available_interfaces(self) -> Dict[str, Dict]:
        """Get all available network interfaces from the host"""
        interfaces = {}
        try:
            stats = psutil.net_io_counters(pernic=True)
            for interface_name, stat in stats.items():
                interfaces[interface_name] = {
                    'bytes_sent': stat.bytes_sent,
                    'bytes_recv': stat.bytes_recv,
                    'packets_sent': stat.packets_sent,
                    'packets_recv': stat.packets_recv
                }
        except Exception as e:
            self.print_status(f"Error getting interfaces: {e}", "ERROR")
        return interfaces
        
    def display_interfaces(self):
        """Display available network interfaces"""
        interfaces = self.get_available_interfaces()
        if not interfaces:
            self.print_status("No network interfaces found", "ERROR")
            return
            
        print("\n" + "="*80)
        print("AVAILABLE NETWORK INTERFACES")
        print("="*80)
        print(f"{'Interface':<15} {'TX Bytes':<12} {'RX Bytes':<12} {'TX Packets':<12} {'RX Packets':<12}")
        print("-"*80)
        
        for name, stats in interfaces.items():
            print(f"{name:<15} {self.get_size(stats['bytes_sent']):<12} "
                  f"{self.get_size(stats['bytes_recv']):<12} "
                  f"{stats['packets_sent']:<12} {stats['packets_recv']:<12}")
        print("="*80)
        
    def get_network_stats(self) -> Optional[psutil._common.snetio]:
        """Get network I/O stats"""
        try:
            if self.interface:
                stats = psutil.net_io_counters(pernic=True)
                if self.interface in stats:
                    return stats[self.interface]
                else:
                    self.print_status(f"Interface '{self.interface}' not found", "ERROR")
                    return None
            else:
                return psutil.net_io_counters()
        except Exception as e:
            self.print_status(f"Error getting network stats: {e}", "ERROR")
            return None
            
    def calculate_speeds(self, current_stats, previous_stats) -> Tuple[float, float]:
        """Calculate upload and download"""
        upload_speed = (current_stats.bytes_sent - previous_stats.bytes_sent) / self.update_delay
        download_speed = (current_stats.bytes_recv - previous_stats.bytes_recv) / self.update_delay
        return upload_speed, download_speed
        
    def update_peaks(self, upload_speed: float, download_speed: float):
        """Update peak speed records"""
        if upload_speed > self.peak_upload:
            self.peak_upload = upload_speed
        if download_speed > self.peak_download:
            self.peak_download = download_speed
            
    def log_traffic_data(self, stats, upload_speed: float, download_speed: float):
        """Log traffic data for analysis"""
        if self.log_enabled:
            timestamp = datetime.now()
            log_entry = {
                'timestamp': timestamp,
                'total_sent': stats.bytes_sent,
                'total_recv': stats.bytes_recv,
                'upload_speed': upload_speed,
                'download_speed': download_speed
            }
            self.log_data.append(log_entry)
            
    def display_dashboard(self, stats, upload_speed: float, download_speed: float, 
                         session_sent: float, session_recv: float):
        """Display real-time dashboard"""
        current_time = datetime.now().strftime("%H:%M:%S")
        session_duration = datetime.now() - self.start_time
        
        # Create dashboard display
        dashboard = f"""
╔══════════════════════════════════════════════════════════════════════╗
║                      NETWORK TRAFFIC MONITOR                         ║
╠══════════════════════════════════════════════════════════════════════╣
║  Time: {current_time:<10}  │  Session: {str(session_duration).split('.')[0]:<10}  │   Interface: {self.interface or 'All':<8}   ║
╚══════════════════════════════════════════════════════════════════════╝
                           CURRENT SPEEDS                             
  ⬆️  Upload:   {self.get_size(upload_speed)}/s{'':<10}     ⬇️  Download: {self.get_size(download_speed)}/s{'':<10}   
╔══════════════════════════════════════════════════════════════════════╗
║                         SESSION TOTALS                               ║
║  📤 Sent:     {self.get_size(session_sent):<15}   │ 📥 Received: {self.get_size(session_recv):<20}  ║
║  🔺 Peak Up:  {self.get_size(self.peak_upload)}/s{'':<9}│ 🔻 Peak Down: {self.get_size(self.peak_download)}/s{'':<11} ║
╠══════════════════════════════════════════════════════════════════════╣
║                         LIFETIME TOTALS                              ║
║  📊 Total Sent:  {self.get_size(stats.bytes_sent):<15}|  📊 Total Received: {self.get_size(stats.bytes_recv):<15}║
╚══════════════════════════════════════════════════════════════════════╝
        """
        
        # Clear screen and display dashboard
        print("\033[2J\033[H", end="")  # Clear screen and move cursor to top
        print(dashboard)
        
        # Add progress bar for speeds
        max_speed = max(upload_speed, download_speed, 1)  # Avoid division by zero
        upload_bar = "█" * int((upload_speed / max_speed) * 20) if max_speed > 0 else ""
        download_bar = "█" * int((download_speed / max_speed) * 20) if max_speed > 0 else ""
        
        print(f"Upload   [{upload_bar:<20}] {self.get_size(upload_speed)}/s")
        print(f"Download [{download_bar:<20}] {self.get_size(download_speed)}/s")
        print("\nPress Ctrl+C to stop the madness...")
        
    def print_final_stats(self):
        """Print final statistics when exiting"""
        if not self.log_data:
            print("\n\nMonitoring session ended.")
            return
            
        session_duration = datetime.now() - self.start_time
        total_session_sent = sum(entry['upload_speed'] for entry in self.log_data) * self.update_delay
        total_session_recv = sum(entry['download_speed'] for entry in self.log_data) * self.update_delay
        
        avg_upload = sum(entry['upload_speed'] for entry in self.log_data) / len(self.log_data)
        avg_download = sum(entry['download_speed'] for entry in self.log_data) / len(self.log_data)
        
        final_stats = [
            f"Session Duration: {str(session_duration).split('.')[0]}",
            f"Data Sent: {self.get_size(total_session_sent)}",
            f"Data Received: {self.get_size(total_session_recv)}",
            f"Average Upload: {self.get_size(avg_upload)}/s",
            f"Average Download: {self.get_size(avg_download)}/s",
            f"Peak Upload: {self.get_size(self.peak_upload)}/s",
            f"Peak Download: {self.get_size(self.peak_download)}/s",
            f"Data Points Collected: {len(self.log_data)}"
        ]
        
        print("\n" + "="*60)
        print("SESSION SUMMARY".center(60))
        print("="*60)
        for stat in final_stats:
            print(f"  {stat}")
        print("="*60)
        
        if self.log_enabled:
            self.save_log_file()
            
    def save_log_file(self):
        """Save traffic log to file"""
        """Comment this out if you dont want to save the log file"""
        try:
            filename = f"network_traffic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            with open(filename, 'w') as f:
                f.write("Timestamp,Total_Sent,Total_Recv,Upload_Speed,Download_Speed\n")
                for entry in self.log_data:
                    f.write(f"{entry['timestamp']},{entry['total_sent']},{entry['total_recv']},"
                           f"{entry['upload_speed']},{entry['download_speed']}\n")
            self.print_status(f"Traffic log saved to {filename}", "SUCCESS")
        except Exception as e:
            self.print_status(f"Error saving log file: {e}", "ERROR")
            
    def run(self):
        """Main monitoring loop"""
        try:
            # Display interfaces if requested
            if self.show_interfaces:
                self.display_interfaces()
                return
                
            # Initialize
            self.clear_screen()
            self.show_header()
            
            # Get initial stats
            initial_stats = self.get_network_stats()
            if not initial_stats:
                return
                
            self.print_status(f"Starting network monitoring (Update rate: {self.update_delay}s)", "NETWORK")
            self.print_status(f"Interface: {self.interface or 'All interfaces'}", "INFO")
            if self.log_enabled:
                self.print_status("Traffic logging enabled", "INFO")
                
            time.sleep(2)  # Brief pause before starting
            
            # Store initial values for session tracking
            session_start_sent = initial_stats.bytes_sent
            session_start_recv = initial_stats.bytes_recv
            previous_stats = initial_stats
            
            # Main monitoring loop again
            while True:
                time.sleep(self.update_delay)
                
                # Get current stats
                current_stats = self.get_network_stats()
                if not current_stats:
                    continue
                    
                # Calculate speeds
                upload_speed, download_speed = self.calculate_speeds(current_stats, previous_stats)
                
                # Update peaks
                self.update_peaks(upload_speed, download_speed)
                
                # Calculate session totals
                session_sent = current_stats.bytes_sent - session_start_sent
                session_recv = current_stats.bytes_recv - session_start_recv
                
                # Log data
                self.log_traffic_data(current_stats, upload_speed, download_speed)
                
                # Display dashboard
                self.display_dashboard(current_stats, upload_speed, download_speed, 
                                     session_sent, session_recv)
                
                # Update for next iteration
                previous_stats = current_stats
                
        except KeyboardInterrupt:
            self.signal_handler(None, None)
        except Exception as e:
            self.print_status(f"Monitoring error: {e}", "ERROR")
            sys.exit(1)

def main():
    """Main function with argument parsing"""
    parser = argparse.ArgumentParser(
        description="Real-time network traffic monitoring tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python network_monitor.py                    # Monitor all interfaces
  python network_monitor.py -i eth0           # Monitor specific interface
  python network_monitor.py -r 0.5            # Update every 0.5 seconds
  python network_monitor.py --log-traffic     # Enable traffic logging
  python network_monitor.py --show-interfaces # List available interfaces
        """
    )
    
    parser.add_argument("-i", "--interface", type=str,
                       help="Specific network interface to monitor")
    parser.add_argument("-r", "--update-rate", type=float, default=1.0,
                       help="Update rate in seconds (default: 1.0)")
    parser.add_argument("--log-traffic", action="store_true",
                       help="Enable traffic data logging")
    parser.add_argument("--show-interfaces", action="store_true",
                       help="Show available network interfaces and exit")
    
    args = parser.parse_args()
    
    # Validate update rate
    if args.update_rate <= 0:
        print("Error: Update rate must be greater than 0")
        sys.exit(1)
        
    # Create and run monitor
    monitor = NetworkMonitor(
        interface=args.interface,
        update_delay=args.update_rate,
        log_enabled=args.log_traffic,
        show_interfaces=args.show_interfaces
    )
    
    monitor.run()

if __name__ == "__main__":
    main()