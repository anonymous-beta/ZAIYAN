import os
import sys
import importlib
import importlib.util
from pathlib import Path
from typing import Dict, List, Optional, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from core.database import ModuleDatabase
from core.session_manager import SessionManager
from core.payload_generator import PayloadGenerator
from core.evasion_engine import EvasionEngine

console = Console()

class ZaiyanFramework:
    def __init__(self):
        self.modules = {}
        self.module_paths = {
            "exploit": "modules/exploits",
            "payload": "modules/payloads",
            "auxiliary": "modules/auxiliary",
            "post": "modules/post",
            "encoder": "modules/encoders",
            "nop": "modules/nop",
            "evasion": "modules/evasion"
        }
        self.db = ModuleDatabase()
        self.sessions = SessionManager()
        self.payload_gen = PayloadGenerator()
        self.evasion = EvasionEngine()
        self.current_module = None
        self.global_options = {
            "LHOST": "",
            "LPORT": "4444",
            "RHOST": "",
            "RPORT": "",
            "TARGETURI": "/",
            "SSL": "false"
        }
        self._load_all_modules()

    def _load_all_modules(self):
        """Dynamically discover and load all modules"""
        base_path = Path(__file__).parent.parent

        for module_type, rel_path in self.module_paths.items():
            module_dir = base_path / rel_path
            if not module_dir.exists():
                continue

            for py_file in module_dir.rglob("*.py"):
                if py_file.name.startswith("__"):
                    continue

                try:
                    spec = importlib.util.spec_from_file_location(
                        f"zaiyan.{rel_path.replace('/', '.')}.{py_file.stem}",
                        py_file
                    )
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    # Look for module class
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (isinstance(attr, type) and
                            hasattr(attr, "MODULE_TYPE") and
                            attr.MODULE_TYPE == module_type):

                            instance = attr()
                            full_name = f"{module_type}/{py_file.parent.relative_to(module_dir)}/{py_file.stem}"
                            full_name = full_name.replace("//", "/").rstrip("/")
                            self.modules[full_name] = instance
                            self.db.register_module(full_name, instance)

                except Exception as e:
                    console.print(f"[red][!] Failed to load {py_file}: {e}[/red]")

        console.print(f"[green][+] Loaded {len(self.modules)} modules[/green]")

    def search_modules(self, keyword: str = "") -> List[str]:
        """Search modules by keyword"""
        results = []
        for name, module in self.modules.items():
            if keyword.lower() in name.lower() or keyword.lower() in str(module).lower():
                results.append(name)
        return results

    def use_module(self, module_name: str) -> bool:
        """Select a module for use"""
        # Fuzzy match
        matches = [k for k in self.modules.keys() if module_name.lower() in k.lower()]
        if not matches:
            console.print(f"[red][!] No module matching '{module_name}'[/red]")
            return False

        if len(matches) > 1:
            console.print("[yellow][*] Multiple matches:[/yellow]")
            for m in matches:
                console.print(f"    {m}")
            return False

        self.current_module = self.modules[matches[0]]
        console.print(f"[green][+] Using {matches[0]}[/green]")
        return True

    def show_options(self):
        """Display current module options"""
        if not self.current_module:
            console.print("[yellow][*] No module selected. Showing global options:[/yellow]")
            opts = self.global_options
        else:
            opts = self.current_module.options

        table = Table(title="Module Options", show_header=True, header_style="bold magenta")
        table.add_column("Name", style="cyan")
        table.add_column("Current Setting", style="green")
        table.add_column("Required", style="red")
        table.add_column("Description", style="white")

        for name, config in opts.items():
            if isinstance(config, dict):
                table.add_row(
                    name,
                    str(config.get("value", "")),
                    "Yes" if config.get("required", False) else "No",
                    config.get("description", "")
                )
            else:
                table.add_row(name, str(config), "No", "Global option")

        console.print(table)

    def set_option(self, name: str, value: str):
        """Set an option value"""
        if self.current_module and name in self.current_module.options:
            self.current_module.options[name]["value"] = value
            console.print(f"[green][+] {name} => {value}[/green]")
        elif name in self.global_options:
            self.global_options[name] = value
            console.print(f"[green][+] {name} => {value} (global)[/green]")
        else:
            console.print(f"[red][!] Unknown option: {name}[/red]")

    def run_module(self) -> Any:
        """Execute the current module"""
        if not self.current_module:
            console.print("[red][!] No module selected[/red]")
            return None

        # Validate required options
        missing = []
        for name, config in self.current_module.options.items():
            if config.get("required", False) and not config.get("value"):
                missing.append(name)

        if missing:
            console.print(f"[red][!] Missing required options: {', '.join(missing)}[/red]")
            return None

        console.print(Panel.fit(
            f"[bold magenta]Executing {self.current_module.__class__.__name__}...[/bold magenta]",
            border_style="magenta"
        ))

        try:
            result = self.current_module.execute()
            if result:
                self.sessions.register_activity(self.current_module)
            return result
        except Exception as e:
            console.print(f"[red][!] Module execution failed: {e}[/red]")
            return None

    def generate_payload(self, payload_type: str, fmt: str, **kwargs) -> bytes:
        """Generate a payload with optional evasion"""
        raw = self.payload_gen.generate(payload_type, **kwargs)

        if kwargs.get("evade", False):
            raw = self.evasion.apply(raw, kwargs.get("evasion_type", "amsi"))

        return self.payload_gen.format_payload(raw, fmt)

    def run_cli(self):
        """Interactive CLI loop"""
        while True:
            try:
                prompt = "zaiyan > "
                if self.current_module:
                    prompt = f"zaiyan ({self.current_module.__class__.__name__}) > "

                cmd = console.input(f"[bold magenta]{prompt}[/bold magenta]").strip()

                if not cmd:
                    continue
                elif cmd == "exit" or cmd == "quit":
                    break
                elif cmd == "help":
                    self._show_help()
                elif cmd.startswith("search "):
                    self._show_search(cmd[7:])
                elif cmd.startswith("use "):
                    self.use_module(cmd[4:])
                elif cmd == "show options":
                    self.show_options()
                elif cmd.startswith("set "):
                    parts = cmd[4:].split(" ", 1)
                    if len(parts) == 2:
                        self.set_option(parts[0], parts[1])
                elif cmd == "run" or cmd == "exploit":
                    self.run_module()
                elif cmd == "sessions":
                    self.sessions.list_sessions()
                elif cmd == "banner":
                    console.print(BANNER)
                else:
                    console.print(f"[red][!] Unknown command: {cmd}[/red]")

            except KeyboardInterrupt:
                console.print("\n[yellow][*] Use 'exit' to quit[/yellow]")
            except EOFError:
                break

    def _show_help(self):
        help_text = """
        Core Commands
        =============
        Command        Description
        -------        -----------
        help           Show this help menu
        search         Search for modules
        use            Select a module
        show options   Show module options
        set            Set an option value
        run/exploit    Execute the module
        sessions       List active sessions
        banner         Display banner
        exit/quit      Exit ZAIYAN
        """
        console.print(help_text)

    def _show_search(self, keyword: str):
        results = self.search_modules(keyword)
        if not results:
            console.print(f"[yellow][*] No results for '{keyword}'[/yellow]")
            return

        table = Table(title=f"Search Results: '{keyword}'", show_header=True)
        table.add_column("Module", style="cyan")
        table.add_column("Type", style="magenta")
        table.add_column("Description", style="white")

        for r in results:
            module = self.modules[r]
            desc = getattr(module, "DESCRIPTION", "No description")
            mtype = getattr(module, "MODULE_TYPE", "unknown")
            table.add_row(r, mtype, desc)

        console.print(table)
