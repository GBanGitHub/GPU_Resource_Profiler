import pynvml
import psutil
from typing import Dict, List, Optional, Tuple, Any
import time
from dataclasses import dataclass
from datetime import datetime
import warnings

# Suppress pynvml deprecation warning
warnings.filterwarnings('ignore', message='.*pynvml.*deprecated.*')

def _decode_name(name):
    """Handle both bytes and string returns from pynvml."""
    if isinstance(name, bytes):
        return name.decode('utf-8')
    return name

@dataclass
class GPUStats:
    """Container for GPU statistics."""
    timestamp: datetime
    device_id: int
    name: str
    utilization: float  # GPU utilization percentage
    memory_used: int    # Used memory in MB
    memory_total: int   # Total memory in MB
    temperature: float  # Temperature in Celsius
    power_usage: float  # Power usage in watts
    processes: List[Dict[str, Any]]  # List of processes using the GPU

class GPUMonitor:
    """Class for monitoring NVIDIA GPU resources."""
    
    def __init__(self):
        """Initialize the GPU monitor."""
        try:
            pynvml.nvmlInit()
            self.device_count = pynvml.nvmlDeviceGetCount()
        except pynvml.NVMLError as e:
            raise RuntimeError(f"Failed to initialize NVML: {e}")

    def __del__(self):
        """Cleanup NVML on object destruction."""
        try:
            pynvml.nvmlShutdown()
        except Exception:
            pass

    def get_gpu_stats(self, device_id: int) -> GPUStats:
        """Get statistics for a specific GPU device."""
        try:
            handle = pynvml.nvmlDeviceGetHandleByIndex(device_id)
            
            # Get basic device info
            name = _decode_name(pynvml.nvmlDeviceGetName(handle))
            
            # Get utilization info
            utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
            
            # Get memory info
            memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            
            # Get temperature
            temperature = pynvml.nvmlDeviceGetTemperature(
                handle, pynvml.NVML_TEMPERATURE_GPU
            )
            
            # Get power usage
            try:
                power_usage = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0  # Convert to watts
            except pynvml.NVMLError:
                power_usage = 0.0  # Power monitoring not available
            
            # Get running processes
            processes = []
            try:
                process_list = pynvml.nvmlDeviceGetComputeRunningProcesses(handle)
                for proc in process_list:
                    try:
                        process = psutil.Process(proc.pid)
                        processes.append({
                            'pid': proc.pid,
                            'name': process.name(),
                            'memory_used': proc.usedGpuMemory // 1024 // 1024,  # Convert to MB
                            'username': process.username()
                        })
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
            except pynvml.NVMLError:
                pass

            return GPUStats(
                timestamp=datetime.now(),
                device_id=device_id,
                name=name,
                utilization=utilization.gpu,
                memory_used=memory_info.used // 1024 // 1024,  # Convert to MB
                memory_total=memory_info.total // 1024 // 1024,  # Convert to MB
                temperature=temperature,
                power_usage=power_usage,
                processes=processes
            )
        except pynvml.NVMLError as e:
            raise RuntimeError(f"Failed to get GPU stats for device {device_id}: {e}")

    def get_all_gpu_stats(self) -> List[GPUStats]:
        """Get statistics for all available GPUs."""
        return [self.get_gpu_stats(i) for i in range(self.device_count)]

    def get_gpu_count(self) -> int:
        """Get the number of available GPUs."""
        return self.device_count

    def get_gpu_names(self) -> List[str]:
        """Get names of all available GPUs."""
        try:
            return [
                _decode_name(pynvml.nvmlDeviceGetName(
                    pynvml.nvmlDeviceGetHandleByIndex(i)
                ))
                for i in range(self.device_count)
            ]
        except pynvml.NVMLError as e:
            raise RuntimeError(f"Failed to get GPU names: {e}") 