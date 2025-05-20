import psutil
import platform
from typing import Dict, List, Optional, Any
import socket
import os
from dataclasses import dataclass
from datetime import datetime

@dataclass
class SystemStats:
    """Container for system statistics."""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used: int  # in MB
    memory_total: int  # in MB
    disk_usage_percent: float
    network_io: Dict[str, Dict[str, int]]  # bytes sent/received per interface

class SystemMonitor:
    """Class for monitoring system resources."""
    
    def __init__(self):
        """Initialize the system monitor."""
        self._cpu_count = psutil.cpu_count()
        self._memory = psutil.virtual_memory()
        self._last_net_io = self._get_network_io()
        self._last_net_io_time = datetime.now()
    
    def _get_network_io(self) -> Dict[str, Dict[str, int]]:
        """Get current network I/O statistics."""
        net_io = {}
        for interface, stats in psutil.net_io_counters(pernic=True).items():
            net_io[interface] = {
                'bytes_sent': stats.bytes_sent,
                'bytes_recv': stats.bytes_recv
            }
        return net_io

    def get_system_stats(self) -> SystemStats:
        """Get current system statistics."""
        try:
            # Get CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Get memory usage
            memory = psutil.virtual_memory()
            
            # Get disk usage
            disk = psutil.disk_usage('/')
            
            # Get network I/O
            current_net_io = self._get_network_io()
            current_time = datetime.now()
            
            # Calculate network I/O rates
            time_diff = (current_time - self._last_net_io_time).total_seconds()
            net_io_rates = {}
            
            for interface in current_net_io:
                if interface in self._last_net_io:
                    bytes_sent_rate = int(
                        (current_net_io[interface]['bytes_sent'] - 
                         self._last_net_io[interface]['bytes_sent']) / time_diff
                    )
                    bytes_recv_rate = int(
                        (current_net_io[interface]['bytes_recv'] - 
                         self._last_net_io[interface]['bytes_recv']) / time_diff
                    )
                    net_io_rates[interface] = {
                        'bytes_sent': bytes_sent_rate,
                        'bytes_recv': bytes_recv_rate
                    }
            
            # Update last network I/O stats
            self._last_net_io = current_net_io
            self._last_net_io_time = current_time

            return SystemStats(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used=memory.used // 1024 // 1024,  # Convert to MB
                memory_total=memory.total // 1024 // 1024,  # Convert to MB
                disk_usage_percent=disk.percent,
                network_io=net_io_rates
            )
        except Exception as e:
            raise RuntimeError(f"Failed to get system stats: {e}")

    def get_system_info(self) -> Dict[str, Any]:
        """Get general system information."""
        try:
            return {
                'platform': platform.system(),
                'platform_version': platform.version(),
                'processor': platform.processor(),
                'python_version': platform.python_version(),
                'hostname': platform.node(),
                'cpu_count': self._cpu_count,
                'cpu_freq': {
                    'current': psutil.cpu_freq().current if psutil.cpu_freq() else None,
                    'min': psutil.cpu_freq().min if psutil.cpu_freq() else None,
                    'max': psutil.cpu_freq().max if psutil.cpu_freq() else None
                }
            }
        except Exception as e:
            raise RuntimeError(f"Failed to get system info: {e}")

    def get_process_list(self) -> List[Dict[str, Any]]:
        """Get list of running processes with their resource usage."""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']):
                try:
                    pinfo = proc.info
                    processes.append({
                        'pid': pinfo['pid'],
                        'name': pinfo['name'],
                        'username': pinfo['username'],
                        'cpu_percent': pinfo['cpu_percent'],
                        'memory_percent': pinfo['memory_percent']
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return processes
        except Exception as e:
            raise RuntimeError(f"Failed to get process list: {e}")
    
    def get_cpu_usage(self) -> Dict[str, float]:
        """Get detailed CPU usage information."""
        return {
            'total': psutil.cpu_percent(interval=1),
            'per_cpu': psutil.cpu_percent(interval=1, percpu=True)
        }
    
    def get_memory_usage(self) -> Dict[str, int]:
        """Get detailed memory usage information."""
        memory = psutil.virtual_memory()
        return {
            'total': memory.total // 1024 // 1024,  # Convert to MB
            'available': memory.available // 1024 // 1024,
            'used': memory.used // 1024 // 1024,
            'free': memory.free // 1024 // 1024,
            'percent': memory.percent
        }
    
    def get_disk_usage(self) -> Dict[str, Dict[str, int]]:
        """Get disk usage information for all mounted partitions."""
        partitions = {}
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                partitions[partition.mountpoint] = {
                    'total': usage.total // 1024 // 1024,  # Convert to MB
                    'used': usage.used // 1024 // 1024,
                    'free': usage.free // 1024 // 1024,
                    'percent': usage.percent
                }
            except (PermissionError, FileNotFoundError):
                continue
        return partitions 