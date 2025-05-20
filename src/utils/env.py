import os
import platform
import subprocess
from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class EnvironmentInfo:
    """Container for environment information."""
    timestamp: datetime
    environment_type: str  # 'bare-metal', 'vm', or 'container'
    hypervisor: Optional[str]  # For VMs
    container_type: Optional[str]  # For containers
    container_id: Optional[str]  # For containers
    hostname: str

class EnvironmentDetector:
    """Class for detecting the execution environment."""
    
    def __init__(self):
        """Initialize the environment detector."""
        self._environment_type = None
        self._hypervisor = None
        self._container_type = None
        self._container_id = None
    
    def _detect_vm(self) -> Optional[str]:
        """Detect if running in a VM and return hypervisor type."""
        if platform.system() == 'Windows':
            try:
                output = subprocess.check_output(
                    'wmic computersystem get manufacturer,model',
                    shell=True
                ).decode()
                if 'VMware' in output:
                    return 'VMware'
                elif 'VirtualBox' in output:
                    return 'VirtualBox'
                elif 'Microsoft' in output and 'Virtual' in output:
                    return 'Hyper-V'
            except:
                pass
        else:
            # Check common VM indicators on Linux
            try:
                with open('/proc/cpuinfo', 'r') as f:
                    cpuinfo = f.read()
                    if 'hypervisor' in cpuinfo:
                        if 'VMware' in cpuinfo:
                            return 'VMware'
                        elif 'KVM' in cpuinfo:
                            return 'KVM'
                        elif 'Xen' in cpuinfo:
                            return 'Xen'
            except:
                pass
        return None

    def _detect_container(self) -> tuple[Optional[str], Optional[str]]:
        """Detect if running in a container and return container type and ID."""
        # Check for Docker
        if os.path.exists('/.dockerenv'):
            container_id = None
            try:
                with open('/proc/self/cgroup', 'r') as f:
                    for line in f:
                        if 'docker' in line:
                            container_id = line.strip().split('/')[-1]
                            break
            except:
                pass
            return 'Docker', container_id
        
        # Check for LXC
        if os.path.exists('/proc/1/environ'):
            try:
                with open('/proc/1/environ', 'r') as f:
                    if 'container=lxc' in f.read():
                        return 'LXC', None
            except:
                pass
        
        return None, None

    def get_environment_info(self) -> EnvironmentInfo:
        """Get current environment information."""
        if self._environment_type is None:
            # Check for container first
            container_type, container_id = self._detect_container()
            if container_type:
                self._environment_type = 'container'
                self._container_type = container_type
                self._container_id = container_id
            else:
                # Check for VM
                hypervisor = self._detect_vm()
                if hypervisor:
                    self._environment_type = 'vm'
                    self._hypervisor = hypervisor
                else:
                    self._environment_type = 'bare-metal'

        return EnvironmentInfo(
            timestamp=datetime.now(),
            environment_type=self._environment_type,
            hypervisor=self._hypervisor,
            container_type=self._container_type,
            container_id=self._container_id,
            hostname=platform.node()
        ) 