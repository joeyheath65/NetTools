#!/usr/bin/env python3
"""
+======================================================================+
|                      LOTTERY ANALYZER                               |
|                Mega Millions & Powerball Generator                  |
+======================================================================+

Author: Joe Heath
Email: joe@joeheath.com
GitHub: https://github.com/joeheath
Location: Floresville, TX

Created: 2025-06-24
Version: 1.0

Description:
    Advanced lottery number analysis tool that generates and analyzes
    frequency patterns for both Mega Millions and Powerball lottery
    systems using statistical simulation over millions of drawings.

Requirements:
    - Python 3.6+
    - No external dependencies (uses built-in libraries)

Usage:
    python lottery_analyzer.py

License: MIT License
+======================================================================+
"""

import random
import collections
import time
import os
import sys
from datetime import datetime

def clear_screen():
    """Clear terminal screen"""
    os.system('clear' if os.name != 'nt' else 'cls')

def show_header():
    """Display main header"""
    print("""
+----------------------------------------------------------------------+
|                        LOTTERY ANALYZER                             |
|                Mega Millions & Powerball Generator                  |
+----------------------------------------------------------------------+
| Author: Joe [Your Last Name] | Floresville, TX | Version 1.0        |
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
        "ANALYZING": "🔍",
        "LOTTERY": "🎰",
        "NUMBERS": "🔢"
    }
    symbol = symbols.get(status_type, "•")
    print(f"[{timestamp}] {symbol} {message}")

def show_menu():
    """Display main menu options"""
    print("""
+----------------------------------------------------------------------+
|                          LOTTERY MENU                               |
+----------------------------------------------------------------------+
| 1. Analyze Mega Millions                                            |
| 2. Analyze Powerball                                                |
| 3. Analyze Both Lotteries                                           |
| 4. Generate Quick Picks                                             |
| 5. Exit                                                             |
+----------------------------------------------------------------------+
    """)

def get_user_choice():
    """Get and validate user menu choice"""
    while True:
        try:
            choice = input("\n🎯 Select an option (1-5): ").strip()
            if choice in ['1', '2', '3', '4', '5']:
                return int(choice)
            print_status("Please enter a number between 1-5", "ERROR")
        except (ValueError, KeyboardInterrupt):
            print_status("Please enter a valid number", "ERROR")

def get_num_drawings():
    """Get number of drawings from user"""
    while True:
        try:
            print("\n📊 How many drawings to simulate?")
            print("   1. Quick Test (10,000)")
            print("   2. Standard (100,000)")
            print("   3. Comprehensive (1,000,000)")
            print("   4. Custom amount")
            
            choice = input("\nSelect option (1-4): ").strip()
            
            if choice == '1':
                return 10000
            elif choice == '2':
                return 100000
            elif choice == '3':
                return 1000000
            elif choice == '4':
                custom = int(input("Enter custom number of drawings: "))
                if custom > 0:
                    return custom
                else:
                    print_status("Number must be positive", "ERROR")
            else:
                print_status("Please select 1-4", "ERROR")
                
        except (ValueError, KeyboardInterrupt):
            print_status("Please enter a valid number", "ERROR")

def analyze_mega_millions(num_drawings):
    """Analyze Mega Millions frequency"""
    print_status(f"Analyzing Mega Millions over {num_drawings:,} drawings", "ANALYZING")
    
    main_numbers = collections.Counter()
    mega_ball = collections.Counter()
    
    # Show progress every 10% for large analyses
    progress_step = max(1, num_drawings // 10)
    
    for i in range(num_drawings):
        # Generate numbers according to Mega Millions rules
        main_num = random.randint(1, 70)
        mega_num = random.randint(1, 25)
        
        main_numbers.update([main_num])
        mega_ball.update([mega_num])
        
        # Show progress
        if i > 0 and i % progress_step == 0:
            percent = (i / num_drawings) * 100
            print(f"   Progress: {percent:.0f}% ({i:,} drawings)")
    
    print_status("Mega Millions analysis complete!", "SUCCESS")
    return main_numbers, mega_ball

def analyze_powerball(num_drawings):
    """Analyze Powerball frequency"""
    print_status(f"Analyzing Powerball over {num_drawings:,} drawings", "ANALYZING")
    
    main_numbers = collections.Counter()
    power_ball = collections.Counter()
    
    # Show progress every 10% for large analyses
    progress_step = max(1, num_drawings // 10)
    
    for i in range(num_drawings):
        # Generate numbers according to Powerball rules
        main_num = random.randint(1, 69)
        power_num = random.randint(1, 26)
        
        main_numbers.update([main_num])
        power_ball.update([power_num])
        
        # Show progress
        if i > 0 and i % progress_step == 0:
            percent = (i / num_drawings) * 100
            print(f"   Progress: {percent:.0f}% ({i:,} drawings)")
    
    print_status("Powerball analysis complete!", "SUCCESS")
    return main_numbers, power_ball

def display_results(lottery_name, main_numbers, special_ball, special_name):
    """Display lottery analysis results"""
    print(f"\n╔{'═' * (len(lottery_name) + 20)}╗")
    print(f"║ {lottery_name.upper()} RESULTS ║")
    print(f"╚{'═' * (len(lottery_name) + 20)}╝")
    
    # Main numbers results
    print(f"\n🎯 Top 10 Most Common Main Numbers:")
    main_top = main_numbers.most_common(10)
    for i, (number, count) in enumerate(main_top, 1):
        print(f"   {i:2d}. Number {number:2d} - appeared {count:,} times")
    
    # Special ball results  
    print(f"\n🔮 Top 5 Most Common {special_name}:")
    special_top = special_ball.most_common(5)
    for i, (number, count) in enumerate(special_top, 1):
        print(f"   {i:2d}. Number {number:2d} - appeared {count:,} times")

def generate_mega_millions_ticket():
    """Generate a Mega Millions ticket"""
    main_numbers = sorted(random.sample(range(1, 71), 5))
    mega_ball = random.randint(1, 25)
    return main_numbers, mega_ball

def generate_powerball_ticket():
    """Generate a Powerball ticket"""
    main_numbers = sorted(random.sample(range(1, 70), 5))
    power_ball = random.randint(1, 26)
    return main_numbers, power_ball

def generate_quick_picks():
    """Generate quick pick tickets for both lotteries"""
    while True:
        try:
            num_tickets = int(input("\n🎲 How many tickets to generate? "))
            if num_tickets > 0:
                break
            print_status("Number must be positive", "ERROR")
        except (ValueError, KeyboardInterrupt):
            print_status("Please enter a valid number", "ERROR")
    
    print(f"\n🎰 MEGA MILLIONS TICKETS:")
    print("=" * 50)
    for i in range(num_tickets):
        main, mega = generate_mega_millions_ticket()
        main_str = " - ".join(f"{num:2d}" for num in main)
        print(f"Ticket {i+1:2d}: {main_str} | Mega Ball: {mega:2d}")
    
    print(f"\n⚡ POWERBALL TICKETS:")
    print("=" * 50)
    for i in range(num_tickets):
        main, power = generate_powerball_ticket()
        main_str = " - ".join(f"{num:2d}" for num in main)
        print(f"Ticket {i+1:2d}: {main_str} | Power Ball: {power:2d}")

def continue_prompt():
    """Ask user if they want to continue"""
    while True:
        try:
            response = input("\n🔄 Would you like to continue? (y/n): ").lower().strip()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                print_status("Please enter 'y' or 'n'", "ERROR")
        except KeyboardInterrupt:
            return False

def main():
    """Main program loop"""
    try:
        while True:
            clear_screen()
            show_header()
            show_menu()
            
            choice = get_user_choice()
            
            if choice == 1:
                # Mega Millions Analysis
                num_drawings = get_num_drawings()
                print()
                main_numbers, mega_ball = analyze_mega_millions(num_drawings)
                display_results("Mega Millions", main_numbers, mega_ball, "Mega Ball")
                
            elif choice == 2:
                # Powerball Analysis
                num_drawings = get_num_drawings()
                print()
                main_numbers, power_ball = analyze_powerball(num_drawings)
                display_results("Powerball", main_numbers, power_ball, "Power Ball")
                
            elif choice == 3:
                # Both Lotteries
                num_drawings = get_num_drawings()
                print()
                
                # Analyze Mega Millions
                mega_main, mega_ball = analyze_mega_millions(num_drawings)
                display_results("Mega Millions", mega_main, mega_ball, "Mega Ball")
                
                print("\n" + "="*70)
                
                # Analyze Powerball
                power_main, power_ball = analyze_powerball(num_drawings)
                display_results("Powerball", power_main, power_ball, "Power Ball")
                
            elif choice == 4:
                # Quick Picks
                generate_quick_picks()
                
            elif choice == 5:
                # Exit
                print_status("Thank you for using Lottery Analyzer! 🎰", "SUCCESS")
                break
            
            # Ask if user wants to continue (except for exit)
            if choice != 5:
                if not continue_prompt():
                    print_status("Thank you for using Lottery Analyzer! 🎰", "SUCCESS")
                    break
                    
    except KeyboardInterrupt:
        print_status("\n\nProgram interrupted by user", "WARNING")
        sys.exit(0)
    except Exception as e:
        print_status(f"An error occurred: {e}", "ERROR")
        sys.exit(1)

if __name__ == "__main__":
    main()