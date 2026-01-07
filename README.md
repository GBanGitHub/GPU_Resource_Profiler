# GPU Resource Profiler

## Overview
The GPU Resource Profiler is a Python-based tool designed to help users monitor and analyze GPU usage during AI training jobs or other GPU-intensive workloads. It provides a structured way to collect, store, and visualize GPU statistics, making it easier to identify performance bottlenecks, optimize resource allocation, and troubleshoot issues.

## Features
- **Comprehensive GPU Monitoring**: Collects data on GPU utilization, memory usage, temperature, power consumption, and active processes.
- **Historical Data Storage**: Saves time-stamped GPU statistics in JSON files for later analysis.
- **Profile Management**: Supports multiple profiling sessions, allowing users to compare GPU usage across different jobs or time periods.
- **Customizable Alerts**: Users can set thresholds for utilization, memory, temperature, and power to receive warnings when limits are exceeded.
- **REST API**: FastAPI-based REST API for programmatic access to GPU metrics.
- **Web Dashboard**: Interactive dashboard for real-time visualization of GPU metrics.
- **CLI Tool**: Easy-to-use command-line interface for all operations.
- **Extensible and Modular**: Built with modular Python scripts for easy customization and extension.

## Quick Start

### Prerequisites
- Python 3.8 or higher
- NVIDIA GPU with drivers and NVML support
- pip package manager

### Installation

**Option 1: Install as a package (Recommended)**
```bash
git clone https://github.com/GBanGitHub/GPU_Resource_Profiler.git
cd GPU_Resource_Profiler
pip install -e .
```

**Option 2: Install dependencies only**
```bash
git clone https://github.com/GBanGitHub/GPU_Resource_Profiler.git
cd GPU_Resource_Profiler
pip install -r requirements.txt
```

### Basic Usage

After installation, you can use the `gpu-profiler` command:

**1. Check GPU Information**
```bash
gpu-profiler info
```
Displays current GPU status including utilization, memory, temperature, and power usage.

**2. Start Profiling**
```bash
# Profile for 60 seconds
gpu-profiler profile --duration 60

# Profile with custom interval and output directory
gpu-profiler profile --interval 0.5 --output-dir my_profiles

# Profile until interrupted (Ctrl+C)
gpu-profiler profile
```

**3. List Available Profiles**
```bash
gpu-profiler list-profiles
```
Shows all profile files with their size and modification time.

**4. Analyze a Profile**
```bash
gpu-profiler analyze profiles/profile_20240601_120000.json
```
Analyzes a profile file and generates performance insights with warnings and suggestions.

**5. Launch Web Dashboard**
```bash
gpu-profiler dashboard

# Custom host and port
gpu-profiler dashboard --host 0.0.0.0 --port 8080
```
Then open http://localhost:8050 in your browser to view interactive graphs and real-time metrics.

**6. Start REST API Server**
```bash
gpu-profiler api

# Custom host and port
gpu-profiler api --host 0.0.0.0 --port 8000
```
API documentation available at http://localhost:8000/docs

### Using with Docker

**Build and run with Docker Compose:**
```bash
docker-compose up
```

The API will be available at `http://localhost:8000`

**Build manually:**
```bash
docker build -t gpu-profiler .
docker run --gpus all -p 8000:8000 gpu-profiler
```

## How It Works

1. **Data Collection**: The profiler uses NVIDIA's NVML library (via `pynvml`) and the `psutil` library to gather real-time statistics from all available GPUs. This includes metrics such as:
   - GPU utilization percentage
   - Memory used (in MB)
   - Temperature (in Celsius)
   - Power usage (in Watts)
   - List of active processes using the GPU

2. **Sampling and Storage**: At a user-defined interval, the profiler samples these statistics and appends them to a structured list. After the profiling session, the data is saved as a JSON file in the `profiles/` directory. Each file represents a profiling session and contains all collected samples.

3. **Analysis and Visualization**: The collected profile files can be loaded for analysis or visualization. The project includes a web dashboard and CLI analysis tool for plotting trends, comparing sessions, and examining process-level GPU usage.

## CLI Commands Reference

```bash
gpu-profiler --help              # Show all available commands
gpu-profiler info                # Display current GPU information
gpu-profiler profile             # Start profiling GPUs
gpu-profiler list-profiles       # List all profile files
gpu-profiler analyze <file>      # Analyze a profile file
gpu-profiler dashboard           # Launch web dashboard
gpu-profiler api                 # Start REST API server
```

### Profile Command Options
```bash
--output-dir DIR     Directory to store profile data (default: profiles)
--interval FLOAT     Sampling interval in seconds (default: 1.0)
--duration FLOAT     Duration to profile in seconds (optional)
```

### Dashboard Command Options
```bash
--host HOST          Host to bind the dashboard (default: localhost)
--port PORT          Port to bind the dashboard (default: 8050)
--config FILE        Path to config file (default: config/config.yaml)
```

### API Command Options
```bash
--host HOST          Host to bind the API server (default: 0.0.0.0)
--port PORT          Port to bind the API server (default: 8000)
```

## REST API Endpoints

- `GET /` - API information
- `GET /gpus` - Get all GPU information
- `GET /gpu/{gpu_id}` - Get specific GPU information
- `GET /gpu/{gpu_id}/processes` - Get processes running on a specific GPU

Full API documentation is available at `/docs` when the API server is running.

## File Structure
```
GPU_Resource_Profiler/
├── config/
│   └── config.yaml         # Main configuration file
├── profiles/               # Directory for storing GPU profile JSON files
│   └── profile_4090_sample.json
├── src/
│   ├── __init__.py
│   ├── cli.py             # Unified CLI entry point
│   ├── profiler.py        # GPU profiler main logic
│   ├── dashboard.py       # Dashboard web app for visualization
│   ├── analysis.py        # Performance analysis utilities
│   ├── api/
│   │   ├── __init__.py
│   │   └── main.py        # FastAPI REST API
│   └── utils/
│       ├── __init__.py
│       ├── gpu.py         # GPU monitoring utilities
│       ├── system.py      # System info utilities
│       └── env.py         # Environment detection utilities
├── tests/                 # Test scripts
├── Dockerfile             # Docker container definition
├── docker-compose.yml     # Docker Compose configuration
├── setup.py               # Package installation script
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
```

## Example Profile File Format
Each profile file is a JSON document containing a list of time-stamped GPU statistics. Example:
```json
{
  "start_time": "2024-06-01T12:00:00",
  "environment": {
    "environment_type": "bare-metal",
    "hostname": "workstation-01"
  },
  "gpu_stats": [
    [
      {
        "timestamp": "2024-06-01T12:00:00",
        "device_id": 0,
        "name": "NVIDIA RTX 4090",
        "utilization": 67,
        "memory_used": 16384,
        "memory_total": 24576,
        "temperature": 62,
        "power_usage": 320,
        "processes": [
          {"pid": 4321, "name": "python", "memory_used": 12000, "username": "user1"}
        ]
      }
    ]
  ]
}
```

## Configuration
The `config/config.yaml` file allows you to customize:
- **Profiling settings**: Sampling interval, output directory, log level
- **Alert thresholds**: Warning and critical thresholds for GPU metrics
- **Dashboard settings**: Port, host, refresh interval, theme
- **Export settings**: Format, compression, Prometheus integration

Example configuration:
```yaml
profiling:
  sampling_interval: 1.0
  output_dir: profiles
  log_level: "INFO"

alerts:
  gpu:
    utilization:
      warning: 90
      critical: 95
    memory:
      warning: 85
      critical: 90
    temperature:
      warning: 80
      critical: 85
```

## Use Cases
- **Performance Optimization**: Identify underutilized or overburdened GPUs during training jobs.
- **Resource Tracking**: Monitor how different users or jobs consume GPU resources over time.
- **Troubleshooting**: Detect issues like overheating, memory leaks, or abnormal power usage.
- **Comparative Analysis**: Compare GPU usage across different sessions or hardware setups.
- **CI/CD Integration**: Use the API to monitor GPU usage in automated pipelines.
- **Multi-user Environments**: Track resource usage across multiple users and projects.

## Troubleshooting

**"Failed to initialize NVML" error:**
- Ensure NVIDIA drivers are properly installed
- Check that your GPU is NVIDIA (AMD/Intel GPUs are not supported)
- Run with sudo if permission issues occur

**Import errors after installation:**
- Make sure you installed the package: `pip install -e .`
- Try reinstalling: `pip uninstall gpu-resource-profiler && pip install -e .`

**Dashboard not loading profiles:**
- Ensure the `profiles/` directory exists
- Check that profile files follow the naming pattern `profile_*.json`
- Verify the config file path is correct

## Development

To contribute or modify the profiler:

```bash
# Clone the repository
git clone https://github.com/GBanGitHub/GPU_Resource_Profiler.git
cd GPU_Resource_Profiler

# Install in development mode
pip install -e .

# Run tests
python -m pytest tests/

# Make your changes and test
gpu-profiler info
```

## License
This project is open source and available under the MIT License.

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Submit a pull request
- Check the documentation at `/docs` when running the API server
