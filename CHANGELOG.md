# Changelog

All notable changes to LeuitLog will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-15

### 🎉 Initial Stable Release

LeuitLog v1.0.0 is the first stable release, focused on reliable logging and long-running service operation.

### Added

#### Core Logging
- Stable, reliable logging daemon for 24/7 operation
- Syslog listener on configurable UDP port
- Journald integration (when python3-systemd is available)
- Consistent log format with timestamps
- System timezone support

#### Log Management
- Automatic log rotation based on file size
- Configurable backup file count
- Secure log file permissions (640)
- No disk space exhaustion protection

#### Service Management
- systemd service integration
- Clean start/stop/restart operations
- Graceful shutdown without zombie processes
- Auto-start on system boot
- PID file management

#### Configuration
- File-based configuration (`/etc/leuitlog/leuitlog.conf`)
- Safe production-ready defaults
- Clear error messages for configuration issues
- No hardcoded values

#### Web UI (Read-Only)
- Minimal web interface for log verification
- Display recent log entries with pagination
- Service status indicator (running/stopped)
- Manual refresh capability
- Timestamp and message display
- Dark theme interface
- Logo placeholder with fallback text

#### Installation
- Automated installer for Ubuntu 24.04 LTS and Debian 12
- Uninstaller with optional data preservation
- Non-root service user creation
- Security-hardened systemd services

#### Documentation
- Comprehensive README with installation guide
- Configuration reference
- Troubleshooting guide
- Service management instructions

### Platform Support
- Ubuntu 24.04 LTS
- Debian 12 (Bookworm)

### Security
- Dedicated service user (leuitlog)
- Minimal required privileges
- Protected system directories
- Read-only Web UI

### Not Included (By Design)
- Authentication or user management
- Log editing or deletion
- Brute-force detection
- Anomaly detection
- Alerts or notifications
- Dashboards or charts
- Advanced filtering or search
- Public APIs
- Plugin systems
- Distributed logging

---

## Future Roadmap

Features under consideration for future releases:

- [ ] Authentication for Web UI
- [ ] Log filtering and search
- [ ] Basic analytics dashboard
- [ ] Alert notifications
- [ ] Remote syslog forwarding
- [ ] Log compression

These features will be considered for v1.1.0 and beyond based on community feedback.
