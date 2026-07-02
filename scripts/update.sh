#!/bin/bash
# ZAIYAN Update Script
# Made by Anonymous-beta for Zaiyan

set -e

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ZAIYAN_DIR="$HOME/zaiyan"

echo -e "${CYAN}[*] ZAIYAN Updater${NC}"

if [ ! -d "$ZAIYAN_DIR" ]; then
    echo -e "${YELLOW}[!] ZAIYAN not found at $ZAIYAN_DIR${NC}"
    exit 1
fi

cd "$ZAIYAN_DIR"

# Check if git repo
if [ -d ".git" ]; then
    echo -e "${CYAN}[*] Pulling latest changes...${NC}"
    git pull origin main 2>/dev/null || git pull origin master 2>/dev/null || \
        echo -e "${YELLOW}[!] Git pull failed, updating manually${NC}"
else
    echo -e "${YELLOW}[!] Not a git repository. Manual update required.${NC}"
fi

# Update Python packages
echo -e "${CYAN}[*] Updating Python packages...${NC}"
pip3 install --upgrade flask flask-socketio requests cryptography psutil pyopenssl pynacl colorama rich prompt-toolkit 2>/dev/null || \
    pip install --upgrade flask flask-socketio requests cryptography psutil pyopenssl pynacl colorama rich prompt-toolkit

echo -e "${GREEN}[+] ZAIYAN updated successfully!${NC}"
echo -e "${CYAN}[*] Restart ZAIYAN to apply changes${NC}"
