import random
from core.module_base import ZaiyanModule

class XOREncoder(ZaiyanModule):
    NAME = "xor_encoder"
    DESCRIPTION = "XOR encoder with variable key length"
    AUTHOR = "Anonymous-beta"
    MODULE_TYPE = "encoder"
    PLATFORM = ["generic"]
    
    def _setup_options(self):
        self.options = {
            "SHELLCODE": {
                "description": "Shellcode bytes to encode (hex)",
                "required": True,
                "value": ""
            },
            "KEY_LENGTH": {
                "description": "XOR key length in bytes",
                "required": False,
                "value": "16"
            }
        }
    
    def execute(self):
        """XOR encode shellcode"""
        shellcode_hex = self.get_option("SHELLCODE")
        key_len = int(self.get_option("KEY_LENGTH"))
        
        if not shellcode_hex:
            print("[-] No shellcode provided")
            return False
        
        try:
            shellcode = bytes.fromhex(shellcode_hex.replace("0x", "").replace(" ", ""))
        except ValueError:
            print("[-] Invalid hex string")
            return False
        
        # Generate random key
        key = bytes([random.randint(1, 255) for _ in range(key_len)])
        
        # XOR encode
        encoded = bytearray()
        for i, b in enumerate(shellcode):
            encoded.append(b ^ key[i % len(key)])
        
        # Generate decoder stub (x64)
        decoder = self._build_decoder(key_len, len(shellcode))
        
        print(f"[+] Original size: {len(shellcode)}")
        print(f"[+] Encoded size: {len(encoded)}")
        print(f"[+] Key: {key.hex()}")
        
        return {
            "key": key.hex(),
            "encoded": bytes(encoded).hex(),
            "decoder": decoder.hex(),
            "full_payload": (decoder + key + bytes(encoded)).hex()
        }
    
    def _build_decoder(self, key_len: int, data_len: int) -> bytes:
        """Build x64 XOR decoder stub"""
        # Simplified decoder: rsi = key, rdi = data, rcx = length
        decoder = bytes([
            0x48, 0x31, 0xc9,                    # xor rcx, rcx
            0x48, 0x31, 0xdb,                    # xor rbx, rbx
            0xeb, 0x10,                          # jmp to call
            0x5e,                                # pop rsi (data addr)
            0x48, 0x89, 0xf7,                    # mov rdi, rsi
            0x48, 0x01, 0xcf,                    # add rdi, rcx
            0x8a, 0x1c, 0x37,                    # mov bl, [rdi]
            0x48, 0x31, 0xd8,                    # xor rax, rbx
            0x88, 0x04, 0x37,                    # mov [rdi], al
            0x48, 0xff, 0xc1,                    # inc rcx
            0xeb, 0xf0,                          # jmp loop
            0xe8, 0xeb, 0xff, 0xff, 0xff       # call back
        ])
        return decoder
