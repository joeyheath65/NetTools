import argparse
import requests
import socket
import subprocess
import sys
import re
from typing import List, Optional, Tuple
import ipaddress
# This will tell you if youre not actually behind Zscaler, and basically just do a traceroute for ya
# Static Zscaler IP ranges (sample, update as needed)
ZSCALER_IP_RANGES = [
    # These are example ranges. For production, fetch or update from:
    # https://help.zscaler.com/zia/zscaler-service-endpoints
    "185.46.212.0/22", "185.46.212.0/23", "185.46.214.0/23", "104.129.192.0/20",
    "165.225.0.0/16", "199.168.148.0/22", "199.168.152.0/21", "199.168.156.0/22",
    "199.168.160.0/21", "199.168.164.0/22", "199.168.168.0/21", "199.168.172.0/22",
    "199.168.176.0/21", "199.168.180.0/22", "199.168.184.0/21", "199.168.188.0/22",
    "199.168.192.0/21", "199.168.196.0/22", "199.168.200.0/21", "199.168.204.0/22",
    "199.168.208.0/21", "199.168.212.0/22", "199.168.216.0/21", "199.168.220.0/22",
    "199.168.224.0/21", "199.168.228.0/22", "199.168.232.0/21", "199.168.236.0/22",
    "199.168.240.0/21", "199.168.244.0/22", "199.168.248.0/21", "199.168.252.0/22",
    # ... add more as needed
]

ZSCALER_HOST_PATTERNS = [
    r"zscaler[0-9]*[.-]", r"zscloud[0-9]*[.-]", r"zscalertwo[.-]", r"zscalerthree[.-]"
]

def is_zscaler_ip(ip: str) -> bool:
    """
    Checks if an IP address is within known Zscaler IP ranges.
    Args:
        ip (str): IP address as string.
    Returns:
        bool: True if IP is in Zscaler range.
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
    Args:
        host (str): Hostname.
    Returns:
        bool: True if matches Zscaler pattern.
    """
    for pat in ZSCALER_HOST_PATTERNS:
        if re.search(pat, host, re.IGNORECASE):
            return True
    return False

def get_public_ip_and_zscaler_info() -> dict:
    """
    Checks https://ip.zscaler.com/ to determine if the client is behind Zscaler.
    Returns:
        dict: Info about Zscaler presence, public IP, and headers.
    """
    url = "https://ip.zscaler.com/"
    try:
        resp = requests.get(url, timeout=5)
        text = resp.text
        zscaler_present = "Zscaler" in text or "zscaler" in text
        # Try to extract Gateway IP and other info
        gateway_ip = None
        m = re.search(r"Gateway IP Address is most likely ([0-9.]+)", text)
        if m:
            gateway_ip = m.group(1)
        # Extract your public IP
        m2 = re.search(r"from the IP address ([0-9.]+)", text)
        public_ip = m2.group(1) if m2 else None
        if not gateway_ip or not public_ip:
            print("[WARN] Could not extract Gateway IP or Public IP from Zscaler. Raw response snippet:")
            print("----- BEGIN RAW RESPONSE -----")
            print(text[:500])
            print("----- END RAW RESPONSE -----")
        return {
            "zscaler": zscaler_present,
            "gateway_ip": gateway_ip,
            "public_ip": public_ip,
            "headers": dict(resp.headers),
            "raw": text
        }
    except Exception as e:
        return {"error": str(e)}

def traceroute_path(target: str, max_hops: int = 30, timeout: int = 60) -> List[Tuple[str, Optional[float], Optional[str]]]:
    """
    Runs traceroute (or tracert on Windows) to the target and returns the list of hops with latency.
    Args:
        target (str): IP or hostname to trace.
        max_hops (int): Maximum hops to trace.
        timeout (int): Timeout in seconds.
    Returns:
        List[Tuple[str, Optional[float], Optional[str]]]: List of (hop IP, latency ms, hostname) tuples.
    """
    is_windows = sys.platform.startswith("win")
    cmd = ["tracert", "-d", "-h", str(max_hops), target] if is_windows else ["traceroute", "-n", "-m", str(max_hops), target]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        output = proc.stdout
        hops = []
        for line in output.splitlines():
            try:
                m = re.match(r"\s*(\d+)\s+([0-9.]+)\s+(.+)", line)
                if m:
                    hop_num = m.group(1)
                    ip = m.group(2)
                    rest = m.group(3)
                    lat_m = re.search(r"(\d+\.?\d*)\s*ms", rest)
                    latency = float(lat_m.group(1)) if lat_m else None
                    hops.append((ip, latency, None))
            except Exception:
                continue
        return hops
    except subprocess.TimeoutExpired as e:
        print(f"[ERROR] Traceroute timed out after {timeout} seconds.")
        # Log a snippet of the raw output for debugging
        if e.stdout:
            print("[DEBUG] Traceroute raw output (first 500 chars):")
            if isinstance(e.stdout, bytes):
                try:
                    raw_out = e.stdout.decode('utf-8', errors='replace')
                except Exception:
                    raw_out = str(e.stdout)
            else:
                raw_out = e.stdout
            print(raw_out[:500])
        hops = []
        lines = e.stdout.splitlines() if e.stdout else []
        for line in lines:
            if isinstance(line, bytes):
                try:
                    line = line.decode('utf-8', errors='replace')
                except Exception:
                    continue
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
            print("[INFO] Partial traceroute results:")
            return hops
        return []
    except Exception as e:
        print(f"[ERROR] Traceroute failed: {e}")
        return []

def highlight_zscaler_in_path(hops: List[Tuple[str, Optional[float], Optional[str]]]) -> List[str]:
    """
    Highlights Zscaler node in the traceroute path if present, and shows latency.
    Args:
        hops (List[Tuple[str, Optional[float], Optional[str]]]): List of (ip, latency, hostname)
    Returns:
        List[str]: List of hops with Zscaler node and latency highlighted.
    """
    highlighted = []
    for ip, latency, _ in hops:
        zscaler = is_zscaler_ip(ip)
        lat_str = f"{latency:.1f} ms" if latency is not None else "-"
        if zscaler:
            highlighted.append(f"--> {ip:15}  {lat_str:>8}  <== ZSCALER ENDPOINT")
        else:
            highlighted.append(f"    {ip:15}  {lat_str:>8}")
    return highlighted

def main():
    parser = argparse.ArgumentParser(description="Test connectivity and Zscaler path to an endpoint.")
    parser.add_argument("endpoint", type=str, nargs="?", help="Target IP address or URL")
    parser.add_argument("--timeout", type=int, default=60, help="Traceroute timeout in seconds (default: 60)")
    parser.add_argument("--max-hops", type=int, default=30, help="Maximum hops for traceroute (default: 30)")
    args = parser.parse_args()
    endpoint = args.endpoint
    if not endpoint:
        endpoint = input("Enter the target IP address or URL: ").strip()
    print(f"\n[INFO] Checking Zscaler presence for this client...")
    zinfo = get_public_ip_and_zscaler_info()
    if "error" in zinfo:
        print(f"[ERROR] Could not check Zscaler info: {zinfo['error']}")
    else:
        if zinfo["zscaler"]:
            print("[ZSCALER] Client appears to be behind Zscaler.")
            print(f"  Gateway IP: {zinfo.get('gateway_ip')}")
            print(f"  Public IP: {zinfo.get('public_ip')}")
        else:
            print("[INFO] Client does NOT appear to be behind Zscaler.")
        print(f"  HTTP Headers from ip.zscaler.com: {zinfo.get('headers')}")
    print(f"\n[INFO] Tracing path to endpoint: {endpoint}")
    hops = traceroute_path(endpoint, max_hops=args.max_hops, timeout=args.timeout)
    if not hops:
        print("[ERROR] Could not determine path to endpoint.")
        sys.exit(1)
    highlighted = highlight_zscaler_in_path(hops)
    print("\n[PATH TO ENDPOINT]:")
    print("IP Address       Latency   Notes")
    print("------------------------------------------")
    for idx, hop in enumerate(highlighted, 1):
        print(f"  {idx:2d}: {hop}")
    zscaler_detected = False
    if zinfo.get('zscaler'):
        zscaler_detected = True
    if any('ZSCALER ENDPOINT' in h for h in highlighted):
        zscaler_detected = True
    if zscaler_detected:
        print("\n[INFO] Zscaler endpoint is present in the path to the endpoint.")
    else:
        print("\n[INFO] You are NOT behind a Zscaler gateway.")

if __name__ == "__main__":
    main() 