#!/usr/bin/env python3
"""
LeuitLog v1.0.0 - Core Logging Daemon
A stable, reliable logging service for Linux servers.

This module handles:
- Syslog monitoring and logging
- Log file management with rotation
- Clean daemon behavior with signal handling
"""

import os
import sys
import time
import signal
import logging
import json
import fcntl
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional
import configparser
import socket
import select

# Global flag for graceful shutdown
shutdown_requested = False
config = None


class ConfigError(Exception):
    """Raised when configuration is invalid."""
    pass


def load_config(config_path: str) -> configparser.ConfigParser:
    """
    Load and validate configuration from file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Parsed configuration object
        
    Raises:
        ConfigError: If configuration is invalid or missing
    """
    if not os.path.exists(config_path):
        raise ConfigError(f"Configuration file not found: {config_path}")
    
    config = configparser.ConfigParser()
    
    try:
        config.read(config_path)
    except configparser.Error as e:
        raise ConfigError(f"Failed to parse configuration file: {e}")
    
    # Validate required sections
    required_sections = ['logging', 'service']
    for section in required_sections:
        if section not in config:
            raise ConfigError(f"Missing required configuration section: [{section}]")
    
    # Validate required keys
    required_keys = {
        'logging': ['log_dir', 'log_file', 'max_size_mb', 'backup_count'],
        'service': ['pid_file', 'listen_port']
    }
    
    for section, keys in required_keys.items():
        for key in keys:
            if key not in config[section]:
                raise ConfigError(f"Missing required configuration key: {section}.{key}")
    
    # Validate numeric values
    try:
        int(config['logging']['max_size_mb'])
        int(config['logging']['backup_count'])
        int(config['service']['listen_port'])
    except ValueError as e:
        raise ConfigError(f"Invalid numeric value in configuration: {e}")
    
    return config


def setup_logging(config: configparser.ConfigParser) -> logging.Logger:
    """
    Set up the logging system with rotation.
    
    Args:
        config: Parsed configuration object
        
    Returns:
        Configured logger instance
    """
    log_dir = Path(config['logging']['log_dir']).expanduser()
    log_file = config['logging']['log_file']
    max_size_mb = int(config['logging']['max_size_mb'])
    backup_count = int(config['logging']['backup_count'])
    
    # Create log directory if it doesn't exist
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Set secure permissions on log directory
    os.chmod(log_dir, 0o750)
    
    log_path = log_dir / log_file
    
    # Create logger
    logger = logging.getLogger('leuitlog')
    logger.setLevel(logging.INFO)
    
    # Remove any existing handlers
    logger.handlers.clear()
    
    # Create rotating file handler
    handler = RotatingFileHandler(
        log_path,
        maxBytes=max_size_mb * 1024 * 1024,
        backupCount=backup_count,
        encoding='utf-8'
    )
    
    # Set log format with consistent timestamp
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(source)-15s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S %z'
    )
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    
    # Set secure permissions on log file
    if log_path.exists():
        os.chmod(log_path, 0o640)
    
    return logger


def write_pid_file(pid_file: str) -> None:
    """
    Write the current process ID to the PID file.
    
    Args:
        pid_file: Path to the PID file
    """
    pid_path = Path(pid_file).expanduser()
    pid_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(pid_path, 'w') as f:
        f.write(str(os.getpid()))
    
    os.chmod(pid_path, 0o644)


def remove_pid_file(pid_file: str) -> None:
    """
    Remove the PID file on shutdown.
    
    Args:
        pid_file: Path to the PID file
    """
    pid_path = Path(pid_file).expanduser()
    if pid_path.exists():
        pid_path.unlink()


def signal_handler(signum: int, frame) -> None:
    """
    Handle shutdown signals gracefully.
    
    Args:
        signum: Signal number
        frame: Current stack frame
    """
    global shutdown_requested
    shutdown_requested = True


def get_service_status(config: configparser.ConfigParser) -> dict:
    """
    Get the current service status.
    
    Args:
        config: Configuration object
        
    Returns:
        Dictionary with status information
    """
    pid_file = Path(config['service']['pid_file']).expanduser()
    log_dir = Path(config['logging']['log_dir']).expanduser()
    log_file = config['logging']['log_file']
    log_path = log_dir / log_file
    
    status = {
        'running': False,
        'pid': None,
        'log_file': str(log_path),
        'log_size_bytes': 0,
        'log_exists': log_path.exists(),
        'timestamp': datetime.now().isoformat()
    }
    
    if pid_file.exists():
        try:
            with open(pid_file, 'r') as f:
                pid = int(f.read().strip())
            # Check if process is actually running
            os.kill(pid, 0)
            status['running'] = True
            status['pid'] = pid
        except (ValueError, ProcessLookupError, PermissionError):
            pass
    
    if log_path.exists():
        status['log_size_bytes'] = log_path.stat().st_size
    
    return status


class SyslogListener:
    """
    Listen for syslog messages on UDP port.
    """
    
    def __init__(self, port: int, logger: logging.Logger):
        """
        Initialize the syslog listener.
        
        Args:
            port: UDP port to listen on
            logger: Logger instance for recording messages
        """
        self.port = port
        self.logger = logger
        self.socket = None
    
    def start(self) -> None:
        """Start listening for syslog messages."""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.setblocking(False)
        
        try:
            self.socket.bind(('127.0.0.1', self.port))
        except PermissionError:
            raise ConfigError(
                f"Cannot bind to port {self.port}. "
                "Try using a port > 1024 or run with appropriate permissions."
            )
        except OSError as e:
            raise ConfigError(f"Cannot bind to port {self.port}: {e}")
    
    def stop(self) -> None:
        """Stop the listener and close the socket."""
        if self.socket:
            self.socket.close()
            self.socket = None
    
    def process_messages(self, timeout: float = 1.0) -> int:
        """
        Process incoming syslog messages.
        
        Args:
            timeout: Select timeout in seconds
            
        Returns:
            Number of messages processed
        """
        if not self.socket:
            return 0
        
        count = 0
        ready, _, _ = select.select([self.socket], [], [], timeout)
        
        if ready:
            while True:
                try:
                    data, addr = self.socket.recvfrom(8192)
                    message = data.decode('utf-8', errors='replace').strip()
                    
                    # Parse syslog priority if present
                    source = addr[0]
                    if message.startswith('<'):
                        try:
                            end = message.index('>')
                            message = message[end + 1:]
                        except ValueError:
                            pass
                    
                    # Log the message
                    self.logger.info(
                        message,
                        extra={'source': source}
                    )
                    count += 1
                    
                except BlockingIOError:
                    break
                except Exception as e:
                    self.logger.error(
                        f"Error processing message: {e}",
                        extra={'source': 'leuitlog'}
                    )
        
        return count


class JournalReader:
    """
    Read and forward journald logs.
    """
    
    def __init__(self, logger: logging.Logger):
        """
        Initialize the journal reader.
        
        Args:
            logger: Logger instance for recording messages
        """
        self.logger = logger
        self.journal = None
        self._available = False
        
        try:
            from systemd import journal
            self.journal = journal.Reader()
            self.journal.this_boot()
            self.journal.seek_tail()
            self.journal.get_previous()
            self._available = True
        except ImportError:
            pass
        except Exception:
            pass
    
    @property
    def available(self) -> bool:
        """Check if journal reading is available."""
        return self._available
    
    def process_entries(self, max_entries: int = 100) -> int:
        """
        Process new journal entries.
        
        Args:
            max_entries: Maximum entries to process per call
            
        Returns:
            Number of entries processed
        """
        if not self._available or not self.journal:
            return 0
        
        count = 0
        
        try:
            for entry in self.journal:
                if count >= max_entries:
                    break
                
                message = entry.get('MESSAGE', '')
                if not message:
                    continue
                
                source = entry.get('SYSLOG_IDENTIFIER', 
                         entry.get('_SYSTEMD_UNIT', 'unknown'))
                
                # Truncate long source names
                if len(source) > 15:
                    source = source[:12] + '...'
                
                priority = entry.get('PRIORITY', 6)
                
                if priority <= 3:
                    self.logger.error(message, extra={'source': source})
                elif priority <= 4:
                    self.logger.warning(message, extra={'source': source})
                else:
                    self.logger.info(message, extra={'source': source})
                
                count += 1
                
        except Exception as e:
            self.logger.error(
                f"Error reading journal: {e}",
                extra={'source': 'leuitlog'}
            )
        
        return count


def run_daemon(config: configparser.ConfigParser) -> int:
    """
    Run the main daemon loop.
    
    Args:
        config: Configuration object
        
    Returns:
        Exit code
    """
    global shutdown_requested
    
    # Set up signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGHUP, signal_handler)
    
    # Set up logging
    logger = setup_logging(config)
    
    # Write PID file
    pid_file = config['service']['pid_file']
    write_pid_file(pid_file)
    
    logger.info(
        "LeuitLog v1.0.0 starting",
        extra={'source': 'leuitlog'}
    )
    
    # Initialize listeners
    listen_port = int(config['service']['listen_port'])
    syslog_listener = SyslogListener(listen_port, logger)
    journal_reader = JournalReader(logger)
    
    try:
        syslog_listener.start()
        logger.info(
            f"Syslog listener started on port {listen_port}",
            extra={'source': 'leuitlog'}
        )
        
        if journal_reader.available:
            logger.info(
                "Journal reader initialized",
                extra={'source': 'leuitlog'}
            )
        
        # Main loop
        while not shutdown_requested:
            # Process syslog messages
            syslog_listener.process_messages(timeout=0.5)
            
            # Process journal entries
            if journal_reader.available:
                journal_reader.process_entries()
            
            # Small sleep to prevent CPU spinning
            time.sleep(0.1)
        
        logger.info(
            "LeuitLog shutting down gracefully",
            extra={'source': 'leuitlog'}
        )
        
    except ConfigError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        logger.error(
            f"Fatal error: {e}",
            extra={'source': 'leuitlog'}
        )
        return 1
    finally:
        syslog_listener.stop()
        remove_pid_file(pid_file)
    
    return 0


def main() -> int:
    """
    Main entry point.
    
    Returns:
        Exit code
    """
    # Default config path
    config_paths = [
        '/etc/leuitlog/leuitlog.conf',
        os.path.expanduser('~/.config/leuitlog/leuitlog.conf'),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'leuitlog.conf')
    ]
    
    config_path = None
    for path in config_paths:
        if os.path.exists(path):
            config_path = path
            break
    
    if not config_path:
        print("Error: No configuration file found.", file=sys.stderr)
        print("Searched locations:", file=sys.stderr)
        for path in config_paths:
            print(f"  - {path}", file=sys.stderr)
        return 1
    
    try:
        config = load_config(config_path)
        print(f"Using configuration: {config_path}")
    except ConfigError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        return 1
    
    return run_daemon(config)


if __name__ == '__main__':
    sys.exit(main())
