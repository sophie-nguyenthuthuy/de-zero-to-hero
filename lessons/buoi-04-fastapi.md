# ⚡ Buổi 4 — Web API & FastAPI

**Data Engineer: Zero to Hero | Phase 1 – Engineering Foundations**
Thời gian: 2.5 tiếng | Lab: 65 phút

## 🎯 Mục tiêu Lab

- Xây dựng REST API hoàn chỉnh với FastAPI + PostgreSQL
- Implement JWT authentication
- Viết health check, validation với Pydantic
- Load test bằng Locust

> **Phụ thuộc Buổi 3:** API thao tác trực tiếp trên các bảng `customers`/`orders` của database `de_lab`. Hoàn thành [Buổi 3](buoi-03-database-sql.md) (schema + seed) trước. App không tự tạo bảng.

---

## PHẦN 1 — Setup Project (5 phút)

```bash
mkdir -p ~/de-lab/b04-fastapi && cd ~/de-lab/b04-fastapi
uv venv --python 3.11 && source .venv/bin/activate

uv add fastapi "uvicorn[standard]" "pydantic[email]" pydantic-settings \
       sqlalchemy psycopg2-binary "python-jose[cryptography]" \
       "passlib[bcrypt]" "bcrypt<4.1" python-multipart
uv add --dev locust httpx pytest pytest-asyncio

mkdir -p app/{routers,models,schemas,services,core} tests
touch app/__init__.py app/routers/__init__.py
```

> **Fix vs bản gốc:** thêm `pydantic[email]` (cho `EmailStr`) và pin `bcrypt<4.1` (passlib 1.7.4 lỗi với bcrypt ≥ 4.1). Xem [README lab](../buoi-04-fastapi/README.md) để biết chi tiết.

---

## PHẦN 2 — App Config & Database (10 phút)

- [`../buoi-04-fastapi/app/core/config.py`](../buoi-04-fastapi/app/core/config.py) — `Settings` qua `pydantic-settings`, property `DATABASE_URL`, JWT config, đọc từ `.env`.
- [`../buoi-04-fastapi/app/core/database.py`](../buoi-04-fastapi/app/core/database.py) — `engine` (`pool_pre_ping`), `SessionLocal`, `Base`, dependency `get_db()`.

> `declarative_base` import từ `sqlalchemy.orm` (đường `sqlalchemy.ext.declarative` đã deprecated ở SQLAlchemy 2.0).

---

## PHẦN 3 — Models, Schemas, Auth (15 phút)

- [`app/models/models.py`](../buoi-04-fastapi/app/models/models.py) — SQLAlchemy `Customer`, `Order` map vào bảng có sẵn.
- [`app/schemas/schemas.py`](../buoi-04-fastapi/app/schemas/schemas.py) — Pydantic v2: `CustomerBase/Create/Response` (validate `customer_id` `^C\d{3,}$`, phone `^0\d{9}$`, `EmailStr`), `Order*`, `PaginatedResponse`, `HealthCheck`, `Token`/`TokenData`.
- [`app/core/auth.py`](../buoi-04-fastapi/app/core/auth.py) — `passlib` bcrypt, JWT (`python-jose`), `OAuth2PasswordBearer`, fake users `admin`/`viewer`, `create_access_token`, `get_current_user`.

> `create_access_token` dùng `datetime.now(timezone.utc)` (thay `datetime.utcnow()` deprecated ở Python 3.12+).

---

## PHẦN 4 — Routers & Main App (15 phút)

- [`app/routers/auth.py`](../buoi-04-fastapi/app/routers/auth.py) — `POST /auth/token` (OAuth2 password flow).
- [`app/routers/customers.py`](../buoi-04-fastapi/app/routers/customers.py) — list (pagination + filter city/search), get by id, create (yêu cầu role `admin`).
- [`app/routers/analytics.py`](../buoi-04-fastapi/app/routers/analytics.py) — `GET /analytics/revenue/monthly`, `GET /analytics/customers/top` (raw SQL parametrized).
- [`app/main.py`](../buoi-04-fastapi/app/main.py) — app factory, CORS, `/` và `/health` (check DB qua `SELECT 1`).

---

## PHẦN 5 — Chạy và Test API (10 phút)

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Health
curl http://localhost:8000/health | python3 -m json.tool

# Lấy token
TOKEN=$(curl -s -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Customers + analytics
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/customers?page=1&page_size=5" | python3 -m json.tool
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/customers?city=HCM" | python3 -m json.tool
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/analytics/revenue/monthly?year=2024" | python3 -m json.tool
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/analytics/customers/top?limit=3" | python3 -m json.tool

# Swagger UI: http://localhost:8000/docs
```

---

## PHẦN 6 — Load Test với Locust (10 phút)

[`../buoi-04-fastapi/locustfile.py`](../buoi-04-fastapi/locustfile.py) — 2 user class (`DEApiUser` admin với task weights, `ReadOnlyUser` viewer).

```bash
mkdir -p reports
locust -f locustfile.py --host http://localhost:8000 --headless \
    --users 50 --spawn-rate 10 --run-time 30s --html reports/load_test.html
# Hoặc UI: locust -f locustfile.py --host http://localhost:8000  ->  http://localhost:8089
```

---

## 📚 Homework

1. Thêm endpoint `GET /orders` với filter theo `status` và `date_from`/`date_to`.
2. Implement Rate Limiting: max 100 requests/minute mỗi IP.
3. Thêm API key authentication song song với JWT.

---

**Buổi tiếp theo:** Buổi 5 — Testing & Docker
