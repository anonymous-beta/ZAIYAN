import socket
import threading
from concurrent.futures import ThreadPoolExecutor
from core.module_base import AuxiliaryModule

class PortScanner(AuxiliaryModule):
    NAME = "tcp_port_scanner"
    DESCRIPTION = "Multi-threaded TCP port scanner with service detection"
    AUTHOR = "Anonymous-beta"
    PLATFORM = ["generic"]
    
    def _setup_options(self):
        super()._setup_options()
        self.options["PORTS"] = {
            "description": "Ports to scan (e.g., 1-1000,22,80,443)",
            "required": True,
            "value": "1-1000"
        }
        self.options["TIMEOUT"] = {
            "description": "Connection timeout in seconds",
            "required": False,
            "value": "1"
        }
    
    def execute(self):
        """Execute port scan"""
        rhosts = self.get_option("RHOSTS")
        ports_str = self.get_option("PORTS")
        timeout = float(self.get_option("TIMEOUT"))
        threads = int(self.get_option("THREADS"))
        
        targets = self._parse_targets(rhosts)
        ports = self._parse_ports(ports_str)
        
        print(f"[*] Scanning {len(targets)} host(s), {len(ports)} port(s)")
        print(f"[*] Threads: {threads}, Timeout: {timeout}s")
        
        results = {}
        for target in targets:
            results[target] = self._scan_host(target, ports, timeout, threads)
        
        # Display results
        for target, open_ports in results.items():
            print(f"\n[+] {target}:")
            for port, service in open_ports:
                print(f"    {port}/tcp open - {service}")
        
        return results
    
    def _parse_targets(self, rhosts: str) -> list:
        """Parse target specification"""
        targets = []
        for part in rhosts.split(","):
            if "-" in part:
                start, end = part.split("-")
                if "." in start:
                    base = ".".join(start.split(".")[:-1])
                    start_ip = int(start.split(".")[-1])
                    end_ip = int(end)
                    for i in range(start_ip, end_ip + 1):
                        targets.append(f"{base}.{i}")
                else:
                    targets.extend(range(int(start), int(end) + 1))
            else:
                targets.append(part)
        return targets
    
    def _parse_ports(self, ports_str: str) -> list:
        """Parse port specification"""
        ports = []
        for part in ports_str.split(","):
            if "-" in part:
                start, end = map(int, part.split("-"))
                ports.extend(range(start, end + 1))
            else:
                ports.append(int(part))
        return ports
    
    def _scan_host(self, target: str, ports: list, timeout: float, max_threads: int) -> list:
        """Scan single host"""
        open_ports = []
        
        def scan_port(port):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(timeout)
                result = sock.connect_ex((target, port))
                if result == 0:
                    service = self._detect_service(sock, port)
                    open_ports.append((port, service))
                sock.close()
            except Exception:
                pass
        
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            executor.map(scan_port, ports)
        
        return sorted(open_ports)
    
    def _detect_service(self, sock: socket.socket, port: int) -> str:
        """Attempt service detection via banner grabbing"""
        common_services = {
            21: "ftp", 22: "ssh", 23: "telnet", 25: "smtp",
            53: "dns", 80: "http", 110: "pop3", 143: "imap",
            443: "https", 445: "smb", 3306: "mysql", 3389: "rdp",
            5432: "postgresql", 8080: "http-proxy", 8443: "https-alt"
        }
        
        try:
            # Try banner grab
            sock.settimeout(2)
            banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
            if banner:
                return banner[:50]
        except:
            pass
        
        return common_services.get(port, "unknown")
