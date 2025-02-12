import os
import time
import threading
import requests
import psutil
import logging
import signal
import sys
from datetime import datetime
from urllib.parse import urlparse
from colorama import Fore, Style, init

init(autoreset=True)

required_libraries = ["requests", "psutil", "colorama"]
missing_libraries = [lib for lib in required_libraries if not __import__(lib, globals(), locals(), [], 0)]

if missing_libraries:
    print(Fore.YELLOW + "Missing dependencies detected. Installing now...")
    os.system("pip install -r requirements.txt")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("network_stress_test.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

stop_test = False
total_requests = 0
successful_requests = 0
failed_requests = 0
response_times = []
start_time = time.time()
results_filename = ""

def print_ascii_art():
    print(Fore.CYAN + Style.BRIGHT + r"""
    ____  ____  ____  _________   ____  ____  ____  ______
   / __ )/ __ \/ __ \/_  __/__ \ / __ \/ __ \/ __ \/_  __/
  / __  / / / / / / / / /  __/ // /_/ / / / / / / / / /   
 / /_/ / /_/ / /_/ / / /  / __// _, _/ /_/ / /_/ / / /    
/_____/\____/\____/ /_/  /____/_/ |_|\____/\____/ /_/     

-NeveR QuiT!            Mailto: likundebi2024@gmail.com
    """)
    print(Fore.YELLOW + Style.BRIGHT + "\n🚀 Network Stress Testing Tool 🚀")
    print(Fore.YELLOW + "=================================")
    print(Fore.GREEN + Style.BRIGHT + "🔹 Press Ctrl+C to stop the test.\n")

def clean_url(user_input):
    if not user_input.startswith(("http://", "https://")):
        return f"https://{user_input}"
    return user_input

def display_stats():
    while not stop_test:
        elapsed_time = time.time() - start_time
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        request_per_sec = total_requests / elapsed_time if elapsed_time > 0 else 0
        response_trend = 0

        if len(response_times) > 1:
            response_trend = ((response_times[-1] - response_times[0]) / response_times[0]) * 100 if response_times[0] > 0 else 0
        
        print("\033[H\033[J", end="")  # Clear the terminal screen
        print(Fore.YELLOW + f"📊 Total Requests Sent: {total_requests}")
        print(Fore.GREEN + f"✅ Successful Requests: {successful_requests}")
        print(Fore.RED + f"❌ Failed Requests: {failed_requests}")
        print(Fore.BLUE + f"⚡ Requests Per Second: {request_per_sec:.2f}")
        print(Fore.CYAN + f"⏳ Average Response Time: {avg_response_time:.4f} sec")
        print(Fore.MAGENTA + f"📈 Response Time Trend: {response_trend:.2f}% change")
        time.sleep(0.5)

def signal_handler(sig, frame):
    global stop_test
    stop_test = True
    save_choice = input(Fore.YELLOW + "\n💾 Save scan results? (Y/N): ").strip().lower()

    if save_choice == "y":
        save_results()
        print(Fore.GREEN + f"💾 Results saved to {results_filename}")
    else:
        print(Fore.RED + "❌ Scan results not saved. Exiting.")

    sys.exit(0)

def save_results():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    domain = urlparse(target_url).netloc.replace(":", "_")
    global results_filename
    results_filename = f"{domain}_stress_test_{timestamp}.txt"

    with open(results_filename, "w") as file:
        file.write("📊 Stress Test Summary\n")
        file.write("=========================\n")
        file.write(f"Target: {target_url}\n")
        file.write(f"Total Requests Sent: {total_requests}\n")
        file.write(f"Successful Requests: {successful_requests}\n")
        file.write(f"Failed Requests: {failed_requests}\n")
        file.write(f"Requests Per Second: {total_requests / (time.time() - start_time):.2f}\n")
        file.write(f"Average Response Time: {sum(response_times) / len(response_times) if response_times else 0:.4f} sec\n")
        file.write(f"Response Time Trend: {((response_times[-1] - response_times[0]) / response_times[0]) * 100 if len(response_times) > 1 and response_times[0] > 0 else 0:.2f}%\n")

def simulate_request(target_url):
    global total_requests, successful_requests, failed_requests
    while not stop_test:
        try:
            start_req_time = time.time()
            response = requests.get(target_url, timeout=5)
            end_req_time = time.time()
            total_requests += 1
            response_times.append(end_req_time - start_req_time)

            if response.status_code == 200:
                successful_requests += 1
            else:
                failed_requests += 1
        except requests.exceptions.RequestException:
            failed_requests += 1
        time.sleep(1)

def run_stress_test(target_url, num_threads):
    global stop_test
    logging.info(Fore.CYAN + f"🚀 Starting Stress Test with {num_threads} concurrent requests to {target_url}...")
    
    stats_thread = threading.Thread(target=display_stats)
    stats_thread.daemon = True
    stats_thread.start()

    threads = []
    for _ in range(num_threads):
        thread = threading.Thread(target=simulate_request, args=(target_url,))
        thread.start()
        threads.append(thread)

    try:
        while not stop_test:
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)

    for thread in threads:
        thread.join()

def main():
    global target_url
    print_ascii_art()
    user_input = input(Fore.YELLOW + "🌐 Enter the target server URL (e.g., example.com or https://example.com): ").strip()
    target_url = clean_url(user_input)
    
    threading_level = input(Fore.YELLOW + "🔧 Choose threading level (1-5): ").strip()
    try:
        level = int(threading_level)
        if level < 1 or level > 5:
            print(Fore.RED + "❌ Invalid level. Setting to 1.")
            level = 1
    except ValueError:
        print(Fore.RED + "❌ Invalid input. Setting threading level to 1.")
        level = 1

    num_threads = level * 10
    signal.signal(signal.SIGINT, signal_handler)
    logging.info(Fore.CYAN + "🚀 Network Stress Testing Simulation Started")
    run_stress_test(target_url, num_threads)
    logging.info(Fore.CYAN + "🏁 Network Stress Testing Simulation Completed")

if __name__ == "__main__":
    main()
