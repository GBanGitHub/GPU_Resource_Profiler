import time
import json
from datetime import datetime
from typing import Dict, List, Optional
import os
from pathlib import Path
import logging
from dataclasses import asdict

from src.utils.gpu import GPUMonitor, GPUStats
from src.utils.system import SystemMonitor
from src.utils.env import EnvironmentDetector, EnvironmentInfo

class GPUProfiler:
    """Main GPU profiler class that coordinates monitoring and data collection."""
    
    def __init__(self, output_dir: str = "profiles", sampling_interval: float = 1.0):
        """Initialize the GPU profiler.
        
        Args:
            output_dir: Directory to store profile data
            sampling_interval: Time between samples in seconds
        """
        self.output_dir = Path(output_dir)
        self.sampling_interval = sampling_interval
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize monitoring components
        self.gpu_monitor = GPUMonitor()
        self.system_monitor = SystemMonitor()
        self.env_detector = EnvironmentDetector()
        
        # Setup logging
        self._setup_logging()
        
        # Initialize data storage
        self.current_profile = {
            'start_time': datetime.now().isoformat(),
            'environment': None,
            'system_info': None,
            'gpu_stats': []
        }
    
    def _setup_logging(self):
        """Setup logging configuration."""
        log_file = self.output_dir / f"profile_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _collect_sample(self) -> Dict:
        """Collect a single sample of all metrics."""
        try:
            # Get environment info (only once)
            if self.current_profile['environment'] is None:
                self.current_profile['environment'] = asdict(
                    self.env_detector.get_environment_info()
                )
            
            # Get system info
            system_info = self.system_monitor.get_system_info()
            self.current_profile['system_info'] = asdict(system_info)
            
            # Get GPU stats
            gpu_stats = self.gpu_monitor.get_all_gpu_stats()
            self.current_profile['gpu_stats'].append([
                asdict(stat) for stat in gpu_stats
            ])
            
            return {
                'timestamp': datetime.now().isoformat(),
                'system_info': asdict(system_info),
                'gpu_stats': [asdict(stat) for stat in gpu_stats]
            }
        except Exception as e:
            self.logger.error(f"Error collecting sample: {e}")
            return None
    
    def _save_profile(self):
        """Save the current profile to a JSON file."""
        try:
            output_file = self.output_dir / f"profile_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w') as f:
                json.dump(self.current_profile, f, indent=2)
            self.logger.info(f"Profile saved to {output_file}")
        except Exception as e:
            self.logger.error(f"Error saving profile: {e}")
    
    def start_profiling(self, duration: Optional[float] = None):
        """Start profiling GPU resources.
        
        Args:
            duration: Optional duration in seconds. If None, runs until interrupted.
        """
        self.logger.info("Starting GPU profiling...")
        start_time = time.time()
        
        try:
            while True:
                sample = self._collect_sample()
                if sample:
                    self.logger.info(
                        f"Collected sample - GPU Utilization: "
                        f"{[stat['utilization'] for stat in sample['gpu_stats']]}%"
                    )
                
                # Check if duration has elapsed
                if duration and (time.time() - start_time) >= duration:
                    break
                
                time.sleep(self.sampling_interval)
        
        except KeyboardInterrupt:
            self.logger.info("Profiling interrupted by user")
        except Exception as e:
            self.logger.error(f"Error during profiling: {e}")
        finally:
            self._save_profile()
            self.logger.info("Profiling completed")

def main():
    """Main entry point for the GPU profiler."""
    import argparse
    
    parser = argparse.ArgumentParser(description="GPU Resource Profiler")
    parser.add_argument(
        "--output-dir",
        default="profiles",
        help="Directory to store profile data"
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=1.0,
        help="Sampling interval in seconds"
    )
    parser.add_argument(
        "--duration",
        type=float,
        help="Duration to profile in seconds (optional)"
    )
    
    args = parser.parse_args()
    
    profiler = GPUProfiler(
        output_dir=args.output_dir,
        sampling_interval=args.interval
    )
    profiler.start_profiling(duration=args.duration)

if __name__ == "__main__":
    main() 