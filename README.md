# 📊 On-Device Latency Dashboard System

Hệ thống dashboard để theo dõi và phân tích latency của các model AI trên thiết bị di động, bao gồm công cụ chuyển đổi dữ liệu telemetry và dashboard phân tích.

## 🚀 Quick Start

### Cách 1: Docker 🐳 (Recommend)

```bash
cd src

# Start tất cả services
docker-compose up -d

# Xem logs
docker-compose logs -f

# Stop
docker-compose down
```

**Truy cập:**
- 📊 Dashboard: http://localhost:8501
- 🔧 API Docs: http://localhost:8000/docs

### Cách 2: Local (Traditional)

#### Terminal 1 - Backend API:
```bash
cd src/api
pip install -r requirements.txt
python -m uvicorn backend:app --host 0.0.0.0 --port 8000
```

#### Terminal 2 - Dashboard:
```bash
cd src/dashboard
pip install -r requirements.txt
streamlit run app.py --server.port 8501
```


---

## 🏗️ Kiến Trúc Hệ Thống

```
┌─────────────────┐
│   Dashboard     │
│   (Port 8501)   │
└────────┬────────┘
         │
         ↓
┌───────────────────────┐
│    Backend API        │
│    (Port 8000)        │
└──────────┬────────────┘
           │
           ↓
┌──────────────────────┐
│  latency_logs.csv    │
│  (Shared Volume)     │
└──────────────────────┘
```

### 2 Ứng Dụng Độc Lập:

| Ứng Dụng | File | Port | Mô Tả |
|----------|------|------|-------|
| 🔧 Backend API | `api/backend.py` | 8000 | FastAPI REST API để nhận và lưu logs |
| 📊 Dashboard | `dashboard/app.py` | 8501 | Streamlit analytics dashboard |

---

## 📁 Cấu Trúc Project

```
src/
├── 📊 Dashboard
│   ├── dashboard/
│   │   ├── app.py              # Dashboard chính (8501)
│   │   ├── Dockerfile          # Docker image cho dashboard
│   │   └── requirements.txt    # Dependencies
│
├── 🔧 Backend API
│   ├── api/
│   │   ├── backend.py          # FastAPI backend (8000)
│   │   ├── Dockerfile          # Docker image cho API
│   │   └── requirements.txt    # Dependencies
│
├── 🐳 Docker
│   ├── docker-compose.yml      # Docker orchestration
│
└── 📊 Data
    ├── convert.py              # Chuyển đổi telemetry logs → CSV
    ├── latency_logs.csv         # Shared CSV file (mounted volume)
    └── *.txt                    # Telemetry log files (input cho convert.py)
```

---

## ✨ Tính Năng

### 📊 Dashboard (Port 8501)

**3 Tabs chính:**

1. **📊 Overview Tab:**
   - Metrics: Avg, Min, Max, P95 latency, Crash rate, Feedback rate
   - Model Summary Table với thống kê chi tiết
   - Visualizations:
     - Latency over time (line chart)
     - Average latency by model (bar chart)
     - Battery percentage over time
     - Battery drain by model
     - Model performance radar chart
     - Latency distribution (box plot)
     - User feedback histogram
     - Temperature vs Latency scatter plot
   - Raw data table với filtering

2. **📌 Per-Run Analysis Tab:**
   - Chọn run_id để xem chi tiết
   - Metrics cho từng run: latency, battery, temperature, crash rate, feedback
   - Timeline visualizations:
     - Latency timeline
     - Battery timeline
     - Temperature timeline (iOS levels: 0-3)
     - Feedback distribution
   - Crash logs viewer

3. **🆚 Compare Runs Tab:**
   - So sánh nhiều runs cùng lúc
   - Summary table
   - Visualizations:
     - Latency distribution per run (boxplot)
     - Average latency per run
     - Battery comparison
     - Temperature comparison
     - Radar chart comparison
     - Correlation heatmap
     - Battery drain rate
     - Temperature rise trend
     - Crash timeline

**Filters:**
- Model name (multiselect)
- Device model (multiselect)
- App version (multiselect)
- User feedback (multiselect)
- Device temperature (iOS levels: nominal/fair/serious/critical)
- Battery percentage (slider)
- Only crashed sessions (checkbox)

### 🔧 Backend API (Port 8000)

**RESTful API endpoints:**

- `GET /` - Health check
- `GET /health` - Health check
- `POST /api/logs` - Gửi 1 log entry
- `POST /api/logs/batch` - Gửi nhiều logs cùng lúc
- `GET /api/stats` - Lấy statistics (runs, models, devices, avg latency, etc.)
- `GET /api/logs/count` - Đếm tổng số logs
- `DELETE /api/logs/clear` - Xóa tất cả logs (giữ headers)

**Features:**
- Auto-save to CSV (`latency_logs.csv`)
- CORS enabled
- Interactive API docs (Swagger UI tại `/docs`)
- Shared volume với dashboard

### 🛠️ Convert Tool (`convert.py`)

Script Python để chuyển đổi telemetry log files (text format) sang CSV:

**Cách sử dụng:**

1. Đặt file `.txt` chứa telemetry data cùng thư mục với `convert.py`
2. Chỉnh sửa tên file trong script:
   ```python
   input_filename = 'your_log_file.txt'
   output_filename = 'output.csv'
   ```
3. Chạy script:
   ```bash
   python convert.py
   ```

**Tính năng:**
- Làm sạch dữ liệu (remove single quotes, strip whitespace)
- Chuẩn hóa JSON objects thành JSON array
- Parse và chuyển đổi sang DataFrame
- Tự động thêm `run_id` column (mặc định: 6)
- Sắp xếp columns theo thứ tự chuẩn
- Export sang CSV

---

## 🔌 API Usage

### Gửi Single Log:

```bash
curl -X POST http://localhost:8000/api/logs \
  -H "Content-Type: application/json" \
  -d '{
    "run_id": "6",
    "request_id": "req_001",
    "model_name": "GPT-2",
    "latency_ms": 150.5,
    "device_model": "iPhone 14",
    "app_version": "2.0.0",
    "device_temperature": 0,
    "battery_percentage": 80.0
  }'
```

### Python:

```python
import requests

response = requests.post(
    "http://localhost:8000/api/logs",
    json={
        "run_id": "6",
        "request_id": "req_001",
        "model_name": "GPT-2",
        "latency_ms": 150.5,
        "device_model": "iPhone 14",
        "app_version": "2.0.0",
        "device_temperature": 0,  # 0=nominal, 1=fair, 2=serious, 3=critical
        "battery_percentage": 80.0
    }
)
print(response.json())
```

### Batch Logs:

```python
import requests

logs = [
    {
        "run_id": "6",
        "request_id": "req_001",
        "model_name": "GPT-2",
        "latency_ms": 150.5,
        "device_model": "iPhone 14",
        "app_version": "2.0.0"
    },
    {
        "run_id": "6",
        "request_id": "req_002",
        "model_name": "BERT",
        "latency_ms": 200.0,
        "device_model": "iPhone 15",
        "app_version": "2.0.0"
    }
]

response = requests.post(
    "http://localhost:8000/api/logs/batch",
    json=logs
)
```

📝 **Interactive API Docs**: http://localhost:8000/docs

---

## 🎯 Data Model

### Log Entry Schema:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `run_id` | string | ✅ | Run identifier |
| `request_id` | string | ✅ | Unique request identifier |
| `model_name` | string | ✅ | Model name (e.g., GPT-2, BERT-Base, LFM2-V1-6B, Qwen2.5-VL-3B-Instruct-4bit) |
| `latency_ms` | float | ✅ | Latency in milliseconds |
| `device_model` | string | ✅ | Device model (e.g., iPhone 13/14/15 Pro/SE) |
| `app_version` | string | ✅ | App version (e.g., 0.1.0, 1.0.0, 1.1.0, 2.0.0) |
| `crash_log` | string | ❌ | Crash log/error message |
| `user_feedback` | string | ❌ | "up" or "down" |
| `device_temperature` | int | ❌ | iOS thermal state: 0=nominal, 1=fair, 2=serious, 3=critical |
| `battery_percentage` | float | ❌ | Battery level (0-100) |

---

## 🐳 Docker Setup

### Docker Compose Services:

1. **api** (Port 8000)
   - FastAPI backend
   - Mounts `latency_logs.csv` as shared volume
   - Health check enabled

2. **dashboard** (Port 8501)
   - Streamlit dashboard
   - Mounts same `latency_logs.csv` as shared volume
   - Depends on api service

**Shared Volume:**
- `./latency_logs.csv` được mount vào cả 2 containers tại `/app/latency_logs.csv`
- Cho phép dashboard và API chia sẻ cùng một file CSV

### Docker Commands:

```bash
# Build và start
docker-compose up -d

# Rebuild sau khi thay đổi code
docker-compose up -d --build

# Xem logs
docker-compose logs -f

# Stop
docker-compose down

# Stop và xóa volumes
docker-compose down -v
```

---

## ⚙️ Configuration

### Backend API (`api/backend.py`):

- CSV file path: `latency_logs.csv` (trong container: `/app/latency_logs.csv`)
- Port: 8000
- CORS: Enabled cho tất cả origins (development only)

### Dashboard (`dashboard/app.py`):

- Shared log path: `/app/latency_logs.csv` (Docker) hoặc local path
- Port: 8501
- Temperature mapping: 0=nominal, 1=fair, 2=serious, 3=critical

### Convert Tool (`convert.py`):

Chỉnh sửa các biến sau để customize:

```python
input_filename = 'logs+stepladder_Good+Qwen2.5-VL-3B-Instruct-4bit+304.txt'
output_filename = 'telemetry_data_Model Qwen2.5-VL-3B-Instruct-4bit.csv'
df['run_id'] = 6  # Thay đổi run_id mặc định
```

---

## 📝 Requirements

### API Requirements (`api/requirements.txt`):
```
fastapi==0.104.1
uvicorn==0.24.0
pydantic
pandas==2.1.1
```

### Dashboard Requirements (`dashboard/requirements.txt`):
```
streamlit==1.28.1
pandas==2.1.1
plotly==5.17.0
fastapi==0.104.1
uvicorn==0.24.0
requests==2.31.0
```

### Convert Tool:
```
pandas
```

Install:
```bash
# API
cd api && pip install -r requirements.txt

# Dashboard
cd dashboard && pip install -r requirements.txt

# Convert tool
pip install pandas
```

---

## 🔍 Troubleshooting

### Port đã bị sử dụng:

```bash
# Linux/Mac
lsof -i :8000  # Backend
lsof -i :8501  # Dashboard

# Kill process
kill $(lsof -t -i:8000)
```

```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Backend không kết nối:

```bash
# Check backend health
curl http://localhost:8000/health

# Check Docker logs
docker-compose logs api
```

### Dashboard không load data:

- Kiểm tra file `latency_logs.csv` có tồn tại không
- Kiểm tra shared volume trong Docker: `docker-compose exec dashboard ls -la /app/latency_logs.csv`
- Đảm bảo file có headers đúng format

### Dependencies issues:

```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade

# Docker: rebuild
docker-compose up -d --build
```

---

## 💡 Use Cases

### 1. Development & Testing
- Gửi logs từ mobile app qua API (POST /api/logs)
- Monitor latency real-time qua dashboard
- Test performance trên các devices khác nhau
- Track temperature và battery impact

### 2. Performance Analysis
- Upload production logs (CSV) hoặc convert từ telemetry files
- Filter theo device, model, version, temperature
- Identify performance bottlenecks
- Compare multiple runs
- Analyze battery drain patterns

### 3. Reporting
- Generate visualizations cho reports
- Export filtered data
- Share insights với team qua dashboard
- Track crash rates và user feedback

### 4. Data Conversion
- Convert telemetry log files (text) sang CSV format
- Batch process multiple log files
- Standardize data format cho analysis

---

## 🔐 Security Notes

⚠️ **Development Only**: Hệ thống này được thiết kế cho development/testing.

**Cho Production:**
- [ ] Add authentication (JWT, OAuth)
- [ ] Restrict CORS origins
- [ ] Use HTTPS
- [ ] Add rate limiting
- [ ] Validate & sanitize inputs
- [ ] Use database (PostgreSQL) thay vì CSV
- [ ] Add monitoring & alerting
- [ ] Implement backup strategy
- [ ] Secure shared volumes

---

## 🚀 Next Steps

1. ✅ Start system: `docker-compose up -d` hoặc chạy local
2. ✅ Truy cập Dashboard: http://localhost:8501
3. ✅ Convert telemetry files: `python convert.py`
4. ✅ Gửi logs qua API: `POST http://localhost:8000/api/logs` (xem API Usage section)
5. ✅ Explore filters và visualizations trong dashboard
6. ✅ Test API: http://localhost:8000/docs
7. ✅ Integrate với mobile app (xem API examples ở trên)

---

## 📞 Support

- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Dashboard**: http://localhost:8501

---

**🎉 Happy Logging!**

*Version: 2.0 - Multi-App Architecture với Docker Support*  
*Last Updated: December 2025*
*Luong Thi Hoai Le*