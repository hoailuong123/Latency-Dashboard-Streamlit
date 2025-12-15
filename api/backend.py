from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import csv
import os
from pathlib import Path

# Initialize FastAPI app
app = FastAPI(
    title="Latency Logger API",
    description="API để thu thập và lưu logs latency vào CSV",
    version="1.0.0"
)

# Add CORS middleware
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Data models
class LatencyLog(BaseModel):
    """Model for latency log entry"""
    run_id: str
    request_id: str
    model_name: str
    latency_ms: float
    device_model: str
    app_version: str
    # Optional extended fields
    crash_log: Optional[str] = None
    user_feedback: Optional[str] = None  # "up", "down"
    device_temperature: Optional[int] = None  # 0: nominal, 1: fair, 2: serious, 3: critical
    battery_percentage: Optional[float] = None  # 0-100

class LatencyLogResponse(BaseModel):
    """Response model"""
    message: str
    data: LatencyLog

# Configuration
CSV_FILE = "latency_logs.csv"
CSV_HEADERS = [
    "run_id",
    "request_id",
    "model_name",
    "latency_ms",
    "device_model",
    "app_version",
    "crash_log",
    "user_feedback",
    "device_temperature",
    "battery_percentage",
]

def ensure_csv_exists():
    """Ensure CSV file exists with headers"""
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            writer.writeheader()

def append_log_to_csv(log: LatencyLog):
    """Append a log entry to the CSV file"""
    ensure_csv_exists()
    
    try:
        with open(CSV_FILE, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            writer.writerow({
                "run_id": log.run_id,
                "request_id": log.request_id,
                "model_name": log.model_name,
                "latency_ms": log.latency_ms,
                "device_model": log.device_model,
                "app_version": log.app_version,
                "crash_log": log.crash_log or "",
                "user_feedback": log.user_feedback or "",
                "device_temperature": log.device_temperature if log.device_temperature is not None else "",
                "battery_percentage": log.battery_percentage if log.battery_percentage is not None else "",
            })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error writing to CSV: {str(e)}")

@app.on_event("startup")
async def startup_event():
    """Initialize CSV file on startup"""
    ensure_csv_exists()
    print(f"✅ CSV file initialized: {CSV_FILE}")

@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "Latency Logger API",
        "version": "1.0.0"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.post("/api/logs", response_model=LatencyLogResponse, tags=["Logging"])
async def create_log(log: LatencyLog):
    """
    Create a new latency log entry and save to CSV
    
    - **request_id**: Unique identifier for the request
    - **model_name**: Name of the model being tested
    - **latency_ms**: Latency in milliseconds
    - **device_model**: Device model name
    - **app_version**: Application version
    """    
    try:
        append_log_to_csv(log)
        return {
            "message": "Log entry created successfully",
            "data": log
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/logs/batch", tags=["Logging"])
async def create_batch_logs(logs: list[LatencyLog]):
    """
    Create multiple latency log entries at once
    
    Takes a list of log entries and saves all to CSV
    """
    try:
        for log in logs:
            append_log_to_csv(log)
        
        return {
            "message": f"Successfully created {len(logs)} log entries",
            "count": len(logs)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/logs/count", tags=["Statistics"])
async def get_logs_count():
    """
    Get total number of logs in CSV file
    """
    ensure_csv_exists()
    
    try:
        with open(CSV_FILE, 'r') as f:
            # Count lines minus 1 for header
            count = sum(1 for _ in f) - 1
        
        return {
            "total_logs": count,
            "csv_file": CSV_FILE
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats", tags=["Statistics"])
async def get_statistics():
    """
    Get statistics from logs
    """
    ensure_csv_exists()
    
    try:
        import pandas as pd
        df = pd.read_csv(CSV_FILE)
        
        if df.empty:
            return {
                "total_records": 0,
                "stats": "No data available"
            }
        
        return {
            "runs": df["run_id"].unique().tolist(),
            "total_records": len(df),
            "avg_latency_ms": float(df['latency_ms'].mean()),
            "min_latency_ms": float(df['latency_ms'].min()),
            "max_latency_ms": float(df['latency_ms'].max()),
            "models": df['model_name'].unique().tolist(),
            "devices": df['device_model'].unique().tolist(),
            "versions": df['app_version'].unique().tolist()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/logs/clear", tags=["Maintenance"])
async def clear_logs():
    """
    Clear all logs from CSV file (keeps headers)
    """
    try:
        ensure_csv_exists()
        with open(CSV_FILE, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            writer.writeheader()
        
        return {
            "message": "All logs cleared successfully",
            "csv_file": CSV_FILE
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
