# Buổi 4 — Web API & FastAPI (Lab)

Code lab cho [Buổi 4](../lessons/buoi-04-fastapi.md). REST API với FastAPI + JWT auth + PostgreSQL, load test bằng Locust.

> **Phụ thuộc Buổi 3:** API đọc/ghi trực tiếp các bảng `customers`/`orders` trong database `de_lab`. Chạy [Buổi 3](../buoi-03-sql/) (schema + seed) trước. App **không** tự tạo bảng (`Base.metadata.create_all()` không được gọi).

## Cấu trúc

```
buoi-04-fastapi/
├── pyproject.toml
├── .env.example          # copy -> .env để override config
├── locustfile.py         # load test (2 user class: admin / viewer)
└── app/
    ├── main.py           # app factory + CORS + /health
    ├── core/
    │   ├── config.py     # pydantic-settings
    │   ├── database.py   # engine + SessionLocal + get_db dependency
    │   └── auth.py       # JWT + passlib, fake users admin/viewer
    ├── models/models.py  # SQLAlchemy Customer / Order
    ├── schemas/schemas.py# Pydantic v2 schemas + validation
    └── routers/          # auth / customers / analytics
```

## Setup

```bash
cd buoi-04-fastapi
uv venv --python 3.11
source .venv/bin/activate
uv sync
```

## Chạy server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# Swagger UI: http://localhost:8000/docs
```

## Test nhanh

```bash
# Health
curl http://localhost:8000/health | python3 -m json.tool

# Lấy token (admin)
TOKEN=$(curl -s -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Gọi endpoint cần auth
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/customers?page=1&page_size=5" | python3 -m json.tool
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/analytics/revenue/monthly?year=2024" | python3 -m json.tool
```

Tài khoản demo: `admin/admin123` (role admin), `viewer/viewer123` (role viewer).

## Load test

```bash
mkdir -p reports
# Headless
locust -f locustfile.py --host http://localhost:8000 --headless \
    --users 50 --spawn-rate 10 --run-time 30s --html reports/load_test.html
# Hoặc UI: locust -f locustfile.py --host http://localhost:8000  ->  http://localhost:8089
```

## Ghi chú (fix so với giáo trình gốc)

- **`pydantic[email]`** trong deps — `EmailStr` cần `email-validator`, bản gốc thiếu nên import lỗi.
- **`bcrypt<4.1`** được pin — passlib 1.7.4 không đọc được version của bcrypt ≥ 4.1 (`AttributeError: __about__`).
- Dùng **`datetime.now(timezone.utc)`** thay `datetime.utcnow()` (deprecated từ Python 3.12).
- `declarative_base` import từ `sqlalchemy.orm` (đường cũ `sqlalchemy.ext.declarative` deprecated ở SQLAlchemy 2.0).
- `SECRET_KEY` mặc định chỉ cho lab — đổi ở production. `.env` đã được `.gitignore`.
