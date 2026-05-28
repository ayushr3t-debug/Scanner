#!/usr/bin/env python3
"""
Basic Port Scanner
Usage: python port_scanner.py <host> [start_port] [end_port] [--threads N] [--timeout T]
"""

import socket
import threading
import argparse
import sys
from datetime import datetime
from queue import Queue

# Common service names
SERVICES = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
    80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS", 445: "SMB",
    3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL", 5900: "VNC",
    6379: "Redis", 8080: "HTTP-Alt", 8443: "HTTPS-Alt", 8000: "HTTP-Dev",
    27017: "MongoDB", 11211: "Memcached", 1433: "MSSQL", 3000: "Node.js",
}

open_ports = []
lock = threading.Lock()


def scan_port(host: str, port: int, timeout: float) -> dict | None:
    """Try to connect to a single port. Returns result dict or None if closed."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        if result == 0:
            service = SERVICES.get(port, "unknown")
            # Try to grab a banner
            banner = grab_banner(host, port, timeout)
            return {"port": port, "service": service, "banner": banner}
    except (socket.error, OSError):
        pass
    return None


def grab_banner(host: str, port: int, timeout: float) -> str:
    """Try to get a service banner."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((host, port))
        sock.send(b"HEAD / HTTP/1.0\r\n\r\n")
        banner = sock.recv(1024).decode("utf-8", errors="ignore").strip()
        sock.close()
        # Return first meaningful line
        lines = [l for l in banner.splitlines() if l.strip()]
        return lines[0][:60] if lines else ""
    except Exception:
        return ""


def worker(host: str, queue: Queue, timeout: float, print_lock: threading.Lock):
    """Thread worker: pulls ports from queue and scans them."""
    while True:
        port = queue.get()
        if port is None:
            break
        result = scan_port(host, port, timeout)
        if result:
            with lock:
                open_ports.append(result)
            with print_lock:
                banner_str = f"  → {result['banner']}" if result['banner'] else ""
                print(f"  \033[92m[OPEN]\033[0m  {port:>5}  {result['service']:<14}{banner_str}")
        queue.task_done()


def resolve_host(host: str) -> str:
    """Resolve hostname to IP."""
    try:
        ip = socket.gethostbyname(host)
        return ip
    except socket.gaierror:
        print(f"\033[91m[ERROR]\033[0m Cannot resolve host: {host}")
        sys.exit(1)


def scan(host: str, start: int, end: int, threads: int, timeout: float):
    print(f"\n{'='*55}")
    print(f"  Port Scanner")
    print(f"{'='*55}")
    ip = resolve_host(host)
    print(f"  Target  : {host} ({ip})")
    print(f"  Ports   : {start} – {end}  ({end - start + 1} total)")
    print(f"  Threads : {threads}")
    print(f"  Timeout : {timeout}s per port")
    print(f"  Started : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*55}\n")

    queue = Queue()
    print_lock = threading.Lock()

    # Fill queue
    for port in range(start, end + 1):
        queue.put(port)
    # Sentinels to stop threads
    for _ in range(threads):
        queue.put(None)

    # Start threads
    thread_list = []
    for _ in range(threads):
        t = threading.Thread(target=worker, args=(ip, queue, timeout, print_lock), daemon=True)
        t.start()
        thread_list.append(t)

    try:
        queue.join()
        for t in thread_list:
            t.join()
    except KeyboardInterrupt:
        print("\n\033[93m[!] Scan interrupted by user\033[0m")

    # Summary
    print(f"\n{'='*55}")
    print(f"  Scan complete — {len(open_ports)} open port(s) found")
    print(f"{'='*55}")
    if open_ports:
        open_ports.sort(key=lambda x: x["port"])
        print(f"\n  {'PORT':<8} {'SERVICE':<16} BANNER")
        print(f"  {'-'*50}")
        for p in open_ports:
            banner = p['banner'][:40] if p['banner'] else ""
            print(f"  {p['port']:<8} {p['service']:<16} {banner}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Basic TCP port scanner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python port_scanner.py 192.168.1.1
  python port_scanner.py example.com 1 1024
  python port_scanner.py 10.0.0.1 1 65535 --threads 200 --timeout 0.5
        """
    )
    parser.add_argument("host", help="Target host (IP or hostname)")
    parser.add_argument("start_port", nargs="?", type=int, default=1, help="Start port (default: 1)")
    parser.add_argument("end_port", nargs="?", type=int, default=1024, help="End port (default: 1024)")
    parser.add_argument("--threads", type=int, default=100, help="Number of threads (default: 100)")
    parser.add_argument("--timeout", type=float, default=0.5, help="Timeout per port in seconds (default: 0.5)")

    args = parser.parse_args()

    if not (1 <= args.start_port <= 65535 and 1 <= args.end_port <= 65535):
        print("[ERROR] Ports must be between 1 and 65535")
        sys.exit(1)
    if args.start_port > args.end_port:
        print("[ERROR] Start port must be <= end port")
        sys.exit(1)

    scan(args.host, args.start_port, args.end_port, args.threads, args.timeout)


if __name__ == "__main__":
    main()
