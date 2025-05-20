# GPU Resource Profiler

## Overview
The GPU Resource Profiler is a tool designed to monitor, record, and visualize GPU usage statistics during AI training jobs or other GPU-intensive tasks. It helps users understand how their GPU resources are being utilized, identify bottlenecks, and optimize performance. The project includes a real-time dashboard for visualizing GPU metrics and supports exporting profiling data for further analysis.

## Features
- **Real-time GPU monitoring**: Tracks utilization, memory usage, temperature, power, and active processes.
- **Data export**: Saves profiling data in JSON format for later review or analysis.
- **Interactive dashboard**: Visualizes GPU metrics and process information using a web-based interface.
- **Customizable alerts**: Warns when GPU metrics exceed configurable thresholds.
- **Support for multiple GPUs**: Monitors all available GPUs in the system.

## How It Works
1. **Profiling**: The profiler collects GPU statistics at regular intervals (configurable in `config/config.yaml`). It uses libraries like `pynvml` and `psutil` to gather data such as utilization, memory usage, temperature, power draw, and running processes.
2. **Data Storage**: Collected data is saved as JSON files in the `profiles/` directory. Each file contains time-stamped samples of GPU stats.
3. **Dashboard**: The dashboard (built with Dash and Plotly) reads these profile files and displays interactive graphs and tables. Users can select different profiles and time ranges to analyze GPU usage patterns.

## Getting Started
### Prerequisites
- Python 3.8+
- NVIDIA GPU with drivers and NVML support (for full functionality)

### Installation
1. **Clone the repository:**
   ```sh
   git clone <repo-url>
   cd GPU_Resource_Profiler
   ```
2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

### Running the Profiler
- (If you have a profiling script, run it to generate profile files in the `profiles/` directory.)
- Or, add sample profile files manually for testing.

### Running the Dashboard
```sh
python src/dashboard.py
```
- Open your browser and go to [http://localhost:8050](http://localhost:8050) (or the port specified in `config/config.yaml`).
- Select a profile file from the dropdown to view GPU usage statistics.

## File Structure
```
GPU_Resource_Profiler/
├── config/
│   └── config.yaml         # Configuration file for profiling and dashboard
├── profiles/               # Directory for storing GPU profile JSON files
│   └── profile_4090_sample.json
├── src/
│   ├── dashboard.py        # Dashboard web app
│   ├── gpu.py              # GPU monitoring utilities
│   ├── system.py           # System info utilities
│   └── ...
├── tests/                  # Test scripts
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
```

## Example Profile File Format
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

## Why Use This Tool?
- **Performance optimization**: Identify GPU bottlenecks and optimize training jobs.
- **Resource tracking**: Monitor how different jobs or users utilize GPU resources.
- **Troubleshooting**: Detect overheating, memory leaks, or abnormal power usage.

## License
This project is open source and available under the MIT License. 