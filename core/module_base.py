from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class ZaiyanModule(ABC):
    """Base class for all ZAIYAN modules"""
    
    MODULE_TYPE = "base"
    NAME = "base_module"
    DESCRIPTION = "Base module - do not use directly"
    AUTHOR = "Anonymous-beta"
    PLATFORM = ["generic"]
    TARGETS = []
    
    def __init__(self):
        self.options = {}
        self.results = {}
        self._setup_options()
    
    @abstractmethod
    def _setup_options(self):
        """Define module options. Override in subclass."""
        pass
    
    @abstractmethod
    def execute(self) -> Any:
        """Execute the module. Must be implemented by subclass."""
        pass
    
    def get_option(self, name: str) -> Any:
        """Get option value"""
        if name in self.options:
            return self.options[name].get("value", self.options[name].get("default", ""))
        return None
    
    def set_option(self, name: str, value: Any):
        """Set option value"""
        if name in self.options:
            self.options[name]["value"] = value
    
    def check(self) -> bool:
        """Check if target is vulnerable. Override for exploit modules."""
        return True
    
    def report(self, data: Dict[str, Any]):
        """Store results"""
        self.results.update(data)
    
    def __str__(self):
        return f"{self.NAME} - {self.DESCRIPTION}"

class ExploitModule(ZaiyanModule):
    """Base class for exploit modules"""
    MODULE_TYPE = "exploit"
    
    def _setup_options(self):
        self.options = {
            "RHOST": {"description": "Target address", "required": True, "value": ""},
            "RPORT": {"description": "Target port", "required": True, "value": ""},
            "TARGETURI": {"description": "Target URI", "required": False, "value": "/"},
            "SSL": {"description": "Use SSL", "required": False, "value": "false"},
            "LHOST": {"description": "Local host for callback", "required": False, "value": ""},
            "LPORT": {"description": "Local port for callback", "required": False, "value": "4444"}
        }

class PayloadModule(ZaiyanModule):
    """Base class for payload modules"""
    MODULE_TYPE = "payload"
    
    def _setup_options(self):
        self.options = {
            "LHOST": {"description": "Callback host", "required": True, "value": ""},
            "LPORT": {"description": "Callback port", "required": True, "value": "4444"},
            "FORMAT": {"description": "Output format (exe/elf/apk/raw)", "required": True, "value": "raw"},
            "ARCH": {"description": "Architecture (x86/x64/arm/arm64)", "required": False, "value": "x64"},
            "ENCODER": {"description": "Encoder to use", "required": False, "value": "none"},
            "EVASION": {"description": "Apply evasion techniques", "required": False, "value": "false"}
        }

class AuxiliaryModule(ZaiyanModule):
    """Base class for auxiliary modules"""
    MODULE_TYPE = "auxiliary"
    
    def _setup_options(self):
        self.options = {
            "RHOSTS": {"description": "Target range", "required": True, "value": ""},
            "THREADS": {"description": "Number of threads", "required": False, "value": "10"},
            "TIMEOUT": {"description": "Connection timeout", "required": False, "value": "5"}
        }

class PostModule(ZaiyanModule):
    """Base class for post-exploitation modules"""
    MODULE_TYPE = "post"
    
    def _setup_options(self):
        self.options = {
            "SESSION": {"description": "Session ID", "required": True, "value": ""},
            "VERBOSE": {"description": "Verbose output", "required": False, "value": "true"}
        }
