# 📊 On-Device Latency Dashboard System

## 🚀 Quick Start

### Cách 1: Docker🐳

```bash
cd /Users/lethihoailuong/Documents/Hitachi/Streamlit-demo/Streamlit

# Start
./docker-start.sh

# Stop
./docker-stop.sh
```

### Cách 2: Local (Traditional)

```bash
cd /Users/lethihoailuong/Documents/Hitachi/Streamlit-demo/Streamlit

# Start
./start_all.sh

# Stop
./stop_all.sh
```

**Truy cập:**
- 📊 Dashboard: http://localhost:8501
- 📤 Send Logs: http://localhost:8502
- 🔧 API Docs: http://localhost:8000/docs

---

## 🏗️ Kiến Trúc Hệ Thống

```
┌─────────────────┐      ┌─────────────────┐
│   Dashboard     │      │  Send Logs App  │
│   (Port 8501)   │      │   (Port 8502)   │
└────────┬────────┘      └────────┬────────┘
         │                        │
         └───────────┬────────────┘
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
         └──────────────────────┘
```

### 3 Ứng Dụng Độc Lập:

| Ứng Dụng | File | Port | Mô Tả |
|----------|------|------|-------|
| 🔧 Backend API | `backend.py` | 8000 | FastAPI REST API |
| 📊 Dashboard | `app.py` | 8501 | Streamlit analytics dashboard |
| 📤 Send Logs | `sendlog_app.py` | 8502 | Streamlit log submission app |

---

## ✨ Tính Năng

### 📊 Dashboard (Port 8501)
- Upload CSV và phân tích dữ liệu
- Multi-dimensional filtering (model, device, version, temperature, battery, feedback)
- Real-time metrics (Avg, Min, Max, P95 latency, Crash rate, Feedback rate)
- Visualizations:
  - Line chart: Latency over time
  - Radar chart: Model performance comparison
  - Box plot: Latency distribution
  - Scatter plot: Temperature vs Latency
  - Histogram: User feedback by model
- Raw data table viewer

### 📤 Send Logs App (Port 8502)
- **Single Log Form**: Gửi log với đầy đủ context
  - Model name, latency, device, app version
  - Extended fields: temperature, battery, feedback, crash logs
- **Batch Logs**: Generate và gửi nhiều logs cùng lúc
- **Statistics**: View backend stats và log count
- **Management**: Clear all logs

### 🔧 Backend API (Port 8000)
- RESTful API endpoints:
  - `POST /api/logs` - Gửi 1 log
  - `POST /api/logs/batch` - Gửi nhiều logs
  - `GET /api/stats` - Lấy statistics
  - `GET /api/logs/count` - Đếm logs
  - `DELETE /api/logs/clear` - Xóa logs
- Auto-save to CSV
- CORS enabled
- Interactive API docs (Swagger UI)

---

## 📖 Documentation

| File | Mô Tả |
|------|-------|
| `README.md` | File này - Overview và quick start |
| `FINAL_GUIDE.md` | Hướng dẫn chi tiết đầy đủ nhất |
| `API_REFERENCE.md` | API reference với examples (cURL, Python, JS) |
| `RUN_GUIDE.md` | Chi tiết về deployment và troubleshooting |
| `DOCKER_GUIDE.md` | 🐳 Docker deployment guide |

---

## 🔌 API Usage

### Gửi Single Log:
```bash
curl --noproxy '*' -X POST http://localhost:8000/api/logs \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "req_001",
    "model_name": "GPT-2",
    "latency_ms": 150.5,
    "device_model": "iPhone 14",
    "app_version": "2.0.0",
    "device_temperature": 40.0,
    "battery_percentage": 80.0
  }'
```

### Python:
```python
import requests

response = requests.post(
    "http://localhost:8000/api/logs",
    json={
        "request_id": "req_001",
        "model_name": "GPT-2",
        "latency_ms": 150.5,
        "device_model": "iPhone 14",
        "app_version": "2.0.0"
    }
)
print(response.json())
```

📝 **Chi tiết API**: Xem `API_REFERENCE.md`

---

## 📁 Cấu Trúc Project

```
Streamlit/
├── 🚀 Applications
│   ├── app.py              # Dashboard (8501)
│   ├── sendlog_app.py      # Send Logs (8502)
│   └── backend.py          # Backend API (8000)
│
├── 🛠️ Scripts
│   ├── start_all.sh        # Start all services (local)
│   ├── stop_all.sh         # Stop all services (local)
│   ├── docker-start.sh     # Start with Docker 🐳
│   ├── docker-stop.sh      # Stop Docker containers
│   └── test_system.sh      # Test system
│
├── 📚 Documentation
│   ├── README.md           # This file
│   ├── FINAL_GUIDE.md      # Complete guide
│   ├── API_REFERENCE.md    # API docs
│   ├── RUN_GUIDE.md        # Deployment guide
│   └── DOCKER_GUIDE.md     # Docker guide 🐳
│
├── 🐳 Docker Files
│   ├── Dockerfile          # Docker image definition
│   ├── docker-compose.yml  # Services orchestration
│   └── .dockerignore       # Docker ignore patterns
│
├── 📊 Data & Config
│   ├── latency_logs.csv    # Data storage
│   ├── requirements.txt    # Dependencies
│   └── backend.log         # Backend logs
│
└── 🧪 Utilities (optional)
    ├── demo.py
    ├── client.py
    └── randomcsv.py
```

---

## ⚙️ Manual Setup (Alternative)

Nếu không dùng `start_all.sh`, chạy từng service:

### Terminal 1 - Backend:
```bash
cd /Users/lethihoailuong/Documents/Hitachi/Streamlit-demo/Streamlit
python3 -m uvicorn backend:app --host 0.0.0.0 --port 8000
```

### Terminal 2 - Dashboard:
```bash
cd /Users/lethihoailuong/Documents/Hitachi/Streamlit-demo/Streamlit
streamlit run app.py --server.port 8501
```

### Terminal 3 - Send Logs:
```bash
cd /Users/lethihoailuong/Documents/Hitachi/Streamlit-demo/Streamlit
streamlit run sendlog_app.py --server.port 8502
```

---

## Testing

### Test hệ thống:
```bash
./test_system.sh
```

### Test thủ công:
```bash
# Health check
curl http://localhost:8000/health

# Send test log
curl --noproxy '*' -X POST http://localhost:8000/api/logs \
  -H "Content-Type: application/json" \
  -d '{"request_id":"test_001","model_name":"GPT-2","latency_ms":150,"device_model":"iPhone 14","app_version":"1.0.0"}'

# Get stats
curl http://localhost:8000/api/stats
```

---

## 🔍 Troubleshooting

### Port đã bị sử dụng:
```bash
lsof -i :8000  # Backend
lsof -i :8501  # Dashboard
lsof -i :8502  # Send Logs

# Kill process
kill $(lsof -t -i:8000)
```

### Backend không kết nối:
```bash
# Check backend
curl http://localhost:8000/health

# View logs
tail -f backend.log
```

### Dependencies:
```bash
pip install -r requirements.txt
```

**📖 Chi tiết troubleshooting**: Xem `RUN_GUIDE.md`

---

## 💡 Use Cases

### 1. Development & Testing
- Gửi logs từ mobile app qua API
- Monitor latency real-time
- Test performance trên các devices khác nhau

### 2. Performance Analysis
- Upload production logs (CSV)
- Filter theo device, model, version
- Identify performance bottlenecks
- Track temperature/battery impact

### 3. Reporting
- Generate visualizations
- Export filtered data
- Share insights với team

---

## 🎯 Data Model

### Log Entry Schema:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `request_id` | string | ✅ | Unique identifier |
| `model_name` | string | ✅ | Model name (GPT-2, BERT-Base, LFM2-V1-6B, LFM2-VL-450M) |
| `latency_ms` | float | ✅ | Latency in milliseconds |
| `device_model` | string | ✅ | Device (iPhone 13/14/15 Pro/SE) |
| `app_version` | string | ✅ | App version (0.1.0, 1.0.0, 1.1.0, 2.0.0) |
| `crash_log` | string | ❌ | Crash log/error message |
| `user_feedback` | string | ❌ | "up" or "down" |
| `device_temperature` | float | ❌ | Temperature in °C |
| `battery_percentage` | float | ❌ | Battery level (0-100) |

---

## 🔐 Security Notes

⚠️ **Development Only**: Hệ thống này cho development/testing.

**Cho Production:**
- [ ] Add authentication (JWT, OAuth)
- [ ] Restrict CORS origins
- [ ] Use HTTPS
- [ ] Add rate limiting
- [ ] Validate & sanitize inputs
- [ ] Use database (PostgreSQL) thay vì CSV
- [ ] Add monitoring & alerting
- [ ] Implement backup strategy

---

## 🚀 Next Steps

1. ✅ Start system: `./start_all.sh`
2. ✅ Truy cập Dashboard: http://localhost:8501
3. ✅ Upload `latency_logs.csv` để xem sample data
4. ✅ Explore filters và visualizations
5. ✅ Test Send Logs app: http://localhost:8502
6. ✅ Check API docs: http://localhost:8000/docs
7. ✅ Integrate with your app (xem `API_REFERENCE.md`)

---

## 📞 Support

- **Full Documentation**: Đọc `FINAL_GUIDE.md`
- **API Reference**: Đọc `API_REFERENCE.md`
- **Deployment**: Đọc `RUN_GUIDE.md`
- **API Testing**: http://localhost:8000/docs

---

## 📝 Requirements

```
fastapi
uvicorn
streamlit
pandas
plotly
requests
pydantic
```

Install: `pip install -r requirements.txt`

---

**🎉 Happy Logging!**

*Version: 2.0 - Multi-App Architecture*  
*Last Updated: December 2025*

# Latency-Dashboard-Streamlit
