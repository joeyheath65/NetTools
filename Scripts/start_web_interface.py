#!/usr/bin/env python3
"""
Start Web Interface
Checks dependencies and starts the web server
"""

import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = ['flask']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Missing required packages: {', '.join(missing_packages)}")
        print("Installing missing packages...")
        
        for package in missing_packages:
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                print(f"✓ Installed {package}")
            except subprocess.CalledProcessError:
                print(f"✗ Failed to install {package}")
                return False
    
    return True

def check_database():
    """Check if database exists"""
    db_path = Path("../Data/network_infrastructure.db")
    if not db_path.exists():
        print("Database not found!")
        print("Please run the migration scripts first:")
        print("  python3 simple_migration.py")
        print("  python3 populate_all_stores.py")
        return False
    
    print(f"✓ Database found: {db_path}")
    return True

def start_server():
    """Start the web server"""
    print("Starting H-E-B Network Infrastructure Web Interface...")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        print("Failed to install dependencies. Please install manually:")
        print("  pip install flask")
        return
    
    # Check database
    if not check_database():
        return
    
    print("\nStarting web server...")
    print("Open your browser to: http://localhost:5002")
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    # Import and run the web server
    try:
        from web_server import app
        app.run(debug=True, host='0.0.0.0', port=5002)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error starting server: {e}")

if __name__ == "__main__":
    start_server() 