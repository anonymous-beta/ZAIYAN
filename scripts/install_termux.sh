#!/bin/bash
# ZAIYAN Installation Script for Termux
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
echo -e "${CYAN}[*] ZAIYAN Termux Installer${NC}"
echo ""

# Check Termux environment
if [ -z "$TERMUX_VERSION" ] && [ ! -d "/data/data/com.termux/files/usr" ]; then
    echo -e "${RED}[-] Not running in Termux environment${NC}"
    exit 1
fi

PREFIX="/data/data/com.termux/files/usr"
ZAIYAN_DIR="$HOME/zaiyan"

echo -e "${CYAN}[*] Updating packages...${NC}"
pkg update -y
pkg upgrade -y

echo -e "${CYAN}[*] Installing dependencies...${NC}"
pkg install -y python python-pip git clang openssl libffi

echo -e "${CYAN}[*] Installing Python packages...${NC}"
pip install --upgrade pip
pip install flask flask-socketio requests cryptography psutil pyopenssl pynacl colorama rich prompt-toolkit

# Optional packages
pip install paramiko scapy pefile 2>/dev/null || echo -e "${RED}[-] Some optional packages failed${NC}"

echo -e "${CYAN}[*] Setting up ZAIYAN directory...${NC}"
mkdir -p "$ZAIYAN_DIR"
cd "$ZAIYAN_DIR"

echo -e "${CYAN}[*] Cloning ZAIYAN repository...${NC}"
if [ -d ".git" ]; then
    git pull
else
    echo -e "${CYAN}[*] Please place ZAIYAN files in $ZAIYAN_DIR${NC}"
fi

echo -e "${CYAN}[*] Setting up storage permissions...${NC}"
termux-setup-storage 2>/dev/null || true

echo -e "${CYAN}[*] Creating launcher...${NC}"
cat > "$PREFIX/bin/zaiyan" << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
cd $HOME/zaiyan
python zaiyan.py "$@"
EOF
chmod +x "$PREFIX/bin/zaiyan"

echo ""
echo -e "${GREEN}[+] ZAIYAN installed successfully!${NC}"
echo -e "${CYAN}[*] Usage:${NC}"
echo -e "    zaiyan --web       # Start web interface"
echo -e "    zaiyan --cli       # Start CLI mode"
echo -e "    cd $ZAIYAN_DIR && python zaiyan.py --web"
echo ""
echo -e "${MAGENTA}Made by Anonymous-beta for Zaiyan${NC}"
