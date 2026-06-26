#!/bin/bash

echo "=========================================="
echo "         LAZARUS Installer"
echo "=========================================="
echo

# Check for root privileges
if [ "$EUID" -ne 0 ]; then
    echo "[!] Please run this installer as root."
    echo "    Example: sudo ./install.sh"
    exit 1
fi

echo "[+] Updating package list..."
apt update

echo
echo "[+] Installing required packages..."
apt install -y python3 nmap dsniff xterm

echo
echo "[+] Setting execution permissions..."
chmod +x LAZARUS_EN/lazarus.py
chmod +x LAZARUS_ES/lazarus.py

echo
echo "=========================================="
echo " Installation completed successfully!"
echo "=========================================="
echo
echo "Run the English version:"
echo "sudo python3 LAZARUS_EN/lazarus.py"
echo
echo "Run the Spanish version:"
echo "sudo python3 LAZARUS_ES/lazarus.py"
echo
