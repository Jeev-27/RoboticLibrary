#!/bin/bash
set -e

echo "Installing QR scanning dependencies for Week 10..."
apt update
apt install -y python3-pip libzbar0
pip3 install pyzbar

echo "Done. QR scanner uses pyzbar and publishes to /qr_scan_result."
