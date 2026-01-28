#!/usr/bin/env python3
"""
LeuitLog v1.0.0 - Web UI (Read-Only)

A minimal, read-only web interface for viewing log files.
This UI is strictly for verification purposes only.

Features:
- Display log entries from log files
- Read-only access (no modification)
- Show latest log records with simple pagination
- Display timestamp and message clearly
- Manual refresh
- Show service status (running / stopped)

This module does NOT:
- Modify any logs or configuration
- Perform heavy parsing or analysis
- Lock or interfere with log files
"""

import os
import sys
import configparser
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Optional
from collections import deque

from flask import Flask, render_template, jsonify, url_for

# Configuration
app = Flask(__name__, 
            static_folder='../web/static',
            template_folder='../web/templates')

# Global config reference
config = None
CONFIG_PATH = None


class ConfigError(Exception):
    """Raised when configuration is invalid."""
    pass


def find_config() -> str:
    """
    Find the configuration file.
    
    Returns:
        Path to configuration file
        
    Raises:
        ConfigError: If no configuration file found
    """
    config_paths = [
        '/etc/leuitlog/leuitlog.conf',
        os.path.expanduser('~/.config/leuitlog/leuitlog.conf'),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'leuitlog.conf')
    ]
    
    for path in config_paths:
        if os.path.exists(path):
            return path
    
    raise ConfigError("No configuration file found")


def load_config(config_path: str) -> configparser.ConfigParser:
    """
    Load configuration from file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Parsed configuration
    """
    config = configparser.ConfigParser()
    config.read(config_path)
    return config


def get_service_status() -> dict:
    """
    Get the current service status.
    
    Returns:
        Dictionary with status information
    """
    global config
    
    if config is None:
        return {
            'running': False,
            'pid': None,
            'error': 'Configuration not loaded'
        }
    
    pid_file = Path(config['service']['pid_file']).expanduser()
    log_dir = Path(config['logging']['log_dir']).expanduser()
    log_file = config['logging']['log_file']
    log_path = log_dir / log_file
    
    status = {
        'running': False,
        'pid': None,
        'log_file': str(log_path),
        'log_size_bytes': 0,
        'log_size_human': '0 B',
        'log_exists': log_path.exists(),
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    if pid_file.exists():
        try:
            with open(pid_file, 'r') as f:
                pid = int(f.read().strip())
            # Check if process is actually running
            os.kill(pid, 0)
            status['running'] = True
            status['pid'] = pid
        except (ValueError, ProcessLookupError, PermissionError, FileNotFoundError):
            pass
    
    if log_path.exists():
        size = log_path.stat().st_size
        status['log_size_bytes'] = size
        status['log_size_human'] = format_size(size)
    
    return status


def format_size(size_bytes: int) -> str:
    """
    Format byte size to human readable string.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Human readable size string
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def read_log_tail(num_lines: int = 100, page: int = 1) -> Tuple[List[dict], int, int]:
    """
    Read the last N lines from the log file.
    
    This function reads the log file without locking it,
    ensuring it doesn't interfere with the logging core.
    
    Args:
        num_lines: Number of lines per page
        page: Page number (1-based)
        
    Returns:
        Tuple of (log entries, total lines, total pages)
    """
    global config
    
    if config is None:
        return [], 0, 0
    
    log_dir = Path(config['logging']['log_dir']).expanduser()
    log_file = config['logging']['log_file']
    log_path = log_dir / log_file
    
    if not log_path.exists():
        return [], 0, 0
    
    entries = []
    total_lines = 0
    
    try:
        # Read all lines to count total (simple approach for small-medium logs)
        with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
            all_lines = f.readlines()
        
        total_lines = len(all_lines)
        total_pages = max(1, (total_lines + num_lines - 1) // num_lines)
        
        # Clamp page number
        page = max(1, min(page, total_pages))
        
        # Calculate slice for requested page (newest first)
        # Page 1 = most recent entries
        start_idx = max(0, total_lines - (page * num_lines))
        end_idx = total_lines - ((page - 1) * num_lines)
        
        page_lines = all_lines[start_idx:end_idx]
        page_lines.reverse()  # Newest first
        
        for line in page_lines:
            line = line.strip()
            if not line:
                continue
            
            entry = parse_log_line(line)
            entries.append(entry)
        
        return entries, total_lines, total_pages
        
    except (IOError, OSError) as e:
        return [], 0, 0


def parse_log_line(line: str) -> dict:
    """
    Parse a log line into structured data.
    
    Expected format:
    2024-01-15 10:30:45 +0000 | INFO     | source          | message
    
    Args:
        line: Raw log line
        
    Returns:
        Dictionary with parsed fields
    """
    entry = {
        'timestamp': '',
        'level': 'INFO',
        'source': '',
        'message': line,
        'raw': line
    }
    
    try:
        parts = line.split(' | ', 3)
        if len(parts) >= 4:
            entry['timestamp'] = parts[0].strip()
            entry['level'] = parts[1].strip()
            entry['source'] = parts[2].strip()
            entry['message'] = parts[3].strip()
        elif len(parts) >= 3:
            entry['timestamp'] = parts[0].strip()
            entry['level'] = parts[1].strip()
            entry['message'] = parts[2].strip()
    except Exception:
        pass
    
    return entry


@app.route('/')
def index():
    """Render the main log viewer page."""
    status = get_service_status()
    return render_template('index.html', status=status)


@app.route('/api/status')
def api_status():
    """API endpoint for service status."""
    return jsonify(get_service_status())


@app.route('/api/logs')
@app.route('/api/logs/<int:page>')
def api_logs(page: int = 1):
    """
    API endpoint for log entries.
    
    Args:
        page: Page number (1 = most recent)
    """
    from flask import request
    
    lines_per_page = request.args.get('limit', 100, type=int)
    lines_per_page = min(500, max(10, lines_per_page))  # Clamp between 10-500
    
    entries, total_lines, total_pages = read_log_tail(lines_per_page, page)
    
    return jsonify({
        'entries': entries,
        'page': page,
        'total_pages': total_pages,
        'total_lines': total_lines,
        'lines_per_page': lines_per_page
    })


@app.context_processor
def utility_processor():
    """Add utility functions to templates."""
    return {
        'now': datetime.now
    }


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors."""
    return render_template('error.html', 
                          error_code=404, 
                          error_message='Page not found'), 404


@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors."""
    return render_template('error.html',
                          error_code=500,
                          error_message='Internal server error'), 500


def init_app():
    """Initialize the application."""
    global config, CONFIG_PATH
    
    try:
        CONFIG_PATH = find_config()
        config = load_config(CONFIG_PATH)
        print(f"Loaded configuration from: {CONFIG_PATH}")
    except ConfigError as e:
        print(f"Warning: {e}", file=sys.stderr)
        print("Web UI will run with limited functionality.", file=sys.stderr)


# Initialize on import
init_app()


if __name__ == '__main__':
    # Development server only - use gunicorn or uwsgi in production
    port = 8080
    if config and 'webui' in config and 'port' in config['webui']:
        port = int(config['webui']['port'])
    
    print(f"Starting LeuitLog Web UI on http://127.0.0.1:{port}")
    print("WARNING: This is the development server. Use gunicorn for production.")
    
    app.run(host='127.0.0.1', port=port, debug=False)
