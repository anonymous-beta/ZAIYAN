import random
from core.module_base import ZaiyanModule

class ShikataGaNai(ZaiyanModule):
    NAME = "shikata_ga_nai"
    DESCRIPTION = "Polymorphic XOR additive feedback encoder"
    AUTHOR = "Anonymous-beta"
    MODULE_TYPE = "encoder"
    PLATFORM = ["x86", "x64"]
    
    def _setup_options(self):
        self.options = {
            "SHELLCODE": {
                "description": "Shellcode to encode (hex)",
                "required": True,
                "value": ""
            },
            "ITERATIONS": {
                "description": "Encoding iterations",
                "required": False,
                "value": "1"
            }
        }
    
    def execute(self):
        """Apply Shikata Ga Nai encoding"""
        shellcode_hex = self.get_option("SHELLCODE")
        iterations = int(self.get_option("ITERATIONS"))
        
        if not shellcode_hex:
            print("[-] No shellcode provided")
            return False
        
        try:
            shellcode = bytes.fromhex(shellcode_hex.replace("0x", "").replace(" ", ""))
        except ValueError:
            print("[-] Invalid hex string")
            return False
        
        # Simplified SGN: XOR with rotating key + additive feedback
        key = random.randint(1, 255)
        encoded = bytearray(shellcode)
        
        for _ in range(iterations):
            new_encoded = bytearray()
            current_key = key
            for b in encoded:
                xored = b ^ current_key
                new_encoded.append(xored)
                current_key = (current_key + xored) % 256
            
            encoded = new_encoded
            key = (key + 1) % 256
        
        print(f"[+] Encoded {len(shellcode)} bytes in {iterations} iteration(s)")
        print(f"[+] Final key: {key}")
        
        return {
            "iterations": iterations,
            "key": key,
            "encoded": bytes(encoded).hex()
        }
