import time
import threading
import requests
import psutil
import logging
import signal
import sys
from colorama import Fore, Style, init

init(autoreset=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('network_stress_test.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

stop_test = False

def print_ascii_art():
    print(Fore.CYAN + r"""
    ____  ____  ____  _________   ____  ____  ____  ______
   / __ )/ __ \/ __ \/_  __/__ \ / __ \/ __ \/ __ \/_  __/
  / __  / / / / / / / / /  __/ // /_/ / / / / / / / / /   
 / /_/ / /_/ / /_/ / / /  / __// _, _/ /_/ / /_/ / / /    
/_____/\____/\____/ /_/  /____/_/ |_|\____/\____/ /_/     

-Never QUIT!
    """)
    print(Fore.YELLOW + "Network Stress Testing Tool")
    print(Fore.YELLOW + "===========================")
    print(Fore.GREEN + "Press Ctrl+C to stop the test.\n")

def signal_handler(sig, frame):
    global stop_test
    logging.info(Fore.RED + "Ctrl+C detected. Stopping the stress test gracefully...")
    stop_test = True
    sys.exit(0)

def check_ddos_protection(target_url):
    try:
        response = requests.get(target_url)
        headers = response.headers
        print(Fore.CYAN + "\nChecking for DDoS protection...\n")
        if "server" in headers and "cloudflare" in headers["server"].lower():
            print(Fore.YELLOW + "DDoS Protection: " + Fore.GREEN + "Cloudflare detected!")
            return True
        elif "cf-ray" in headers:
            print(Fore.YELLOW + "DDoS Protection: " + Fore.GREEN + "Cloudflare detected!")
            return True
        elif "__cfduid" in response.cookies:
            print(Fore.YELLOW + "DDoS Protection: " + Fore.GREEN + "Cloudflare detected!")
            return True
        elif "server" in headers and "akamai" in headers["server"].lower():
            print(Fore.YELLOW + "DDoS Protection: " + Fore.GREEN + "Akamai detected!")
            return True
        elif "x-akamai-transformed" in headers:
            print(Fore.YELLOW + "DDoS Protection: " + Fore.GREEN + "Akamai detected!")
            return True
        elif "x-amz-cf-pop" in headers:
            print(Fore.YELLOW + "DDoS Protection: " + Fore.GREEN + "AWS Shield (CloudFront) detected!")
            return True
        elif "server" in headers and "cloudfront" in headers["server"].lower():
            print(Fore.YELLOW + "DDoS Protection: " + Fore.GREEN + "AWS Shield (CloudFront) detected!")
            return True
        else:
            print(Fore.YELLOW + "DDoS Protection: " + Fore.RED + "No known DDoS protection detected.")
            return False
    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"Error: {e}")
        return True

def simulate_request(target_url):
    global stop_test
    while not stop_test:
        try:
            start_time = time.time()
            response = requests.get(target_url, timeout=5)
            end_time = time.time()
            response_time = end_time - start_time
            logging.info(Fore.GREEN + f"Response Time: {response_time:.4f} seconds, Status Code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logging.error(Fore.RED + f"Request Failed: {e}")
            if "Max retries exceeded" in str(e) or "Connection refused" in str(e):
                logging.error(Fore.RED + "The site appears to be down!")
                stop_test = True
                break
        time.sleep(1)

def monitor_system_resources():
    global stop_test
    while not stop_test:
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_usage = psutil.virtual_memory().percent
        logging.info(Fore.BLUE + f"CPU Usage: {cpu_usage}%, Memory Usage: {memory_usage}%")
        time.sleep(5)

def run_stress_test(target_url, num_threads):
    global stop_test
    logging.info(Fore.CYAN + f"Starting Stress Test with {num_threads} concurrent requests to {target_url}...")
    threads = []
    for _ in range(num_threads):
        thread = threading.Thread(target=simulate_request, args=(target_url,))
        thread.start()
        threads.append(thread)
    monitor_thread = threading.Thread(target=monitor_system_resources)
    monitor_thread.start()
    try:
        while not stop_test:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_test = True
    for thread in threads:
        thread.join()
    monitor_thread.join()
    logging.info(Fore.CYAN + "Stress Test Completed.")

def main():
    print_ascii_art()
    target_url = input(Fore.YELLOW + "Enter the target server URL (e.g., http://yourserver.com): ").strip()
    if check_ddos_protection(target_url):
        print(Fore.RED + "The website is protected by a DDoS protection service. Exiting...")
        sys.exit(0)
    threading_level = input(Fore.YELLOW + "Enter threading level (1-5): ").strip()
    try:
        level = int(threading_level)
        if level < 1 or level > 5:
            print(Fore.RED + "Invalid level. Setting to 1.")
            level = 1
    except ValueError:
        print(Fore.RED + "Invalid input. Setting threading level to 1.")
        level = 1
    base_threads = 10
    num_threads = level * base_threads
    signal.signal(signal.SIGINT, signal_handler)
    logging.info(Fore.CYAN + "Network Stress Testing Simulation Started")
    run_stress_test(target_url, num_threads)
    logging.info(Fore.CYAN + "Network Stress Testing Simulation Completed")

if __name__ == "__main__":
    main()
