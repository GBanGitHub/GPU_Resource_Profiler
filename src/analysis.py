import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class PerformanceInsight:
    """Container for performance insights."""
    timestamp: datetime
    severity: str  # 'info', 'warning', or 'critical'
    message: str
    metric: str
    value: float
    threshold: float
    suggestion: str

class PerformanceAnalyzer:
    """Class for analyzing GPU performance data and providing insights."""
    
    def __init__(self, config: Dict):
        """Initialize the performance analyzer.
        
        Args:
            config: Configuration dictionary containing alert thresholds
        """
        self.config = config
        self.insights = []
    
    def analyze_profile(self, df: pd.DataFrame) -> List[PerformanceInsight]:
        """Analyze GPU profile data and generate insights.
        
        Args:
            df: DataFrame containing GPU metrics
            
        Returns:
            List of performance insights
        """
        self.insights = []
        
        # Analyze each GPU separately
        for gpu_id in df['device_id'].unique():
            gpu_data = df[df['device_id'] == gpu_id]
            self._analyze_gpu(gpu_data, gpu_id)
        
        return self.insights
    
    def _analyze_gpu(self, gpu_data: pd.DataFrame, gpu_id: int):
        """Analyze metrics for a single GPU."""
        # Check utilization
        self._check_utilization(gpu_data, gpu_id)
        
        # Check memory usage
        self._check_memory_usage(gpu_data, gpu_id)
        
        # Check temperature
        self._check_temperature(gpu_data, gpu_id)
        
        # Check power usage
        self._check_power_usage(gpu_data, gpu_id)
        
        # Check for idle periods
        self._check_idle_periods(gpu_data, gpu_id)
        
        # Check for memory bottlenecks
        self._check_memory_bottlenecks(gpu_data, gpu_id)
    
    def _check_utilization(self, gpu_data: pd.DataFrame, gpu_id: int):
        """Check GPU utilization against thresholds."""
        warning_threshold = self.config['alerts']['gpu']['utilization']['warning']
        critical_threshold = self.config['alerts']['gpu']['utilization']['critical']
        
        # Check for high utilization
        high_util = gpu_data[gpu_data['utilization'] > warning_threshold]
        if not high_util.empty:
            max_util = high_util['utilization'].max()
            if max_util >= critical_threshold:
                self.insights.append(PerformanceInsight(
                    timestamp=high_util.iloc[-1]['timestamp'],
                    severity='critical',
                    message=f"GPU {gpu_id} utilization critically high",
                    metric='utilization',
                    value=max_util,
                    threshold=critical_threshold,
                    suggestion="Consider distributing workload across multiple GPUs or optimizing compute operations"
                ))
            else:
                self.insights.append(PerformanceInsight(
                    timestamp=high_util.iloc[-1]['timestamp'],
                    severity='warning',
                    message=f"GPU {gpu_id} utilization high",
                    metric='utilization',
                    value=max_util,
                    threshold=warning_threshold,
                    suggestion="Monitor for potential performance bottlenecks"
                ))
    
    def _check_memory_usage(self, gpu_data: pd.DataFrame, gpu_id: int):
        """Check GPU memory usage against thresholds."""
        warning_threshold = self.config['alerts']['gpu']['memory']['warning']
        critical_threshold = self.config['alerts']['gpu']['memory']['critical']
        
        # Calculate memory usage percentage
        memory_pct = (gpu_data['memory_used'] / gpu_data['memory_total']) * 100
        
        # Check for high memory usage
        high_mem = gpu_data[memory_pct > warning_threshold]
        if not high_mem.empty:
            max_mem_pct = memory_pct[high_mem.index].max()
            if max_mem_pct >= critical_threshold:
                self.insights.append(PerformanceInsight(
                    timestamp=high_mem.iloc[-1]['timestamp'],
                    severity='critical',
                    message=f"GPU {gpu_id} memory usage critically high",
                    metric='memory',
                    value=max_mem_pct,
                    threshold=critical_threshold,
                    suggestion="Consider reducing batch size or implementing gradient checkpointing"
                ))
            else:
                self.insights.append(PerformanceInsight(
                    timestamp=high_mem.iloc[-1]['timestamp'],
                    severity='warning',
                    message=f"GPU {gpu_id} memory usage high",
                    metric='memory',
                    value=max_mem_pct,
                    threshold=warning_threshold,
                    suggestion="Monitor memory usage and consider optimization if it continues to increase"
                ))
    
    def _check_temperature(self, gpu_data: pd.DataFrame, gpu_id: int):
        """Check GPU temperature against thresholds."""
        warning_threshold = self.config['alerts']['gpu']['temperature']['warning']
        critical_threshold = self.config['alerts']['gpu']['temperature']['critical']
        
        # Check for high temperature
        high_temp = gpu_data[gpu_data['temperature'] > warning_threshold]
        if not high_temp.empty:
            max_temp = high_temp['temperature'].max()
            if max_temp >= critical_threshold:
                self.insights.append(PerformanceInsight(
                    timestamp=high_temp.iloc[-1]['timestamp'],
                    severity='critical',
                    message=f"GPU {gpu_id} temperature critically high",
                    metric='temperature',
                    value=max_temp,
                    threshold=critical_threshold,
                    suggestion="Check cooling system and consider reducing workload or implementing thermal throttling"
                ))
            else:
                self.insights.append(PerformanceInsight(
                    timestamp=high_temp.iloc[-1]['timestamp'],
                    severity='warning',
                    message=f"GPU {gpu_id} temperature high",
                    metric='temperature',
                    value=max_temp,
                    threshold=warning_threshold,
                    suggestion="Monitor temperature and ensure proper cooling"
                ))
    
    def _check_power_usage(self, gpu_data: pd.DataFrame, gpu_id: int):
        """Check GPU power usage against thresholds."""
        warning_threshold = self.config['alerts']['gpu']['power']['warning']
        critical_threshold = self.config['alerts']['gpu']['power']['critical']
        
        # Check for high power usage
        high_power = gpu_data[gpu_data['power_usage'] > warning_threshold]
        if not high_power.empty:
            max_power = high_power['power_usage'].max()
            if max_power >= critical_threshold:
                self.insights.append(PerformanceInsight(
                    timestamp=high_power.iloc[-1]['timestamp'],
                    severity='critical',
                    message=f"GPU {gpu_id} power usage critically high",
                    metric='power',
                    value=max_power,
                    threshold=critical_threshold,
                    suggestion="Consider implementing power limits or optimizing power-intensive operations"
                ))
            else:
                self.insights.append(PerformanceInsight(
                    timestamp=high_power.iloc[-1]['timestamp'],
                    severity='warning',
                    message=f"GPU {gpu_id} power usage high",
                    metric='power',
                    value=max_power,
                    threshold=warning_threshold,
                    suggestion="Monitor power usage and consider optimization if it continues to increase"
                ))
    
    def _check_idle_periods(self, gpu_data: pd.DataFrame, gpu_id: int):
        """Check for idle periods in GPU utilization."""
        idle_threshold = 10  # Consider GPU idle if utilization < 10%
        min_idle_duration = timedelta(minutes=5)  # Minimum duration to consider it an idle period
        
        # Find idle periods
        idle_periods = []
        current_period = None
        
        for idx, row in gpu_data.iterrows():
            if row['utilization'] < idle_threshold:
                if current_period is None:
                    current_period = row['timestamp']
            else:
                if current_period is not None:
                    duration = row['timestamp'] - current_period
                    if duration >= min_idle_duration:
                        idle_periods.append((current_period, row['timestamp']))
                    current_period = None
        
        # Check if there's an ongoing idle period
        if current_period is not None:
            duration = gpu_data.iloc[-1]['timestamp'] - current_period
            if duration >= min_idle_duration:
                idle_periods.append((current_period, gpu_data.iloc[-1]['timestamp']))
        
        # Add insights for idle periods
        for start, end in idle_periods:
            self.insights.append(PerformanceInsight(
                timestamp=end,
                severity='info',
                message=f"GPU {gpu_id} idle period detected",
                metric='utilization',
                value=idle_threshold,
                threshold=idle_threshold,
                suggestion=f"Consider scheduling other workloads during idle periods ({start} to {end})"
            ))
    
    def _check_memory_bottlenecks(self, gpu_data: pd.DataFrame, gpu_id: int):
        """Check for memory bottlenecks based on utilization and memory patterns."""
        # Look for high memory usage with low utilization
        memory_pct = (gpu_data['memory_used'] / gpu_data['memory_total']) * 100
        potential_bottlenecks = gpu_data[
            (memory_pct > 80) &  # High memory usage
            (gpu_data['utilization'] < 50)  # Low utilization
        ]
        
        if not potential_bottlenecks.empty:
            self.insights.append(PerformanceInsight(
                timestamp=potential_bottlenecks.iloc[-1]['timestamp'],
                severity='warning',
                message=f"GPU {gpu_id} potential memory bottleneck detected",
                metric='memory_utilization_ratio',
                value=memory_pct[potential_bottlenecks.index].mean(),
                threshold=80,
                suggestion="Consider optimizing memory access patterns or reducing memory footprint"
            )) 