#!/bin/bash
#
# LeuitLog v1.0.0 Uninstallation Script
# ======================================
#
# This script removes LeuitLog from the system.
#
# Usage: sudo ./uninstall.sh [--keep-logs] [--keep-config]
#
# Options:
#   --keep-logs    Keep log files in /var/log/leuitlog
#   --keep-config  Keep configuration in /etc/leuitlog

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
INSTALL_DIR="/opt/leuitlog"
CONFIG_DIR="/etc/leuitlog"
LOG_DIR="/var/log/leuitlog"
RUN_DIR="/var/run/leuitlog"
SERVICE_USER="leuitlog"

# Flags
KEEP_LOGS=false
KEEP_CONFIG=false

# Parse arguments
for arg in "$@"; do
    case $arg in
        --keep-logs)
            KEEP_LOGS=true
            ;;
        --keep-config)
            KEEP_CONFIG=true
            ;;
        --help|-h)
            echo "Usage: sudo ./uninstall.sh [--keep-logs] [--keep-config]"
            echo ""
            echo "Options:"
            echo "  --keep-logs    Keep log files in /var/log/leuitlog"
            echo "  --keep-config  Keep configuration in /etc/leuitlog"
            exit 0
            ;;
    esac
done

# Print functions
print_header() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}\n"
}

print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Check root
if [[ $EUID -ne 0 ]]; then
    print_error "This script must be run as root (use sudo)"
    exit 1
fi

print_header "LeuitLog v1.0.0 Uninstaller"

# Confirmation
echo -e "${YELLOW}WARNING: This will remove LeuitLog from your system.${NC}"
if [[ "$KEEP_LOGS" == false ]]; then
    echo -e "${YELLOW}         All log files will be deleted.${NC}"
fi
if [[ "$KEEP_CONFIG" == false ]]; then
    echo -e "${YELLOW}         Configuration will be deleted.${NC}"
fi
echo ""
read -p "Are you sure you want to continue? [y/N] " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Uninstallation cancelled."
    exit 0
fi

# Stop services
print_header "Stopping Services"

if systemctl is-active --quiet leuitlog-webui.service 2>/dev/null; then
    systemctl stop leuitlog-webui.service
    print_status "Stopped leuitlog-webui service"
fi

if systemctl is-active --quiet leuitlog.service 2>/dev/null; then
    systemctl stop leuitlog.service
    print_status "Stopped leuitlog service"
fi

# Disable services
if systemctl is-enabled --quiet leuitlog-webui.service 2>/dev/null; then
    systemctl disable leuitlog-webui.service
    print_status "Disabled leuitlog-webui service"
fi

if systemctl is-enabled --quiet leuitlog.service 2>/dev/null; then
    systemctl disable leuitlog.service
    print_status "Disabled leuitlog service"
fi

# Remove service files
print_header "Removing Files"

if [[ -f /etc/systemd/system/leuitlog.service ]]; then
    rm /etc/systemd/system/leuitlog.service
    print_status "Removed leuitlog.service"
fi

if [[ -f /etc/systemd/system/leuitlog-webui.service ]]; then
    rm /etc/systemd/system/leuitlog-webui.service
    print_status "Removed leuitlog-webui.service"
fi

systemctl daemon-reload
print_status "Reloaded systemd daemon"

# Remove installation directory
if [[ -d "$INSTALL_DIR" ]]; then
    rm -rf "$INSTALL_DIR"
    print_status "Removed $INSTALL_DIR"
fi

# Remove tmpfiles.d entry
if [[ -f /etc/tmpfiles.d/leuitlog.conf ]]; then
    rm /etc/tmpfiles.d/leuitlog.conf
    print_status "Removed tmpfiles.d configuration"
fi

# Remove run directory
if [[ -d "$RUN_DIR" ]]; then
    rm -rf "$RUN_DIR"
    print_status "Removed $RUN_DIR"
fi

# Remove configuration
if [[ "$KEEP_CONFIG" == false ]]; then
    if [[ -d "$CONFIG_DIR" ]]; then
        rm -rf "$CONFIG_DIR"
        print_status "Removed $CONFIG_DIR"
    fi
else
    print_warning "Keeping configuration in $CONFIG_DIR"
fi

# Remove logs
if [[ "$KEEP_LOGS" == false ]]; then
    if [[ -d "$LOG_DIR" ]]; then
        rm -rf "$LOG_DIR"
        print_status "Removed $LOG_DIR"
    fi
else
    print_warning "Keeping logs in $LOG_DIR"
fi

# Remove user
print_header "Cleaning Up"

if id "$SERVICE_USER" &>/dev/null; then
    userdel "$SERVICE_USER" 2>/dev/null || true
    print_status "Removed user: $SERVICE_USER"
fi

# Summary
print_header "Uninstallation Complete"

echo "LeuitLog has been removed from your system."
echo ""

if [[ "$KEEP_LOGS" == true ]]; then
    echo "  • Logs preserved in: $LOG_DIR"
fi

if [[ "$KEEP_CONFIG" == true ]]; then
    echo "  • Configuration preserved in: $CONFIG_DIR"
fi

echo ""
