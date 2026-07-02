#!/usr/bin/env python3
# ZAIYAN — Advanced Exploitation Framework
# Made by Anonymous-beta for Zaiyan

import sys
import os
import argparse
from pathlib import Path

# Add core to path
CORE_DIR = Path(__file__).parent / "core"
sys.path.insert(0, str(CORE_DIR))

from core.framework import ZaiyanFramework
from core.termux_compat import TermuxCompat
from web.server import start_web_server

BANNER = r"""
    ███████╗ █████╗ ██╗██╗   ██╗ █████╗ ███╗   ██╗
    ╚══███╔╝██╔══██╗██║╚██╗ ██╔╝██╔══██╗████╗  ██║
      ███╔╝ ███████║██║ ╚████╔╝ ███████║██╔██╗ ██║
     ███╔╝  ██╔══██║██║  ╚██╔╝  ██╔══██║██║╚██╗██║
    ███████╗██║  ██║██║   ██║   ██║  ██║██║ ╚████║
    ╚══════╝╚═╝  ╚═╝╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═══╝
    
    [ Advanced Exploitation Framework v1.0.0 ]
    Made by Anonymous-beta for Zaiyan
    
    Type 'help' for available commands
"""

def main():
    parser = argparse.ArgumentParser(description="ZAIYAN Framework")
    parser.add_argument("--web", action="store_true", help="Start web interface")
    parser.add_argument("--host", default="0.0.0.0", help="Web host")
    parser.add_argument("--port", default="5000", help="Web port")
    parser.add_argument("--cli", action="store_true", help="Force CLI mode")
    
    args = parser.parse_args()
    
    # Termux environment detection
    termux = TermuxCompat()
    if termux.is_termux():
        print("[*] Termux environment detected — applying compatibility layer")
        termux.setup_environment()
    
    if args.web or not args.cli:
        print(BANNER)
        print("[*] Starting ZAIYAN Web Interface...")
        start_web_server(host=args.host, port=int(args.port))
    else:
        print(BANNER)
        framework = ZaiyanFramework()
        framework.run_cli()

if __name__ == "__main__":
    main()
