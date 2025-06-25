#!/usr/bin/env python3
"""
+======================================================================+
|                            SCANNERY                                  |
|                    Network Scanning & Discovery                      |
+======================================================================+

Author: Joe Heath
Email: joe@lawndart.dev, joseph.r.heath@gmail.com
GitHub: https://github.com/joeyheath65

Created: 2024-06-11
Version: 1.5

Description:
    Advanced network scanning tool with multiple scanning modes
    using nmap and netcat for network discovery.

Requirements:
    - Python 3.6+
    - nmap (sudo apt install nmap)
    - netcat (sudo apt install netcat)
    - You must have sudo privileges to run this!

License: MIT License
+======================================================================+
"""

import os
import sys
import time
import re
from datetime import datetime

def clear_screen():
    """Clear terminal screen"""
    os.system('clear' if os.name != 'nt' else 'cls')

def show_header():
    """Display main header"""
    print("""
+----------------------------------------------------------------------+
|                             SCANNERY                                 |
|                    Network Scanning & Discovery                      |
+----------------------------------------------------------------------+
| Author: Joe Heath - joseph.r.heath@gmail.com |   Version 1.5         |
+----------------------------------------------------------------------+
    """)

def show_menu():
    """Display main scanning menu"""
    print("""
╔═════════════════════════════════════════════════════════════════════╗
║                        SCANNING OPTIONS                             ║
╠═════════════════════════════════════════════════════════════════════╣
║  1.  Basic IP Scan & Fingerprinting                                 ║
║  2.  Specific Port Scan                                             ║
║  3.  IP Range Scan                                                  ║
║  4.  Top Popular Ports Scan                                         ║
║  5.  No DNS Resolution Scan                                         ║
║  6.  Service Version Detection                                      ║
║  7.  TCP Only Scan                                                  ║
║  8.  UDP Only Scan                                                  ║
║  9.  Vulnerability Scan (CVE Detection)                             ║
║ 10.  Aggressive Scan (Mike Tyson Style)                             ║
║                                                                     ║
║  0.  Exit                                                           ║
╚═════════════════════════════════════════════════════════════════════╝
    """)

def validate_ip(ip):
    """Validate IP address format"""
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if re.match(pattern, ip):
        octets = ip.split('.')
        return all(0 <= int(octet) <= 255 for octet in octets)
    return False

def validate_ip_range(ip_range):
    """Validate IP range format (CIDR notation - or slash notation for you nerds.)"""
    pattern = r'^(\d{1,3}\.){3}\d{1,3}/\d{1,2}$'
    if re.match(pattern, ip_range):
        ip, cidr = ip_range.split('/')
        return validate_ip(ip) and 0 <= int(cidr) <= 32
    return False

def validate_port(port):
    """Validate port number"""
    try:
        port_num = int(port)
        return 1 <= port_num <= 65535
    except ValueError:
        return False

def log_scan(scan_type, target, command):
    """Log scan activity"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {scan_type}: {target} - Command: {command}\n"
    
    try:
        with open("scannery.log", "a") as log_file:
            log_file.write(log_entry)
    except Exception as e:
        print(f"[WARNING] Could not write to log file: {e}")

def print_status(message, status_type="INFO"):
    """Print formatted status messages"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    symbols = {
        "INFO": "ℹ",
        "SUCCESS": "✓",
        "WARNING": "⚠",
        "ERROR": "✗",
        "SCANNING": "🔍"
    }
    symbol = symbols.get(status_type, "•")
    print(f"[{timestamp}] {symbol} {message}")

def get_target_ip():
    """Get and validate target IP from user"""
    while True:
        target_ip = input("\n🎯 Enter target IP address: ").strip()
        if validate_ip(target_ip):
            return target_ip
        print_status("Invalid IP address format. Please enter a valid IP (e.g., 192.168.1.1)", "ERROR")

def get_user_choice():
    """Get and validate user menu choice"""
    while True:
        try:
            choice = input("\n🔢 Select scanning option (0-10): ").strip()
            if choice == '0':
                return 0
            choice_num = int(choice)
            if 1 <= choice_num <= 10:
                return choice_num
            print_status("Please enter a number between 0-10", "ERROR")
        except ValueError:
            print_status("Please enter a valid number", "ERROR")

def execute_scan(command, scan_type, target):
    """Execute scan command with logging"""
    print_status(f"Starting {scan_type} scan on {target}", "SCANNING")
    print_status(f"Command: {command}", "INFO")
    print("-" * 70)
    
    log_scan(scan_type, target, command)
    
    try:
        os.system(command)
        print("-" * 70)
        print_status(f"{scan_type} scan completed", "SUCCESS")
    except Exception as e:
        print_status(f"Scan failed: {e}", "ERROR")

def run_scannery():
    """Main scanning function"""
    clear_screen()
    show_header()
    
    # Get target IP
    target_ip = get_target_ip()
    
    # Show menu and get choice
    show_menu()
    choice = get_user_choice()
    
    if choice == 0:
        print_status("Exiting SCANNERY. Goodbye!", "INFO")
        return False
    
    print_status("Preparing scan...", "INFO")
    time.sleep(1)
    
    # Execute based on choice
    if choice == 1:
        # Basic IP scan & fingerprinting
        command = f"sudo nmap -sS -O {target_ip}"
        execute_scan(command, "Basic Scan", target_ip)
        
    elif choice == 2:
        # Specific port scan
        while True:
            port = input("\n🔌 Enter port number to scan: ").strip()
            if validate_port(port):
                break
            print_status("Invalid port number. Enter a port between 1-65535", "ERROR")
        
        command = f"sudo nmap -p {port} {target_ip}"
        execute_scan(command, f"Port {port} Scan", target_ip)
        
    elif choice == 3:
        # IP range scan
        while True:
            ip_range = input("\n🌐 Enter IP range (CIDR notation, e.g., 192.168.1.0/24): ").strip()
            if validate_ip_range(ip_range):
                break
            print_status("Invalid IP range format. Use CIDR notation (e.g., 192.168.1.0/24)", "ERROR")
        
        command = f"sudo nmap {ip_range}"
        execute_scan(command, "Range Scan", ip_range)
        
    elif choice == 4:
        # common ports
        while True:
            try:
                num_ports = int(input("\n🔝 Enter number of top ports to scan: ").strip())
                if 1 <= num_ports <= 65535:
                    break
                print_status("Enter a number between 1-65535", "ERROR")
            except ValueError:
                print_status("Please enter a valid number", "ERROR")
        
        command = f"sudo nmap --top-ports {num_ports} {target_ip}"
        execute_scan(command, f"Top {num_ports} Ports Scan", target_ip)
        
    elif choice == 5:
        # No DNS resolution
        command = f"sudo nmap -n {target_ip}"
        execute_scan(command, "No DNS Scan", target_ip)
        
    elif choice == 6:
        # Service version detection
        command = f"sudo nmap -sV {target_ip}"
        execute_scan(command, "Service Detection", target_ip)
        
    elif choice == 7:
        # TCP only scan
        command = f"sudo nmap -sT {target_ip}"
        execute_scan(command, "TCP Scan", target_ip)
        
    elif choice == 8:
        # UDP only scan
        print_status("UDP scans may take longer to complete", "WARNING")
        command = f"sudo nmap -sU --top-ports 1000 {target_ip}"
        execute_scan(command, "UDP Scan", target_ip)
        
    elif choice == 9:
        # Vulnerability scan
        print_status("Vulnerability scan may take several minutes", "WARNING")
        command = f"sudo nmap -Pn --script vuln {target_ip}"
        execute_scan(command, "Vulnerability Scan", target_ip)
        
    elif choice == 10:
        # Aggressive scan (Mike Tyson style)
        print_status("AGGRESSIVE SCAN MODE ACTIVATED! 🥊", "WARNING")
        print_status("This scan is pretty intense and may take a while", "WARNING")
        command = f"sudo nmap -A -T4 -Pn {target_ip}"
        execute_scan(command, "Aggressive Scan", target_ip)
    
    # Ask to continue
    print("\n" + "="*70)
    while True:
        continue_choice = input("🔄 Scan another? (y/n): ").lower().strip()
        if continue_choice in ['y', 'yes']:
            return True
        elif continue_choice in ['n', 'no']:
            return False
        print_status("Please enter 'y' or 'n'", "ERROR")

def main():
    """Main scannery function"""
    try:
        # Check if running on linux or mac
        if os.name == 'nt':
            print_status("This tool is designed for linux and macsystems", "WARNING")
            
        # Check for nmap
        if os.system("which nmap > /dev/null 2>&1") != 0:
            print_status("nmap is not installed. Please install it first:", "ERROR")
            sys.exit(1)
        
        # Main loop
        while True:
            if not run_scannery():
                break
                
        print_status("Thank you for using SCANNERY! 🎯", "SUCCESS")
        
    except KeyboardInterrupt:
        print_status("\n\nScan interrupted by you. Exiting...wimp...", "WARNING")
        sys.exit(0)
    except Exception as e:
        print_status(f"Unexpected error: {e}", "ERROR")
        sys.exit(1)

if __name__ == "__main__":
    main()