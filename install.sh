#!/bin/bash
set -e

REPO="KB5R/PyLinker"
BIN_NAME="pylink"
INSTALL_DIR="$HOME/.local/bin"

echo "[*] Dependency check..."
command -v python3 >/dev/null || { echo "❌ Required python3"; exit 1; }
command -v pip >/dev/null || { echo "❌ Required pip"; exit 1; }

echo "git clone repos"
git clone --depth 1 https://github.com/$REPO
cd PyLinker

echo "Install dependency"
pip install -r requirements.txt
pip install pyinstaller

echo "Assembly bin"
pyinstaller --onefile main.py --name "$BIN_NAME"

echo "[*] Copy bin in $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR"
cp dist/"$BIN_NAME" "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/$BIN_NAME"

echo "Install!: $INSTALL_DIR/$BIN_NAME"
echo "Make sure $INSTALL_DIR is in \$PATH"
