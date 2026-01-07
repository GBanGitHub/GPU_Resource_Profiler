from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import pynvml
from datetime import datetime
import warnings

# Suppress pynvml deprecation warning
warnings.filterwarnings('ignore', message='.*pynvml.*deprecated.*')

def _decode_name(name):
    """Handle both bytes and string returns from pynvml."""
    if isinstance(name, bytes):
        return name.decode('utf-8')
    return name

app = FastAPI(
    title="GPU Resource Profiler API",
    description="API for monitoring GPU resources and performance metrics",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize NVML
try:
    pynvml.nvmlInit()
except pynvml.NVMLError as e:
    print(f"Failed to initialize NVML: {e}")

class GPUInfo(BaseModel):
    id: int
    name: str
    temperature: float
    memory_total: int
    memory_used: int
    memory_free: int
    utilization_gpu: float
    utilization_memory: float
    power_usage: float
    timestamp: datetime

@app.get("/")
async def root():
    return {"message": "GPU Resource Profiler API"}

@app.get("/gpus", response_model=List[GPUInfo])
async def get_gpus():
    try:
        device_count = pynvml.nvmlDeviceGetCount()
        gpus = []
        
        for i in range(device_count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            
            # Get GPU info
            name = pynvml.nvmlDeviceGetName(handle)
            temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
            
            # Get memory info
            memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            
            # Get utilization
            utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
            
            # Get power usage
            power = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0  # Convert to watts
            
            gpu_info = GPUInfo(
                id=i,
                name=_decode_name(name),
                temperature=temp,
                memory_total=memory_info.total,
                memory_used=memory_info.used,
                memory_free=memory_info.free,
                utilization_gpu=utilization.gpu,
                utilization_memory=utilization.memory,
                power_usage=power,
                timestamp=datetime.now()
            )
            gpus.append(gpu_info)
            
        return gpus
    except pynvml.NVMLError as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/gpu/{gpu_id}", response_model=GPUInfo)
async def get_gpu(gpu_id: int):
    try:
        handle = pynvml.nvmlDeviceGetHandleByIndex(gpu_id)
        
        # Get GPU info
        name = pynvml.nvmlDeviceGetName(handle)
        temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
        
        # Get memory info
        memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
        
        # Get utilization
        utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
        
        # Get power usage
        power = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0  # Convert to watts
        
        return GPUInfo(
            id=gpu_id,
            name=_decode_name(name),
            temperature=temp,
            memory_total=memory_info.total,
            memory_used=memory_info.used,
            memory_free=memory_info.free,
            utilization_gpu=utilization.gpu,
            utilization_memory=utilization.memory,
            power_usage=power,
            timestamp=datetime.now()
        )
    except pynvml.NVMLError as e:
        raise HTTPException(status_code=404, detail=f"GPU {gpu_id} not found: {str(e)}")

@app.get("/gpu/{gpu_id}/processes")
async def get_gpu_processes(gpu_id: int):
    try:
        handle = pynvml.nvmlDeviceGetHandleByIndex(gpu_id)
        processes = pynvml.nvmlDeviceGetComputeRunningProcesses(handle)
        
        process_info = []
        for process in processes:
            try:
                process_info.append({
                    "pid": process.pid,
                    "used_memory": process.usedGpuMemory,
                    "gpu_id": gpu_id
                })
            except Exception as e:
                continue
                
        return process_info
    except pynvml.NVMLError as e:
        raise HTTPException(status_code=404, detail=f"GPU {gpu_id} not found: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 