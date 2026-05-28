# Scanner
Lightweight TCP port scanner in Python — supports multithreading, banner grabbing, and service detection. Zero external dependencies.


# 🔍 Port Scanner

A fast, multithreaded TCP port scanner written in Python. No external dependencies — uses only the standard library.

## Features

- **Multithreaded** — scans hundreds of ports simultaneously using a thread pool
- **Banner grabbing** — attempts to identify services on open ports
- **Service detection** — recognizes 20+ common services by port number
- **Configurable** — control thread count, timeout, and port range via CLI flags
- **Zero dependencies** — pure Python standard library only

## Requirements

- Python 3.10 or higher

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/port-scanner.git
cd port-scanner
```

That's it. No `pip install` needed.

## Usage

```bash
python port_scanner.py <host> [start_port] [end_port] [options]
```

### Arguments

| Argument | Description | Default |
|---|---|---|
| `host` | Target IP address or hostname | *(required)* |
| `start_port` | First port to scan | `1` |
| `end_port` | Last port to scan | `1024` |
| `--threads N` | Number of concurrent threads | `100` |
| `--timeout T` | Seconds to wait per port | `0.5` |

### Examples

```bash
# Scan common ports (1–1024) on a local machine
python port_scanner.py 192.168.1.1

# Scan a specific range
python port_scanner.py 192.168.1.1 1 9000

# Scan with a hostname
python port_scanner.py example.com 1 1024

# Full port scan (all 65535 ports) with more threads
python port_scanner.py 10.0.0.1 1 65535 --threads 200 --timeout 0.5

# Slow, careful scan with a longer timeout
python port_scanner.py 10.0.0.1 1 1024 --threads 50 --timeout 2.0
```

### Sample Output

```
=======================================================
  Port Scanner
=======================================================
  Target  : 192.168.1.1 (192.168.1.1)
  Ports   : 1 – 1024  (1024 total)
  Threads : 100
  Timeout : 0.5s
  Started : 2025-01-01 12:00:00
=======================================================

  [OPEN]     22  SSH             SSH-2.0-OpenSSH_8.9
  [OPEN]     80  HTTP            HTTP/1.1 200 OK
  [OPEN]    443  HTTPS

=======================================================
  Scan complete — 3 open port(s) found
=======================================================

  PORT     SERVICE          BANNER
  --------------------------------------------------
  22       SSH              SSH-2.0-OpenSSH_8.9
  80       HTTP             HTTP/1.1 200 OK
  443      HTTPS
```

## How It Works

1. The target hostname is resolved to an IP address via `socket.gethostbyname()`
2. All ports in the range are pushed into a thread-safe `Queue`
3. A pool of worker threads pulls ports from the queue and attempts a TCP `connect_ex()` to each
4. On a successful connection (return code `0`), the scanner attempts to read a banner from the service
5. Results are collected with a lock and printed in sorted order at the end

## Performance Tips

| Scenario | Recommended flags |
|---|---|
| Quick scan of common ports | `--threads 100 --timeout 0.5` (default) |
| Full 65535-port scan | `--threads 300 --timeout 0.3` |
| Slow/distant target | `--threads 50 --timeout 2.0` |
| Local network | `--threads 200 --timeout 0.2` |

## Supported Services

The scanner recognizes these ports by name out of the box:

`FTP (21)` · `SSH (22)` · `Telnet (23)` · `SMTP (25)` · `DNS (53)` · `HTTP (80)` · `POP3 (110)` · `IMAP (143)` · `HTTPS (443)` · `SMB (445)` · `MSSQL (1433)` · `MySQL (3306)` · `RDP (3389)` · `PostgreSQL (5432)` · `VNC (5900)` · `Redis (6379)` · `HTTP-Dev (8000)` · `HTTP-Alt (8080)` · `HTTPS-Alt (8443)` · `MongoDB (27017)`

## Legal Disclaimer

> **Only scan hosts you own or have explicit written permission to scan.**
>
> Unauthorized port scanning may violate the Computer Fraud and Abuse Act (CFAA), local laws, and the terms of service of networks and ISPs. The author is not responsible for any misuse of this tool.

## License

MIT License — see [LICENSE](LICENSE) for details.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you'd like to change.

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Open a Pull Request
