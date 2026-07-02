# ZAIYAN — Advanced Exploitation Framework

> **Made by Anonymous-beta for Zaiyan**

<p align="center">
  <img src="image-1.jpg" width="200" alt="ZAIYAN Logo">
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#modules">Modules</a> •
  <a href="#web-interface">Web Interface</a> •
  <a href="#architecture">Architecture</a>
</p>

---

## Overview

ZAIYAN is a next-generation exploitation framework designed to surpass existing solutions in modularity, usability, and capability. Built with a modern web frontend and cross-platform compatibility, ZAIYAN provides a seamless experience for security professionals operating in diverse environments.

**Key Highlights:**
- Real-time collaboration via WebSocket-powered interface
- Architecture-aware payload generation (multi-format output)
- Advanced evasion techniques (AMSI/ETW bypasses, sandbox detection)
- Full Termux-native support for mobile operations
- Highly extensible module system with dynamic discovery

---

## Features

### Core Capabilities
- **Exploit Modules**: Windows, Linux, Android, and Web exploits
- **Payload Generation**: x86, x64, ARM, ARM64 — outputs: EXE, ELF, APK, Python, PowerShell, C#
- **Auxiliary Tools**: Port scanning, enumeration, DoS attacks
- **Post-Exploitation**: Persistence, credential harvesting, lateral movement
- **Encoders**: XOR, Shikata Ga Nai polymorphic encoding
- **Evasion**: AMSI bypass, ETW bypass, sandbox detection & evasion

### Web Interface
- Dark-themed, elegant violet/rose aesthetic
- Real-time terminal with Socket.IO
- Interactive module browser with search & filtering
- Visual payload builder
- Session management dashboard
- Loot tracking system

### Platform Support

| Platform | Status     | Notes                     |
|----------|------------|---------------------------|
| Linux    | ✅ Full    | Native support            |
| Termux   | ✅ Full    | Android compatibility     |
| Windows  | ✅ Full    | WSL or native Python      |
| macOS    | ⚠️ Partial | Limited testing           |

---

## Installation

### Quick Start (Linux)

```bash
git clone https://github.com/Anonymous-beta/zaiyan.git
cd zaiyan
chmod +x scripts/install_linux.sh
./scripts/install_linux.sh
zaiyan --web
```
### Termux (Android)
```bash
pkg install git
git clone https://github.com/Anonymous-beta/zaiyan.git
cd zaiyan
chmod +x scripts/install_termux.sh
./scripts/install_termux.sh
zaiyan --web
```
### Manual Installation
```
pip install -r requirements.txt
python zaiyan.py --web
```
## Example commands:
```
zaiyan > search eternalblue
zaiyan > use exploit/windows/ms17_010
zaiyan (ms17_010) > set RHOST 192.168.1.105
zaiyan (ms17_010) > set LHOST 192.168.1.100
zaiyan (ms17_010) > run
```
### Web Interface
```
zaiyan --web --host 0.0.0.0 --port 5000
Access at: http://localhost:5000
```
## Web Interface
The ZAIYAN web interface offers a modern, intuitive alternative to traditional terminal-based frameworks:
Dashboard — Real-time statistics and activity feed
Modules — Visual browser with powerful filtering
Payloads — Point-and-click payload builder
Sessions — Active session management & interaction
Terminal — Full browser-based interactive shell
Loot — Centralized credential and data storage
## Contributing
Fork the repository
Create a feature branch
Submit a pull request
Module Requirements:
Must include NAME, DESCRIPTION, AUTHOR, and PLATFORM attributes
Proper option definitions
Robust error handling in execute()
### Disclaimer
ZAIYAN is intended for authorized security testing and research only. Users are responsible for complying with all applicable laws and regulations. The authors assume no liability for misuse.
License
## MIT License — See LICENSE file.
�
Made by Anonymous-beta for Zaiyan (I DEY QUICK VEX OOO SO BETTER STAR MY REPO)
