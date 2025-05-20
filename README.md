# GPU Resource Profiler

## Overview
The GPU Resource Profiler is a Python-based tool designed to help users monitor and analyze GPU usage during AI training jobs or other GPU-intensive workloads. It provides a structured way to collect, store, and visualize GPU statistics, making it easier to identify performance bottlenecks, optimize resource allocation, and troubleshoot issues.

## Features
- **Comprehensive GPU Monitoring**: Collects data on GPU utilization, memory usage, temperature, power consumption, and active processes.
- **Historical Data Storage**: Saves time-stamped GPU statistics in JSON files for later analysis.
- **Profile Management**: Supports multiple profiling sessions, allowing users to compare GPU usage across different jobs or time periods.
- **Customizable Alerts**: Users can set thresholds for utilization, memory, temperature, and power to receive warnings when limits are exceeded.
- **Extensible and Modular**: Built with modular Python scripts for easy customization and extension.

## How It Works
1. **Data Collection**: The profiler uses NVIDIA's NVML library (via `pynvml`) and the `psutil` library to gather real-time statistics from all available GPUs. This includes metrics such as:
   - GPU utilization percentage
   - Memory used (in MB)
   - Temperature (in Celsius)
   - Power usage (in Watts)
   - List of active processes using the GPU
2. **Sampling and Storage**: At a user-defined interval (set in `config/config.yaml`), the profiler samples these statistics and appends them to a structured list. After the profiling session, the data is saved as a JSON file in the `profiles/` directory. Each file represents a profiling session and contains all collected samples.
3. **Analysis and Visualization**: The collected profile files can be loaded for analysis or visualization. The project includes scripts and a dashboard (optional) for plotting trends, comparing sessions, and examining process-level GPU usage.

## Getting Started
### Prerequisites
- Python 3.8 or higher
- NVIDIA GPU with drivers and NVML support (for full functionality)
- Required Python packages (see `requirements.txt`)

### Installation
1. **Clone the repository:**
   ```sh
   git clone https://github.com/GBanGitHub/GPU_Resource_Profiler.git
   cd GPU_Resource_Profiler
   ```
2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

### Profiling Workflow
1. **Configure Profiling:**
   - Edit `config/config.yaml` to set the sampling interval, output directory, alert thresholds, and other options.
2. **Run the Profiler:**
   - Use the provided Python scripts to start a profiling session. The profiler will collect GPU stats at the specified interval and save them to a JSON file in the `profiles/` directory.
3. **Analyze Results:**
   - Load the generated profile files for analysis or visualization. You can use the included dashboard or write your own scripts to process the JSON data.

## File Structure
```
GPU_Resource_Profiler/
├── config/
│   └── config.yaml         # Main configuration file
├── profiles/               # Directory for storing GPU profile JSON files
│   └── profile_4090_sample.json
├── src/
│   ├── dashboard.py        # (Optional) Dashboard web app for visualization
│   ├── gpu.py              # GPU monitoring utilities
│   ├── system.py           # System info utilities
│   └── ...
├── tests/                  # Test scripts
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
```

## Example Profile File Format
Each profile file is a JSON document containing a list of time-stamped GPU statistics. Example:
```json
{
  "gpu_stats": [
    [
      {
        "timestamp": "2024-06-01T12:00:00",
        "device_id": 0,
        "name": "NVIDIA RTX 4090",
        "utilization": 67,
        "memory_used": 16384,
        "temperature": 62,
        "power_usage": 320,
        "processes": [
          {"pid": 4321, "name": "python.exe", "memory_used": 12000, "username": "user1"}
        ]
      }
    ]
  ]
}
```

## Configuration
- **config/config.yaml**: Central configuration file for the profiler. You can set:
  - Sampling interval (how often stats are collected)
  - Output directory for profile files
  - Alert thresholds for GPU metrics
  - Export and dashboard options

## Use Cases
- **Performance Optimization**: Identify underutilized or overburdened GPUs during training jobs.
- **Resource Tracking**: Monitor how different users or jobs consume GPU resources over time.
- **Troubleshooting**: Detect issues like overheating, memory leaks, or abnormal power usage.
- **Comparative Analysis**: Compare GPU usage across different sessions or hardware setups.

## License
This project is open source and available under the MIT License. 