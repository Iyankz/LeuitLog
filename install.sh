#!/bin/bash
#
# LeuitLog v1.0.0 Installation Script
# ====================================
# 
# This script installs LeuitLog on Ubuntu 24.04 LTS and Debian 12.
#
# Usage: sudo ./install.sh
#
# Requirements:
#   - Root privileges (sudo)
#   - Ubuntu 24.04 LTS or Debian 12
#   - Python 3.10+
#   - systemd

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="/opt/leuitlog"
CONFIG_DIR="/etc/leuitlog"
LOG_DIR="/var/log/leuitlog"
RUN_DIR="/var/run/leuitlog"
SERVICE_USER="leuitlog"
SERVICE_GROUP="leuitlog"

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

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

# Check OS compatibility
check_os() {
    print_header "Checking System Compatibility"
    
    if [[ ! -f /etc/os-release ]]; then
        print_error "Cannot determine OS. /etc/os-release not found."
        exit 1
    fi
    
    source /etc/os-release
    
    local supported=false
    
    # Check for Ubuntu 24.04
    if [[ "$ID" == "ubuntu" && "$VERSION_ID" == "24.04" ]]; then
        supported=true
        print_status "Detected Ubuntu 24.04 LTS"
    fi
    
    # Check for Debian 12
    if [[ "$ID" == "debian" && "$VERSION_ID" == "12" ]]; then
        supported=true
        print_status "Detected Debian 12 (Bookworm)"
    fi
    
    if [[ "$supported" == false ]]; then
        print_error "Unsupported OS: $PRETTY_NAME"
        print_error "LeuitLog v1.0.0 supports only Ubuntu 24.04 LTS and Debian 12"
        exit 1
    fi
    
    # Check for systemd
    if ! command -v systemctl &> /dev/null; then
        print_error "systemd is required but not found"
        exit 1
    fi
    print_status "systemd detected"
    
    # Check Python version
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required but not found"
        exit 1
    fi
    
    local python_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    print_status "Python $python_version detected"
}

# Install dependencies
install_dependencies() {
    print_header "Installing Dependencies"
    
    apt-get update -qq
    
    # Install required packages
    apt-get install -y -qq \
        python3 \
        python3-pip \
        python3-venv \
        python3-systemd \
        > /dev/null 2>&1
    
    print_status "System packages installed"
    
    # Install Python packages
    pip3 install --quiet --break-system-packages \
        flask \
        gunicorn \
        2>/dev/null || pip3 install --quiet flask gunicorn
    
    print_status "Python packages installed (flask, gunicorn)"
}

# Create system user
create_user() {
    print_header "Creating Service User"
    
    if id "$SERVICE_USER" &>/dev/null; then
        print_warning "User '$SERVICE_USER' already exists"
    else
        useradd --system --no-create-home --shell /usr/sbin/nologin "$SERVICE_USER"
        print_status "Created system user: $SERVICE_USER"
    fi
}

# Create directories
create_directories() {
    print_header "Creating Directories"
    
    # Installation directory
    mkdir -p "$INSTALL_DIR"
    print_status "Created $INSTALL_DIR"
    
    # Configuration directory
    mkdir -p "$CONFIG_DIR"
    print_status "Created $CONFIG_DIR"
    
    # Log directory
    mkdir -p "$LOG_DIR"
    chown "$SERVICE_USER:$SERVICE_GROUP" "$LOG_DIR"
    chmod 750 "$LOG_DIR"
    print_status "Created $LOG_DIR"
    
    # Run directory (for PID file)
    mkdir -p "$RUN_DIR"
    chown "$SERVICE_USER:$SERVICE_GROUP" "$RUN_DIR"
    chmod 755 "$RUN_DIR"
    print_status "Created $RUN_DIR"
    
    # Create tmpfiles.d entry for /var/run/leuitlog persistence
    cat > /etc/tmpfiles.d/leuitlog.conf << EOF
d /var/run/leuitlog 0755 $SERVICE_USER $SERVICE_GROUP -
EOF
    print_status "Created tmpfiles.d configuration"
}

# Copy files
copy_files() {
    print_header "Installing Files"
    
    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    
    # Copy source files
    cp -r "$script_dir/src" "$INSTALL_DIR/"
    print_status "Installed source files"
    
    # Copy web files
    cp -r "$script_dir/web" "$INSTALL_DIR/"
    print_status "Installed web files"
    
    # Copy configuration (don't overwrite if exists)
    if [[ ! -f "$CONFIG_DIR/leuitlog.conf" ]]; then
        cp "$script_dir/config/leuitlog.conf" "$CONFIG_DIR/"
        print_status "Installed configuration file"
    else
        print_warning "Configuration file exists, not overwriting"
        cp "$script_dir/config/leuitlog.conf" "$CONFIG_DIR/leuitlog.conf.new"
        print_status "New configuration saved as leuitlog.conf.new"
    fi
    
    # Copy systemd service files
    cp "$script_dir/config/leuitlog.service" /etc/systemd/system/
    cp "$script_dir/config/leuitlog-webui.service" /etc/systemd/system/
    print_status "Installed systemd service files"
    
    # Set permissions
    chown -R root:root "$INSTALL_DIR"
    chmod -R 755 "$INSTALL_DIR"
    chown root:root "$CONFIG_DIR/leuitlog.conf"
    chmod 644 "$CONFIG_DIR/leuitlog.conf"
}

# Create placeholder logo
create_logo() {
    print_header "Creating Logo Placeholder"
    
    local logo_dir="$INSTALL_DIR/web/static/logo"
    mkdir -p "$logo_dir"
    
    # Create a simple SVG placeholder and convert to PNG
    # If convert is not available, create a minimal placeholder
    if command -v convert &> /dev/null; then
        convert -size 512x512 xc:transparent \
            -fill '#e94560' \
            -font DejaVu-Sans-Bold \
            -pointsize 120 \
            -gravity center \
            -annotate 0 'LL' \
            "$logo_dir/logo.png" 2>/dev/null || true
    fi
    
    # If logo wasn't created, create a minimal 1x1 transparent PNG
    if [[ ! -f "$logo_dir/logo.png" ]]; then
        # Minimal valid PNG (1x1 transparent)
        printf '\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82' > "$logo_dir/logo.png"
        print_warning "Created minimal placeholder logo (replace with custom logo)"
    else
        print_status "Created logo placeholder"
    fi
    
    chmod 644 "$logo_dir/logo.png"
}

# Enable and start services
enable_services() {
    print_header "Configuring Services"
    
    systemctl daemon-reload
    print_status "Reloaded systemd daemon"
    
    systemctl enable leuitlog.service
    print_status "Enabled leuitlog service"
    
    systemctl enable leuitlog-webui.service
    print_status "Enabled leuitlog-webui service"
    
    # Start services
    systemctl start leuitlog.service
    if systemctl is-active --quiet leuitlog.service; then
        print_status "Started leuitlog service"
    else
        print_warning "leuitlog service failed to start (check: journalctl -u leuitlog)"
    fi
    
    systemctl start leuitlog-webui.service
    if systemctl is-active --quiet leuitlog-webui.service; then
        print_status "Started leuitlog-webui service"
    else
        print_warning "leuitlog-webui service failed to start (check: journalctl -u leuitlog-webui)"
    fi
}

# Print summary
print_summary() {
    print_header "Installation Complete"
    
    echo -e "LeuitLog v1.0.0 has been installed successfully!\n"
    
    echo "Installation Summary:"
    echo "  • Install directory:  $INSTALL_DIR"
    echo "  • Configuration:      $CONFIG_DIR/leuitlog.conf"
    echo "  • Log directory:      $LOG_DIR"
    echo "  • Service user:       $SERVICE_USER"
    echo ""
    
    echo "Service Commands:"
    echo "  • Start:    sudo systemctl start leuitlog"
    echo "  • Stop:     sudo systemctl stop leuitlog"
    echo "  • Restart:  sudo systemctl restart leuitlog"
    echo "  • Status:   sudo systemctl status leuitlog"
    echo ""
    
    echo "Web UI:"
    echo "  • URL:      http://127.0.0.1:8080"
    echo "  • Status:   sudo systemctl status leuitlog-webui"
    echo ""
    
    echo "Log Files:"
    echo "  • Main log: $LOG_DIR/leuitlog.log"
    echo "  • Journal:  journalctl -u leuitlog"
    echo ""
    
    print_warning "To customize, edit: $CONFIG_DIR/leuitlog.conf"
    echo ""
}

# Main installation
main() {
    print_header "LeuitLog v1.0.0 Installer"
    
    check_root
    check_os
    install_dependencies
    create_user
    create_directories
    copy_files
    create_logo
    enable_services
    print_summary
}

# Run main function
main "$@"
