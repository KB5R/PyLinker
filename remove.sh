#!/bin/bash
set -e

BIN_NAME="pylink"
INSTALL_DIR="$HOME/.local/bin"
BIN_PATH="$INSTALL_DIR/$BIN_NAME"

echo "[*] Delete bin..."

if [ -f "$BIN_PATH" ]; then
    rm "$BIN_PATH"
    echo "Delet: $BIN_PATH"
else
    echo "Bin not found: $BIN_PATH"
fi

echo "Ready."