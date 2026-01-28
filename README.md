# LeuitLog v1.0.0

**A stable, reliable logging service for Linux servers.**

LeuitLog is a lightweight logging daemon designed for 24/7 server operation with a minimal read-only web interface for log verification.

## Features

- ✅ **Stable Logging** - Consistent, reliable log capture without missing entries
- ✅ **24/7 Ready** - Designed for long-running server deployments
- ✅ **Log Rotation** - Automatic size-based log rotation to prevent disk exhaustion
- ✅ **Minimal Web UI** - Read-only interface for log verification
- ✅ **systemd Integration** - Full support for start, stop, restart, and auto-start
- ✅ **Security Focused** - Runs as dedicated user with minimal privileges

## Requirements

- **Operating System**: Ubuntu 24.04 LTS or Debian 12 (Bookworm)
- **Python**: 3.10 or higher
- **Init System**: systemd

## Installation

### Quick Install

```bash
# Clone or download the repository
git clone https://github.com/Iyankz/LeuitLog.git
cd LeuitLog

# Run the installer (requires root)
sudo bash install.sh
```

### Manual Installation

If you prefer manual installation, follow these steps:

1. Install dependencies:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-systemd
   sudo pip3 install flask gunicorn --break-system-packages
   ```

2. Create the service user:
   ```bash
   sudo useradd --system --no-create-home --shell /usr/sbin/nologin leuitlog
   ```

3. Create directories:
   ```bash
   sudo mkdir -p /opt/leuitlog /etc/leuitlog /var/log/leuitlog /var/run/leuitlog
   sudo chown leuitlog:leuitlog /var/log/leuitlog /var/run/leuitlog
   ```

4. Copy files:
   ```bash
   sudo cp -r src web /opt/leuitlog/
   sudo cp config/leuitlog.conf /etc/leuitlog/
   sudo cp config/leuitlog.service /etc/systemd/system/
   sudo cp config/leuitlog-webui.service /etc/systemd/system/
   ```

5. Enable and start services:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable leuitlog leuitlog-webui
   sudo systemctl start leuitlog leuitlog-webui
   ```

## Service Management

### Start/Stop/Restart

```bash
# Core logging service
sudo systemctl start leuitlog
sudo systemctl stop leuitlog
sudo systemctl restart leuitlog

# Web UI
sudo systemctl start leuitlog-webui
sudo systemctl stop leuitlog-webui
sudo systemctl restart leuitlog-webui
```

### Check Status

```bash
sudo systemctl status leuitlog
sudo systemctl status leuitlog-webui
```

### View Logs

```bash
# View LeuitLog's own logs via journald
journalctl -u leuitlog -f

# View captured logs
tail -f /var/log/leuitlog/leuitlog.log
```

## Configuration

The main configuration file is located at `/etc/leuitlog/leuitlog.conf`.

### Key Settings

| Section | Key | Default | Description |
|---------|-----|---------|-------------|
| `logging` | `log_dir` | `/var/log/leuitlog` | Directory for log files |
| `logging` | `log_file` | `leuitlog.log` | Main log file name |
| `logging` | `max_size_mb` | `50` | Max size before rotation (MB) |
| `logging` | `backup_count` | `5` | Number of rotated files to keep |
| `service` | `listen_port` | `5514` | UDP port for syslog messages |
| `webui` | `port` | `8080` | Web UI port |
| `webui` | `host` | `127.0.0.1` | Web UI bind address |

After changing configuration:
```bash
sudo systemctl restart leuitlog leuitlog-webui
```

## Web UI Access

The Web UI is accessible at:

```
http://127.0.0.1:8080
```

### Web UI Features

- View recent log entries
- See service status (running/stopped)
- Manual refresh
- Simple pagination

### Web UI Limitations (by design)

The Web UI in v1.0.0 is intentionally minimal and read-only:

- ❌ No authentication (local access only recommended)
- ❌ No log editing or deletion
- ❌ No configuration changes
- ❌ No advanced filtering
- ❌ No charts or dashboards

## Log File Location

| File | Location |
|------|----------|
| Main log | `/var/log/leuitlog/leuitlog.log` |
| Rotated logs | `/var/log/leuitlog/leuitlog.log.1`, `.2`, etc. |
| PID file | `/var/run/leuitlog/leuitlog.pid` |

## Sending Logs to LeuitLog

LeuitLog listens for syslog messages on UDP port 5514 (configurable).

### Configure rsyslog

Add to `/etc/rsyslog.d/50-leuitlog.conf`:

```
*.* @127.0.0.1:5514
```

Then restart rsyslog:
```bash
sudo systemctl restart rsyslog
```

### Send Test Message

```bash
logger -n 127.0.0.1 -P 5514 "Test message from $(hostname)"
```

## Logo Customization

To use a custom logo:

1. Prepare your logo as a PNG file (recommended: 512x512, transparent background)
2. Replace the placeholder:
   ```bash
   sudo cp your-logo.png /opt/leuitlog/web/static/logo/logo.png
   ```
3. Refresh the Web UI

If the logo file is missing, "LeuitLog" text will be displayed as fallback.

## Uninstallation

```bash
# Full uninstall
sudo ./uninstall.sh

# Keep logs and configuration
sudo ./uninstall.sh --keep-logs --keep-config
```

## Troubleshooting

### Service won't start

Check the journal for errors:
```bash
journalctl -u leuitlog -e
```

Common issues:
- Port already in use: Change `listen_port` in config
- Permission denied: Check directory ownership
- Config error: Validate `/etc/leuitlog/leuitlog.conf`

### Web UI not accessible

1. Check if service is running:
   ```bash
   sudo systemctl status leuitlog-webui
   ```

2. Verify port binding:
   ```bash
   ss -tlnp | grep 8080
   ```

3. Check firewall rules (if accessing remotely)

### No logs appearing

1. Verify the core service is running
2. Check if messages are being sent to the correct port
3. Review permissions on `/var/log/leuitlog`

## Security Notes

- The Web UI binds to `127.0.0.1` by default (local access only)
- For remote access, use a reverse proxy with authentication
- Log files have restricted permissions (640)
- The service runs as a dedicated non-root user

## Not Included in v1.0.0

The following features are explicitly **not** part of this release:

- Brute-force detection
- Anomaly detection
- Alerts or notifications
- Dashboards or charts
- Authentication
- Public APIs
- Distributed logging

## License

MIT License - See LICENSE file for details.

## Version History

See [CHANGELOG.md](CHANGELOG.md) for version history.

---

**LeuitLog v1.0.0** - First Stable Release
