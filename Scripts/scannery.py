import os
import time

os.system('clear')

def show_menu():
    print("        * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *\n"
          "         *                                                                                                                                 *\n"
          "         *                                                         S C A N N E R Y                                                         *\n"
          "         *                                                                                                                                 *\n"
          "        * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *\n")
    print()
show_menu() 

def scanny_menu():
    print("Welcome to Scan Scannery! Current scanning options available are :\n")
    print("""
        Press 1  to scan single IP and do simple fingerprinting
        Press 2  for Scanning a Specific Port
        Press 3  for Scanning an IP Range
        Press 4  for Scanning top-popular ports
        Press 5  for Scanning with disabling DNS resolution
        Press 6  for Scanning used services
        Press 7  for Scanning only TCP protocols
        Press 8  for Scanning only UDP protocols
        Press 9  for Scanning CVE stuff
        Press 10 for Mike Tyson style scanning\n""") 

def run_scanny():
    time.sleep(1)
    print()   
    TargetIP = input("Enter the IP of Target Machine : ")
    print()
    scanny_menu()
    print()
    usrInput = int(input("Enter the number of the scan to perform : "))
    print()
    print("[INFO] Scanning now...")
    time.sleep(2.0)

    if (usrInput == 1):
        os.system("sudo nmap {}".format(TargetIP))
        os.system("sudo nc -v ".format(TargetIP))
        exit(0)
        
    elif (usrInput == 2):
        port=input("Enter the IP Port to Scan :")
        os.system("sudo nmap -p {} {}".format(port,TargetIP))
        exit(0)

    elif (usrInput == 3):
        #range=input("Enter the IP ranges to Scan :")
        iprange = input("Enter the Complete IP Range :")
        os.system("sudo nmap -p {}".format(iprange))
        exit(0)

    elif (usrInput == 4):
        num=int(input("Enter the count of ports you want to Scan :"))
        os.system("sudo nmap --top-ports {} {}".format(num,TargetIP))
        exit(0)

    elif (usrInput == 5):
        os.system("sudo nmap -p 80 -n {}".format(TargetIP))
        exit(0)

    elif (usrInput == 6):
        os.system("sudo nmap -sV {}".format(TargetIP))
        exit(0)

    elif (usrInput == 7):
        os.system("sudo nmap -sT {}".format(TargetIP))
        exit(0)

    elif (usrInput == 8):
        os.system("sudo nmap -sU {}".format(TargetIP))
        exit(0)

    elif (usrInput == 9):
        os.system("sudo nmap -Pn --script vuln {}".format(TargetIP))
        exit(0)

    elif (usrInput == 10):
        os.system("sudo nmap -sV -T4 -O -A -Pn {}".format(TargetIP))
        exit(0)

    else:
        print("[INFO] Bruh....")
        time.sleep(1)
        print("[INFO] Follow directions better....")
        print("[INFO] Aborting...")
        time.sleep(2.0)
        print("Please Enter Correct Number!!!")

def main():
    while True:
        run_scanny()

if __name__ == "__main__":
    main()