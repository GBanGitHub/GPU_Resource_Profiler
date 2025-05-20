import unittest
import os
import json
import time
from pathlib import Path
import yaml
import sys
from datetime import datetime
import pandas as pd

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.profiler import GPUProfiler
from src.analysis import PerformanceAnalyzer
from src.utils.gpu import GPUMonitor
from src.utils.system import SystemMonitor
from src.utils.env import EnvironmentDetector

class TestGPUProfiler(unittest.TestCase):
    """Test cases for the GPU Resource Profiler."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        # Load configuration
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'config.yaml')
        with open(config_path, 'r') as f:
            cls.config = yaml.safe_load(f)
        
        # Create test output directory
        cls.test_output_dir = "test_profiles"
        os.makedirs(cls.test_output_dir, exist_ok=True)
    
    def setUp(self):
        """Set up each test case."""
        self.profiler = GPUProfiler(
            output_dir=self.test_output_dir,
            sampling_interval=0.1  # Use a small interval for testing
        )
    
    def tearDown(self):
        """Clean up after each test case."""
        # Remove test profile files
        for file in Path(self.test_output_dir).glob('profile_*.json'):
            file.unlink()
        for file in Path(self.test_output_dir).glob('profile_*.log'):
            file.unlink()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        # Remove test directory
        if os.path.exists(cls.test_output_dir):
            os.rmdir(cls.test_output_dir)
    
    def test_gpu_monitor_initialization(self):
        """Test GPU monitor initialization."""
        try:
            monitor = GPUMonitor()
            self.assertIsInstance(monitor.get_gpu_count(), int)
            self.assertGreaterEqual(monitor.get_gpu_count(), 0)
        except RuntimeError as e:
            self.skipTest(f"GPU monitoring not available: {e}")
    
    def test_system_monitor_initialization(self):
        """Test system monitor initialization."""
        monitor = SystemMonitor()
        system_info = monitor.get_system_info()
        self.assertIsNotNone(system_info.hostname)
        self.assertIsNotNone(system_info.os_name)
        self.assertGreater(system_info.cpu_count, 0)
    
    def test_environment_detection(self):
        """Test environment detection."""
        detector = EnvironmentDetector()
        env_info = detector.get_environment_info()
        self.assertIn(env_info.environment_type, ['bare-metal', 'vm', 'container'])
    
    def test_profiler_data_collection(self):
        """Test profiler data collection."""
        try:
            # Run profiler for a short duration
            self.profiler.start_profiling(duration=1.0)
            
            # Check if profile file was created
            profile_files = list(Path(self.test_output_dir).glob('profile_*.json'))
            self.assertEqual(len(profile_files), 1)
            
            # Check profile data
            with open(profile_files[0], 'r') as f:
                profile_data = json.load(f)
            
            self.assertIn('start_time', profile_data)
            self.assertIn('environment', profile_data)
            self.assertIn('system_info', profile_data)
            self.assertIn('gpu_stats', profile_data)
            self.assertGreater(len(profile_data['gpu_stats']), 0)
        except RuntimeError as e:
            self.skipTest(f"GPU profiling not available: {e}")
    
    def test_performance_analysis(self):
        """Test performance analysis."""
        # Create sample data
        sample_data = {
            'start_time': datetime.now().isoformat(),
            'environment': {
                'environment_type': 'bare-metal',
                'hostname': 'test-host'
            },
            'system_info': {
                'hostname': 'test-host',
                'os_name': 'Linux',
                'cpu_count': 4
            },
            'gpu_stats': [
                [
                    {
                        'timestamp': datetime.now().isoformat(),
                        'device_id': 0,
                        'name': 'Test GPU',
                        'utilization': 95.0,
                        'memory_used': 8000,
                        'memory_total': 10000,
                        'temperature': 85.0,
                        'power_usage': 95.0,
                        'processes': []
                    }
                ]
            ]
        }
        
        # Save sample data
        profile_file = Path(self.test_output_dir) / 'test_profile.json'
        with open(profile_file, 'w') as f:
            json.dump(sample_data, f)
        
        # Analyze profile
        analyzer = PerformanceAnalyzer(self.config)
        insights = analyzer.analyze_profile(pd.DataFrame(sample_data['gpu_stats'][0]))
        
        # Check if insights were generated
        self.assertGreater(len(insights), 0)
        
        # Check if critical alerts were generated
        critical_insights = [i for i in insights if i.severity == 'critical']
        self.assertGreater(len(critical_insights), 0)

if __name__ == '__main__':
    unittest.main() 