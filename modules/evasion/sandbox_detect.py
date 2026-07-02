import os
import time
from core.module_base import ZaiyanModule

class SandboxDetect(ZaiyanModule):
    NAME = "sandbox_detect"
    DESCRIPTION = "Detect and evade sandbox/VM environments"
    AUTHOR = "Anonymous-beta"
    MODULE_TYPE = "evasion"
    PLATFORM = ["windows", "linux"]
    
    def _setup_options(self):
        self.options = {
            "ACTION": {
                "description": "Action on detect: exit, sleep, fake",
                "required": False,
                "value": "exit"
            },
            "CHECKS": {
                "description": "Checks to run: all, vm, processes, sleep, domain",
                "required": False,
                "value": "all"
            }
        }
    
    def execute(self):
        """Run sandbox detection checks"""
        action = self.get_option("ACTION")
        checks = self.get_option("CHECKS")
        
        results = {
            "is_sandbox": False,
            "indicators": []
        }
        
        if checks in ["all", "vm"]:
            vm_result = self._check_vm_artifacts()
            results["indicators"].extend(vm_result)
        
        if checks in ["all", "processes"]:
            proc_result = self._check_processes()
            results["indicators"].extend(proc_result)
        
        if checks in ["all", "sleep"]:
            sleep_result = self._check_sleep_acceleration()
            results["indicators"].append(sleep_result)
        
        if checks in ["all", "domain"]:
            domain_result = self._check_domain()
            results["indicators"].append(domain_result)
        
        results["is_sandbox"] = len([i for i in results["indicators"] if i.get("detected")]) > 0
        
        print(f"[*] Checks completed: {len(results['indicators'])} indicators")
        print(f"[*] Sandbox detected: {results['is_sandbox']}")
        
        for ind in results["indicators"]:
            status = "[!]" if ind.get("detected") else "[+]"
            print(f"{status} {ind['name']}: {ind['detail']}")
        
        if results["is_sandbox"]:
            self._take_action(action)
        
        return results
    
    def _check_vm_artifacts(self):
        """Check for VM artifacts"""
        indicators = []
        
        # Check common VM files
        vm_files = [
            "C:\\windows\\System32\\Drivers\\Vmmouse.sys",
            "C:\\windows\\System32\\Drivers\\vm3dgl.dll",
            "C:\\windows\\System32\\Drivers\\vmdum.dll",
            "C:\\windows\\System32\\Drivers\\vm3dver.dll",
            "C:\\windows\\System32\\Drivers\\vmtray.dll",
            "C:\\windows\\System32\\Drivers\\vmci.sys",
            "C:\\windows\\System32\\Drivers\\vmusbmouse.sys",
            "C:\\windows\\System32\\Drivers\\vmx_svga.sys",
            "C:\\windows\\System32\\Drivers\\VBoxMouse.sys",
            "C:\\windows\\System32\\Drivers\\VBoxGuest.sys",
            "C:\\windows\\System32\\Drivers\\VBoxSF.sys",
            "C:\\windows\\System32\\Drivers\\VBoxVideo.sys",
            "/usr/bin/VBoxClient",
            "/usr/bin/VBoxControl"
        ]
        
        for f in vm_files:
            if os.path.exists(f):
                indicators.append({
                    "name": "VM File Artifact",
                    "detected": True,
                    "detail": f"Found: {f}"
                })
                return indicators
        
        # Check MAC address prefixes
        vm_macs = ["00:05:69", "00:0C:29", "00:1C:14", "00:50:56", "08:00:27"]
        
        indicators.append({
            "name": "VM File Artifact",
            "detected": False,
            "detail": "No VM files found"
        })
        
        return indicators
    
    def _check_processes(self):
        """Check for analysis processes"""
        indicators = []
        
        analysis_procs = [
            "vmsrvc.exe", "vmusrvc.exe", "vboxtray.exe", "vmtoolsd.exe",
            "vmwaretray.exe", "vmwareuser.exe", "VGAuthService.exe",
            "vmacthlp.exe", "vmtoolsd.exe", "xenservice.exe",
            "qemu-ga.exe", "wireshark.exe", "procmon.exe", "processhacker.exe",
            "autoruns.exe", "autorunsc.exe", "filemon.exe", "regmon.exe",
            "idaq.exe", "idaq64.exe", "ImmunityDebugger.exe", "ollydbg.exe",
            "x64dbg.exe", "x32dbg.exe", "windbg.exe", "httpdebuggerui.exe"
        ]
        
        try:
            import psutil
            running = [p.name().lower() for p in psutil.process_iter(['name'])]
            
            for proc in analysis_procs:
                if proc.lower() in running:
                    indicators.append({
                        "name": "Analysis Process",
                        "detected": True,
                        "detail": f"Found: {proc}"
                    })
                    return indicators
        except ImportError:
            pass
        
        indicators.append({
            "name": "Analysis Process",
            "detected": False,
            "detail": "No analysis tools detected"
        })
        
        return indicators
    
    def _check_sleep_acceleration(self):
        """Detect sleep acceleration (time compression)"""
        start = time.time()
        time.sleep(2)
        elapsed = time.time() - start
        
        # If sleep took significantly less than 2 seconds, time is accelerated
        if elapsed < 1.5:
            return {
                "name": "Sleep Acceleration",
                "detected": True,
                "detail": f"Expected 2s, got {elapsed:.2f}s"
            }
        
        return {
            "name": "Sleep Acceleration",
            "detected": False,
            "detail": f"Sleep normal: {elapsed:.2f}s"
        }
    
    def _check_domain(self):
        """Check if machine is domain-joined"""
        try:
            import socket
            domain = socket.getfqdn()
            if domain == socket.gethostname() or "sandbox" in domain.lower():
                return {
                    "name": "Domain Check",
                    "detected": True,
                    "detail": f"Standalone/sandbox hostname: {domain}"
                }
            return {
                "name": "Domain Check",
                "detected": False,
                "detail": f"Domain-joined: {domain}"
            }
        except:
            return {
                "name": "Domain Check",
                "detected": False,
                "detail": "Check failed"
            }
    
    def _take_action(self, action: str):
        """Take evasive action"""
        if action == "exit":
            print("[!] Exiting due to sandbox detection")
            os._exit(0)
        elif action == "sleep":
            print("[*] Sleeping to evade analysis...")
            time.sleep(300)  # 5 minutes
        elif action == "fake":
            print("[*] Running fake benign operations...")
            # Perform fake calculations
            for _ in range(1000000):
                _ = _ * _
        else:
            print(f"[-] Unknown action: {action}")
