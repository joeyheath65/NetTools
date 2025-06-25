#!/usr/bin/env python3
"""
+======================================================================+
|                         ZSCALER CHECKER                             |
|                   Network Path & Proxy Detection                    |
+======================================================================+

Author: Joe Heath
Email: joe@lawndart.dev, joseph.r.heath@gmail.com
GitHub: https://github.com/joeyheath65

Created: 2025-06-24
Version: 1.0

Description:
    Advanced network path analyzer to detect Zscaler proxy presence
    and trace network routes. Performs traceroute analysis with
    Zscaler endpoint detection and latency measurement.

Requirements:
    - Python 3.6+
    - requests library (pip install requests)
    - traceroute (Linux/Mac) or tracert (Windows)
    - The interwebs (internet) connectivity

Usage:
    python zscaler_checker.py [target_host]
    python zscaler_checker.py --help

Examples:
    python zscaler_checker.py google.com
    python zscaler_checker.py 8.8.8.8 --timeout 30

License: MIT License
+======================================================================+
"""

import argparse
import requests
import socket
import subprocess
import sys
import re
import time
from typing import List, Optional, Tuple
import ipaddress
from datetime import datetime

# Static Zscaler IP ranges (update as needed from Zscaler documentation)
ZSCALER_IP_RANGES = [
    "185.46.212.0/22", "185.46.212.0/23", "185.46.214.0/23", "104.129.192.0/20",
    "165.225.0.0/16", "199.168.148.0/22", "199.168.152.0/21", "199.168.156.0/22",
    "199.168.160.0/21", "199.168.164.0/22", "199.168.168.0/21", "199.168.172.0/22",
    "199.168.176.0/21", "199.168.180.0/22", "199.168.184.0/21", "199.168.188.0/22",
    "199.168.192.0/21", "199.168.196.0/22", "199.168.200.0/21", "199.168.204.0/22",
    "199.168.208.0/21", "199.168.212.0/22", "199.168.216.0/21", "199.168.220.0/22",
    "199.168.224.0/21", "199.168.228.0/22", "199.168.232.0/21", "199.168.236.0/22",
    "199.168.240.0/21", "199.168.244.0/22", "199.168.248.0/21", "199.168.252.0/22",
]

ZSCALER_HOST_PATTERNS = [
    r"zscaler[0-9]*[.-]", r"zscloud[0-9]*[.-]", r"zscalertwo[.-]", r"zscalerthree[.-]"
]

def clear_screen():
    """Clear terminal screen"""
    import os
    os.system('clear' if os.name != 'nt' else 'cls')

def show_header():
    """Display main header"""
    print("""
+----------------------------------------------------------------------+
|                         ZSCALER CHECKER                              |
|                   Network Path & Proxy Detection                     |
+----------------------------------------------------------------------+
| Author: Joe Heath - joseph.r.heath@gmail.com |   Version 1.0         |
+----------------------------------------------------------------------+
    """)

def print_status(message, status_type="INFO"):
    """Print formatted status messages"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    symbols = {
        "INFO": "ℹ",
        "SUCCESS": "✓",
        "WARNING": "⚠",
        "ERROR": "✗",
        "CHECKING": "🔍",
        "ZSCALER": "🛡",
        "NETWORK": "🌐",
        "PATH": "🛤"
    }
    symbol = symbols.get(status_type, "•")
    print(f"[{timestamp}] {symbol} {message}")

def show_summary_box(title, content_lines):
    """Display information in a prettyformatted box"""
    max_width = max(len(line) for line in content_lines + [title]) + 4
    max_width = max(max_width, 60)
    
    print("+" + "="*(max_width-2) + "+")
    print(f"|{title.center(max_width-2)}|")
    print("+" + "-"*(max_width-2) + "+")
    for line in content_lines:
        print(f"| {line.ljust(max_width-4)} |")
    print("+" + "="*(max_width-2) + "+")

def is_zscaler_ip(ip: str) -> bool:
    """
    Checks if an IP address is within known Zscaler IP ranges (updated June 2025).
    """
    try:
        ip_obj = ipaddress.ip_address(ip)
        for net in ZSCALER_IP_RANGES:
            if ip_obj in ipaddress.ip_network(net):
                return True
    except Exception:
        pass
    return False

def is_zscaler_host(host: str) -> bool:
    """
    Checks if a hostname matches known Zscaler patterns.
    """
    for pat in ZSCALER_HOST_PATTERNS:
        if re.search(pat, host, re.IGNORECASE):
            return True
    return False

def get_public_ip_and_zscaler_info() -> dict:
    """
    Checks https://ip.zscaler.com/ to determine if the client is behind Zscaler.
    """
    url = "https://ip.zscaler.com/"
    print_status("Querying Zscaler detection service...", "CHECKING")
    
    try:
        resp = requests.get(url, timeout=10)
        text = resp.text
        zscaler_present = "Zscaler" in text or "zscaler" in text
        
        # Try to extract Gateway IP and other info
        gateway_ip = None
        m = re.search(r"Gateway IP Address is most likely ([0-9.]+)", text)
        if m:
            gateway_ip = m.group(1)
            
        # Extract public IP
        m2 = re.search(r"from the IP address ([0-9.]+)", text)
        public_ip = m2.group(1) if m2 else None
        
        if not gateway_ip or not public_ip:
            print_status("Could not extract complete Zscaler info from response", "WARNING")
            print("\n--- RAW RESPONSE SAMPLE ---")
            print(text[:300] + "..." if len(text) > 300 else text)
            print("--- END SAMPLE ---\n")
            
        return {
            "zscaler": zscaler_present,
            "gateway_ip": gateway_ip,
            "public_ip": public_ip,
            "headers": dict(resp.headers),
            "raw": text
        }
    except Exception as e:
        print_status(f"Failed to check Zscaler service: {e}", "ERROR")
        return {"error": str(e)}

def traceroute_path(target: str, max_hops: int = 30, timeout: int = 60) -> List[Tuple[str, Optional[float], Optional[str]]]:
    """
    Runs traceroute to the target and returns hop information. I havent tested this on windows yet, I'm guessing it will work.
    """
    is_windows = sys.platform.startswith("win")
    cmd = ["tracert", "-d", "-h", str(max_hops), target] if is_windows else ["traceroute", "-n", "-m", str(max_hops), target]
    
    print_status(f"Starting traceroute to {target} (max {max_hops} hops, {timeout}s timeout)", "PATH")
    print_status(f"Command: {' '.join(cmd)}", "INFO")
    
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        output = proc.stdout
        hops = []
        
        print_status("Parsing traceroute output...", "CHECKING")
        
        for line_num, line in enumerate(output.splitlines(), 1):
            try:
                # Match traceroute output
                m = re.match(r"\s*(\d+)\s+([0-9.]+)\s+(.+)", line)
                if m:
                    hop_num = int(m.group(1))
                    ip = m.group(2)
                    rest = m.group(3)
                    
                    # Get the latency
                    lat_m = re.search(r"(\d+\.?\d*)\s*ms", rest)
                    latency = float(lat_m.group(1)) if lat_m else None
                    
                    hops.append((ip, latency, None))
                    
            except Exception as e:
                continue
                
        print_status(f"Parsed {len(hops)} network hops", "SUCCESS")
        return hops
        
    except subprocess.TimeoutExpired as e:
        print_status(f"Traceroute timed out after {timeout} seconds", "WARNING")
        
        # Try to parse partial results
        hops = []
        if e.stdout:
            raw_output = e.stdout.decode('utf-8', errors='replace') if isinstance(e.stdout, bytes) else e.stdout
            print_status("Attempting to parse partial results...", "INFO")
            
            for line in raw_output.splitlines():
                try:
                    m = re.match(r"\s*(\d+)\s+([0-9.]+)\s+(.+)", line)
                    if m:
                        ip = m.group(2)
                        rest = m.group(3)
                        lat_m = re.search(r"(\d+\.?\d*)\s*ms", rest)
                        latency = float(lat_m.group(1)) if lat_m else None
                        hops.append((ip, latency, None))
                except Exception:
                    continue
                    
        if hops:
            print_status(f"Retrieved {len(hops)} partial hops before timeout", "WARNING")
        
        return hops
        
    except Exception as e:
        print_status(f"Traceroute failed: {e}", "ERROR")
        return []

def analyze_path_latency(hops: List[Tuple[str, Optional[float], Optional[str]]]) -> dict:
    """
    Analyze those latency patterns in the network path.
    """
    if not hops:
        return {}
        
    latencies = [lat for _, lat, _ in hops if lat is not None]
    if not latencies:
        return {}
        
    return {
        "min_latency": min(latencies),
        "max_latency": max(latencies),
        "avg_latency": sum(latencies) / len(latencies),
        "total_hops": len(hops),
        "responsive_hops": len(latencies)
    }

def highlight_zscaler_in_path(hops: List[Tuple[str, Optional[float], Optional[str]]]) -> Tuple[List[str], bool]:
    """
    Highlights Zscaler nodes in the traceroute path and returns formatted output.
    """
    highlighted = []
    zscaler_found = False
    
    for hop_num, (ip, latency, _) in enumerate(hops, 1):
        zscaler = is_zscaler_ip(ip)
        lat_str = f"{latency:.1f}ms" if latency is not None else "   *  "
        
        if zscaler:
            highlighted.append(f"  {hop_num:2d}: {ip:15}  {lat_str:>7}  🛡 ZSCALER ENDPOINT")
            zscaler_found = True
        else:
            highlighted.append(f"  {hop_num:2d}: {ip:15}  {lat_str:>7}")
            
    return highlighted, zscaler_found

def display_results(zinfo: dict, hops: List[Tuple[str, Optional[float], Optional[str]]], target: str):
    """
    Display results in pretty formatted boxes.
    """
    # Zscaler Results
    zscaler_lines = []
    if "error" in zinfo:
        zscaler_lines.append(f"❌ Error checking Zscaler: {zinfo['error']}")
    else:
        if zinfo.get("zscaler"):
            zscaler_lines.append("🛡 STATUS: Behind Zscaler Proxy")
            zscaler_lines.append(f"📍 Gateway IP: {zinfo.get('gateway_ip', 'Unknown')}")
            zscaler_lines.append(f"🌐 Public IP: {zinfo.get('public_ip', 'Unknown')}")
        else:
            zscaler_lines.append("🔓 STATUS: NOT behind Zscaler")
            zscaler_lines.append(f"🌐 Public IP: {zinfo.get('public_ip', 'Unknown')}")
            
    show_summary_box("ZSCALER DETECTION RESULTS", zscaler_lines)
    print()
    
    # Path Analysis
    if hops:
        highlighted, zscaler_in_path = highlight_zscaler_in_path(hops)
        latency_stats = analyze_path_latency(hops)
        
        path_lines = [f"🎯 Target: {target}"]
        if latency_stats:
            path_lines.extend([
                f"📊 Total Hops: {latency_stats['total_hops']}",
                f"⚡ Min Latency: {latency_stats['min_latency']:.1f}ms",
                f"⚡ Max Latency: {latency_stats['max_latency']:.1f}ms",
                f"⚡ Avg Latency: {latency_stats['avg_latency']:.1f}ms"
            ])
            
        show_summary_box("PATH ANALYSIS SUMMARY", path_lines)
        print()
        
        # More Detailed Path
        print("+" + "="*70 + "+")
        print("|" + "NETWORK PATH TO TARGET".center(70) + "|")
        print("+" + "-"*70 + "+")
        print("| Hop | IP Address      | Latency | Notes" + " "*25 + "|")
        print("+" + "-"*70 + "+")
        
        for line in highlighted:
            # Truncate long lines to fit in box
            display_line = line[:66] if len(line) > 66 else line
            print(f"|{display_line.ljust(70)}|")
            
        print("+" + "="*70 + "+")
        
        # Final Assessment
        final_lines = []
        if zinfo.get('zscaler') or zscaler_in_path:
            final_lines.extend([
                "✅ CONCLUSION: Zscaler - You have been Zscaler'd",
                "   You are a victim of Zscaler. Your traffic is being",
                "   overly inspected and filtered."
            ])
        else:
            final_lines.extend([
                "❌ CONCLUSION: No Zscaler - You are not a victim of Zscaler",
                "   You have freedom to roam the internet without Zscaler."
            ])
            
        print()
        show_summary_box("FINAL ASSESSMENT", final_lines)
        
    else:
        print_status("No information available", "ERROR")

def get_target_input() -> str:
    """Get target from user with validation"""
    while True:
        target = input("\n🎯 Enter target IP address or hostname: ").strip()
        if target:
            return target
        print_status("Please enter a valid target", "ERROR")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Advanced Zscaler detection and network path analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python zscaler_checker.py google.com
  python zscaler_checker.py 8.8.8.8 --timeout 30
  python zscaler_checker.py --max-hops 20
        """
    )
    
    parser.add_argument("endpoint", type=str, nargs="?", 
                       help="Target IP address or hostname")
    parser.add_argument("--timeout", type=int, default=60, 
                       help="Traceroute timeout in seconds (default: 60)")
    parser.add_argument("--max-hops", type=int, default=30, 
                       help="Maximum hops for traceroute (default: 30)")
    parser.add_argument("--no-clear", action="store_true",
                       help="Don't clear screen on startup")
    
    args = parser.parse_args()
    
    try:
        # Setup display
        if not args.no_clear:
            clear_screen()
        show_header()
        
        # Get target
        endpoint = args.endpoint
        if not endpoint:
            endpoint = get_target_input()
            
        print_status(f"Starting analysis for target: {endpoint}", "NETWORK")
        print_status("This may take 30-60 seconds to complete...", "INFO")
        print()
        
        # Check Zscaler presence
        print_status("Phase 1: Checking Zscaler presence", "CHECKING")
        zinfo = get_public_ip_and_zscaler_info()
        time.sleep(1)
        
        # Perform traceroute
        print_status("Phase 2: Tracing network path", "CHECKING")
        hops = traceroute_path(endpoint, max_hops=args.max_hops, timeout=args.timeout)
        time.sleep(1)
        
        # Display results
        print_status("Phase 3: Analyzing results", "CHECKING")
        print("\n" + "="*80)
        display_results(zinfo, hops, endpoint)
        
        print_status("Analysis complete!", "SUCCESS")
        
    except KeyboardInterrupt:
        print_status("\n\nAnalysis interrupted by you", "WARNING")
        sys.exit(0)
    except Exception as e:
        print_status(f"Unexpected error: {e}", "ERROR")
        sys.exit(1)

if __name__ == "__main__":
    main()