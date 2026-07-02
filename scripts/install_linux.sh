#!/bin/bash
# ZAIYAN Installation Script for Linux
# Made by Anonymous-beta for Zaiyan

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${MAGENTA}"
echo "    ███████╗ █████╗ ██╗██╗   ██╗ █████╗ ███╗   ██╗"
echo "    ╚══███╔╝██╔══██╗██║╚██╗ ██╔╝██╔══██╗████╗  ██║"
echo "      ███╔╝ ███████║██║ ╚████╔╝ ███████║██╔██╗ ██║"
echo "     ███╔╝  ██╔══██║██║  ╚██╔╝  ██╔══██║██║╚██╗██║"
echo "    ███████╗██║  ██║██║   ██║   ██║  ██║██║ ╚████║"
echo "    ╚══════╝╚═╝  ╚═╝╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═══╝"
echo -e "${NC}"
echo -e "${CYAN}[*] ZAIYAN Linux Installer${NC}"
echo ""

# Detect distribution
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO=$ID
else
    DISTRO="unknown"
fi

echo -e "${CYAN}[*] Detected distribution: $DISTRO${NC}"

# Install system dependencies
echo -e "${CYAN}[*] Installing system dependencies...${NC}"

case $DISTRO in
    ubuntu|debian)
        sudo apt-get update
        sudo apt-get install -y python3 python3-pip python3-venv git gcc libssl-dev libffi-dev
        ;;
    fedora|rhel|centos)
        sudo dnf install -y python3 python3-pip git gcc openssl-devel libffi-devel
        ;;
    arch|manjaro)
        sudo pacman -Sy --noconfirm python python-pip git gcc openssl libffi
        ;;
    alpine)
        sudo apk add --no-cache python3 py3-pip git gcc musl-dev openssl-dev libffi-dev
        ;;
    *)
        echo -e "${RED}[-] Unknown distribution. Please install manually:${NC}"
        echo "    python3, python3-pip, git, gcc, libssl-dev, libffi-dev"
        exit 1
        ;;
esac

# Install Python packages
echo -e "${CYAN}[*] Installing Python packages...${NC}"
pip3 install --upgrade pip
pip3 install flask flask-socketio requests cryptography psutil pyopenssl pynacl colorama rich prompt-toolkit

# Optional packages
pip3 install paramiko scapy pefile capstone keystone-engine 2>/dev/null || \
    echo -e "${RED}[-] Some optional packages failed (install manually if needed)${NC}"

# Setup ZAIYAN
ZAIYAN_DIR="$HOME/zaiyan"
mkdir -p "$ZAIYAN_DIR"
cd "$ZAIYAN_DIR"

echo -e "${CYAN}[*] Setting up ZAIYAN...${NC}"

# Create launcher
sudo tee /usr/local/bin/zaiyan > /dev/null << 'EOF'
#!/usr/bin/env bash
cd $HOME/zaiyan
python3 zaiyan.py "$@"
EOF
sudo chmod +x /usr/local/bin/zaiyan

echo ""
echo -e "${GREEN}[+] ZAIYAN installed successfully!${NC}"
echo -e "${CYAN}[*] Usage:${NC}"
echo -e "    zaiyan --web       # Start web interface (http://localhost:5000)"
echo -e "    zaiyan --cli       # Start CLI mode"
echo -e "    zaiyan --web --host 0.0.0.0 --port 8080"
echo ""
echo -e "${MAGENTA}Made by Anonymous-beta for Zaiyan${NC}"
