# Tasker – Asynchronous Task Execution Service

A production-style asynchronous task processing service built with FastAPI, Celery, PostgreSQL and Redis.

This project demonstrates:
- Fire-and-forget task submission
- Durable persistence
- Background execution
- Caching layer
- Scalable architecture
- Clean decoupling between API and workers
- Versioned database schema (Alembic)
- Full Docker-based setup

---

## 🏗 Architecture Overview

### Components

| Component | Responsibility |
|------------|---------------|
| FastAPI (API) | Accepts requests, validates input, persists tasks, enqueues jobs |
| PostgreSQL | Durable source of truth |
| Redis (Broker) | Message broker for Celery |
| Redis (Cache) | Caching task results (TTL-based) |
| Celery Worker | Executes tasks asynchronously |
| Alembic | Database migrations & schema versioning |

### Flow

1. Client submits `/run-task`
2. API stores task as `PENDING`
3. API sends message to Redis broker
4. Worker consumes task
5. Worker updates status (`RUNNING → SUCCESS / FAILED`)
6. Result stored in PostgreSQL
7. Frequently requested outputs cached in Redis

API never blocks waiting for execution.

---

## 🚀 Getting Started

### Prerequisites

- Docker Desktop (includes Docker Compose)
- (Optional) Make

Verify installation:

```bash
docker --version
docker compose version
````

---

## ⚙️ Setup

Create environment file:

```bash
cp .env.example .env
```

Then start development environment:

```bash
make dev
```

or:

```bash
docker compose --profile dev up --build
```

Swagger UI:

```
http://localhost:8000/docs
```

---

## 🧪 Run Tests

```bash
make test
```

All tests should pass successfully.

---

## 🛑 Stop

```bash
docker compose --profile dev down
```

To reset database (development only):

```bash
docker compose --profile dev down -v
```

---

## 📡 API

### 1️⃣ Run Task

**POST** `/run-task`

Example:

```bash
curl -X POST http://localhost:8000/run-task \
  -H "Content-Type: application/json" \
  -d '{"task_name":"sum","task_parameters":{"a":10,"b":25}}'
```

Response:

```json
{
  "uuid": "f3c..."
}
```

---

### 2️⃣ Get Task Output

**GET** `/get-task-output?task_uuid=<UUID>`

Example:

```bash
curl "http://localhost:8000/get-task-output?task_uuid=<UUID>"
```

Response:

```json
{
  "task_uuid": "...",
  "status": "SUCCESS",
  "task_output": { ... },
  "error": null
}
```

---

## 🧩 Supported Tasks

### `sum`

Adds two numbers.

```json
{ "a": 10, "b": 25 }
```

---

### `word_count` (Custom Task)

Counts words and characters.

```json
{ "text": "hello world" }
```

---

### `chatgpt`

Supports two modes:

#### Mock mode (default)

```
OPENAI_ENABLED=false
```

No external API required.

#### Live mode

```
OPENAI_ENABLED=true
OPENAI_API_KEY=<your_key>
```

Calls OpenAI Responses API.

If no quota/billing is available, task will fail gracefully.

---

### `boom` (Failure simulation)

Used for testing FAILED status handling.

---

## 🗄 Persistence & Migrations

* Schema managed with Alembic
* Containers automatically run:

```bash
alembic upgrade head
```

* Database survives restarts
* Indexed columns for efficient querying

---

## 🧠 Design Decisions

### Why PostgreSQL?

Durable persistence with strong consistency guarantees.

### Why Redis?

Used both as:

* Celery broker
* Result cache (TTL-based)

Keeps stack minimal and efficient.

### Why Celery?

Mature distributed task queue with horizontal scaling support.

### Why Alembic?

Versioned schema management suitable for production systems.

---

## 📈 Scalability

Scale workers horizontally:

```bash
docker compose --profile prod up --build --scale worker=3
```

The system scales linearly with additional workers.

---

## 🔒 Production Considerations

* API and workers are fully decoupled
* DB is authoritative source of truth
* Cache is best-effort
* Tasks are idempotent-safe
* Failure paths are persisted
* Sensitive configuration handled via environment variables

---

## 📌 Notes

This project prioritizes correctness and architecture quality over surface features.

All components are containerized and environment-agnostic.

---

## 👩‍💻 Author

Noy Saadon


