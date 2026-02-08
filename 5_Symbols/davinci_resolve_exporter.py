#!/usr/bin/env python3
"""
DaVinci Resolve Metrics Exporter for Prometheus

This exporter collects metrics specific to DaVinci Resolve:
- Hard drive usage for media storage and cache
- Project file monitoring
- Log file analysis
- Render queue status (when available)
- GPU and CPU usage specific to DaVinci Resolve processes
"""

import os
import time
import psutil
import platform
from pathlib import Path
from prometheus_client import start_http_server, Gauge, Counter, Info
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Metrics definitions
davinci_resolve_info = Info('davinci_resolve', 'DaVinci Resolve Installation Information')
davinci_resolve_running = Gauge('davinci_resolve_running', 'Whether DaVinci Resolve is running (1=running, 0=stopped)')
davinci_resolve_cpu_percent = Gauge('davinci_resolve_cpu_percent', 'CPU usage percentage by DaVinci Resolve')
davinci_resolve_memory_bytes = Gauge('davinci_resolve_memory_bytes', 'Memory usage by DaVinci Resolve in bytes')

# Hard drive metrics
davinci_media_disk_total_bytes = Gauge('davinci_media_disk_total_bytes', 'Total disk space for media storage', ['mount_point'])
davinci_media_disk_used_bytes = Gauge('davinci_media_disk_used_bytes', 'Used disk space for media storage', ['mount_point'])
davinci_media_disk_free_bytes = Gauge('davinci_media_disk_free_bytes', 'Free disk space for media storage', ['mount_point'])
davinci_media_disk_usage_percent = Gauge('davinci_media_disk_usage_percent', 'Disk usage percentage for media storage', ['mount_point'])

davinci_cache_disk_total_bytes = Gauge('davinci_cache_disk_total_bytes', 'Total disk space for cache')
davinci_cache_disk_used_bytes = Gauge('davinci_cache_disk_used_bytes', 'Used disk space for cache')
davinci_cache_disk_free_bytes = Gauge('davinci_cache_disk_free_bytes', 'Free disk space for cache')

# Project metrics
davinci_project_count = Gauge('davinci_project_count', 'Number of DaVinci Resolve projects')
davinci_project_total_size_bytes = Gauge('davinci_project_total_size_bytes', 'Total size of all projects in bytes')

# Log metrics
davinci_log_errors_total = Counter('davinci_log_errors_total', 'Total number of errors in logs')
davinci_log_warnings_total = Counter('davinci_log_warnings_total', 'Total number of warnings in logs')
davinci_log_size_bytes = Gauge('davinci_log_size_bytes', 'Size of DaVinci Resolve log files in bytes')

# GPU metrics specific to DaVinci
davinci_gpu_memory_used_bytes = Gauge('davinci_gpu_memory_used_bytes', 'GPU memory used by DaVinci Resolve', ['gpu_id'])
davinci_gpu_utilization_percent = Gauge('davinci_gpu_utilization_percent', 'GPU utilization by DaVinci Resolve', ['gpu_id'])


class DaVinciResolveExporter:
    """Exporter for DaVinci Resolve metrics"""
    
    def __init__(self):
        self.platform = platform.system()
        self.davinci_process_names = ['Resolve.exe', 'resolve', 'DaVinci Resolve']
        self.setup_paths()
        
    def setup_paths(self):
        """Setup paths for DaVinci Resolve installation and data directories"""
        if self.platform == 'Windows':
            self.install_path = Path('C:/Program Files/Blackmagic Design/DaVinci Resolve')
            self.appdata_path = Path(os.environ.get('PROGRAMDATA', 'C:/ProgramData')) / 'Blackmagic Design/DaVinci Resolve'
            self.log_path = self.appdata_path / 'logs'
            self.cache_path = self.appdata_path / 'CacheClip'
            # Common media storage locations
            self.media_paths = [
                Path('D:/'),  # Common external drive
                Path('E:/'),  # Common external drive
                Path('C:/Users') / os.environ.get('USERNAME', 'Public') / 'Videos',
            ]
        else:  # Linux/macOS
            self.install_path = Path('/opt/resolve')
            self.log_path = Path.home() / '.local/share/DaVinciResolve/logs'
            self.cache_path = Path.home() / '.local/share/DaVinciResolve/cache'
            self.media_paths = [Path.home() / 'Videos']
    
    def find_davinci_process(self):
        """Find DaVinci Resolve process"""
        for proc in psutil.process_iter(['name', 'cpu_percent', 'memory_info']):
            try:
                if any(name.lower() in proc.info['name'].lower() for name in self.davinci_process_names):
                    return proc
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return None
    
    def collect_process_metrics(self):
        """Collect metrics about DaVinci Resolve process"""
        proc = self.find_davinci_process()
        
        if proc:
            davinci_resolve_running.set(1)
            try:
                # CPU usage
                cpu_percent = proc.cpu_percent(interval=1)
                davinci_resolve_cpu_percent.set(cpu_percent)
                
                # Memory usage
                mem_info = proc.memory_info()
                davinci_resolve_memory_bytes.set(mem_info.rss)
                
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        else:
            davinci_resolve_running.set(0)
            davinci_resolve_cpu_percent.set(0)
            davinci_resolve_memory_bytes.set(0)
    
    def collect_disk_metrics(self):
        """Collect disk metrics for media storage and cache"""
        # Cache disk metrics
        if self.cache_path.exists():
            try:
                cache_usage = psutil.disk_usage(str(self.cache_path))
                davinci_cache_disk_total_bytes.set(cache_usage.total)
                davinci_cache_disk_used_bytes.set(cache_usage.used)
                davinci_cache_disk_free_bytes.set(cache_usage.free)
            except Exception:
                pass
        
        # Media storage disk metrics
        for media_path in self.media_paths:
            if media_path.exists():
                try:
                    disk_usage = psutil.disk_usage(str(media_path))
                    mount_point = str(media_path)
                    davinci_media_disk_total_bytes.labels(mount_point=mount_point).set(disk_usage.total)
                    davinci_media_disk_used_bytes.labels(mount_point=mount_point).set(disk_usage.used)
                    davinci_media_disk_free_bytes.labels(mount_point=mount_point).set(disk_usage.free)
                    davinci_media_disk_usage_percent.labels(mount_point=mount_point).set(disk_usage.percent)
                except Exception:
                    pass
    
    def collect_project_metrics(self):
        """Collect metrics about DaVinci Resolve projects"""
        # Project databases are typically in AppData
        project_paths = []
        if self.platform == 'Windows':
            resolve_projects = self.appdata_path / 'Resolve Disk Database'
            if resolve_projects.exists():
                project_paths.append(resolve_projects)
        
        total_projects = 0
        total_size = 0
        
        for project_path in project_paths:
            if project_path.exists():
                try:
                    for item in project_path.rglob('*'):
                        if item.is_file():
                            total_size += item.stat().st_size
                            if item.suffix in ['.drp', '.resolve']:
                                total_projects += 1
                except Exception:
                    pass
        
        davinci_project_count.set(total_projects)
        davinci_project_total_size_bytes.set(total_size)
    
    def collect_log_metrics(self):
        """Collect metrics from DaVinci Resolve logs"""
        if not self.log_path.exists():
            return
        
        total_log_size = 0
        error_count = 0
        warning_count = 0
        
        try:
            for log_file in self.log_path.glob('*.log'):
                if log_file.is_file():
                    total_log_size += log_file.stat().st_size
                    
                    # Read recent log entries (last 100 lines to avoid reading huge files)
                    try:
                        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                            # Read last 100 lines
                            lines = f.readlines()[-100:]
                            for line in lines:
                                line_lower = line.lower()
                                if 'error' in line_lower:
                                    error_count += 1
                                elif 'warning' in line_lower or 'warn' in line_lower:
                                    warning_count += 1
                    except Exception:
                        pass
            
            davinci_log_size_bytes.set(total_log_size)
            # Note: Counters should only increase, so we track total
            if error_count > 0:
                davinci_log_errors_total.inc(error_count)
            if warning_count > 0:
                davinci_log_warnings_total.inc(warning_count)
                
        except Exception:
            pass
    
    def collect_gpu_metrics(self):
        """Collect GPU metrics specific to DaVinci Resolve"""
        # This is a placeholder - actual GPU metrics would require
        # GPU-specific libraries like pynvml for NVIDIA or similar for AMD
        # For now, we'll set dummy values to show the structure
        try:
            # Try to get GPU info using psutil (limited)
            # In production, use pynvml for NVIDIA or similar for AMD
            proc = self.find_davinci_process()
            if proc:
                # Set placeholder values
                davinci_gpu_memory_used_bytes.labels(gpu_id='0').set(0)
                davinci_gpu_utilization_percent.labels(gpu_id='0').set(0)
        except Exception:
            pass
    
    def collect_all_metrics(self):
        """Collect all metrics"""
        self.collect_process_metrics()
        self.collect_disk_metrics()
        self.collect_project_metrics()
        self.collect_log_metrics()
        self.collect_gpu_metrics()
        
        # Update info metric
        davinci_resolve_info.info({
            'version': 'unknown',
            'platform': self.platform,
            'install_path': str(self.install_path)
        })


def main():
    """Main function to start the exporter"""
    port = int(os.environ.get('EXPORTER_PORT', '9183'))
    interval = int(os.environ.get('SCRAPE_INTERVAL', '30'))
    
    print(f"Starting DaVinci Resolve Exporter on port {port}")
    print(f"Scrape interval: {interval} seconds")
    
    # Start HTTP server for Prometheus to scrape
    start_http_server(port)
    
    # Create exporter instance
    exporter = DaVinciResolveExporter()
    
    print("DaVinci Resolve Exporter started successfully")
    print(f"Metrics available at http://localhost:{port}/metrics")
    
    # Collect metrics in a loop
    while True:
        try:
            exporter.collect_all_metrics()
        except Exception as e:
            print(f"Error collecting metrics: {e}")
        
        time.sleep(interval)


if __name__ == '__main__':
    main()
