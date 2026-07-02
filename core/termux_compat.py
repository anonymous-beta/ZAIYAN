import os
import sys
import subprocess
from pathlib import Path

class TermuxCompat:
    """Termux/Android compatibility layer"""
    
    TERMUX_PREFIX = "/data/data/com.termux/files/usr"
    
    def is_termux(self) -> bool:
        """Detect Termux environment"""
        return (
            os.environ.get("TERMUX_VERSION") is not None or
            self.TERMUX_PREFIX in os.environ.get("PREFIX", "") or
            os.path.exists(self.TERMUX_PREFIX)
        )
    
    def setup_environment(self):
        """Configure environment for Termux"""
        os.environ.setdefault("PREFIX", self.TERMUX_PREFIX)
        os.environ.setdefault("TMPDIR", "/data/data/com.termux/files/usr/tmp")
        
        # Adjust paths
        if self.TERMUX_PREFIX not in os.environ.get("PATH", ""):
            os.environ["PATH"] = f"{self.TERMUX_PREFIX}/bin:" + os.environ.get("PATH", "")
    
    def install_package(self, package: str) -> bool:
        """Install package via pkg/apt"""
        try:
            result = subprocess.run(
                ["pkg", "install", "-y", package],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except FileNotFoundError:
            try:
                result = subprocess.run(
                    ["apt", "install", "-y", package],
                    capture_output=True,
                    text=True
                )
                return result.returncode == 0
            except Exception:
                return False
    
    def check_storage(self) -> bool:
        """Check Termux storage permissions"""
        storage_path = Path("/data/data/com.termux/files/home/storage")
        return storage_path.exists()
    
    def get_storage_path(self) -> Path:
        """Get accessible storage path"""
        if self.check_storage():
            return Path("/data/data/com.termux/files/home/storage/shared")
        return Path.home()
    
    def fix_shebang(self, script_path: str):
        """Fix Python shebang for Termux"""
        path = Path(script_path)
        if not path.exists():
            return
        
        content = path.read_text()
        if content.startswith("#!/usr/bin/python") or content.startswith("#!/usr/bin/env python"):
            content = content.replace("#!/usr/bin/python", "#!" + sys.executable)
            content = content.replace("#!/usr/bin/env python", "#!" + sys.executable)
            path.write_text(content)
