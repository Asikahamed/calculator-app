# Calculator API

A simple REST API built with FastAPI, designed as a hands-on DevOps learning project covering CI/CD, Docker, Terraform, and GCP deployment (Cloud Run + GKE).

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.12 |
| Framework | FastAPI |
| Validation | Pydantic v2 |
| Storage | In-memory (dict) |
| Metrics | Prometheus (`/metrics`) |
| Containerization | Docker (multi-stage) |
| CI/CD | GitHub Actions |
| Infrastructure | Terraform |
| Cloud | Google Cloud Platform |

---

## Project Structure

```
calculator-api/
├── app/
│   ├── calculator.py     # Pure business logic — add, subtract, multiply, divide, power, modulo
│   ├── schemas.py        # Pydantic request/response models
│   ├── store.py          # In-memory calculation history store
│   └── main.py           # FastAPI routes + Prometheus metrics
├── tests/
│   ├── test_calculator.py  # Unit tests for business logic (20 tests)
│   └── test_main.py        # Integration tests for API endpoints (25 tests)
├── Dockerfile            # Multi-stage build — tests run inside build
├── docker-compose.yml    # Local development
├── requirements.txt
└── pyproject.toml        # Pytest + coverage config
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check — used by Cloud Run and GKE probes |
| `POST` | `/calculate` | Perform a calculation |
| `GET` | `/history` | Get all past calculations (most recent first) |
| `GET` | `/history/{id}` | Get a specific calculation by ID |
| `DELETE` | `/history` | Clear all calculation history |
| `GET` | `/metrics` | Prometheus metrics endpoint |
| `GET` | `/docs` | Swagger UI |
| `GET` | `/redoc` | ReDoc UI |

### Supported Operations

`add` `subtract` `multiply` `divide` `power` `modulo`

---

## Getting Started

### Prerequisites

- Python 3.12+
- Docker
- pip

### Run Locally (Python)

```bash
# Clone the repo
git clone https://github.com/your-org/calculator-api.git
cd calculator-api

# Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
uvicorn app.main:app --reload --port 8080
```

App is live at http://localhost:8080
Swagger UI at http://localhost:8080/docs

### Run Locally (Docker)

```bash
# Build and run
docker-compose up --build

# Or manually
docker build -t calculator-api .
docker run -p 8080:8080 calculator-api
```

> Note: Docker build runs all tests in the test stage. Build fails if any test fails.

---

## Usage Examples

### Perform a Calculation

```bash
curl -X POST http://localhost:8080/calculate \
  -H "Content-Type: application/json" \
  -d '{"operation": "add", "a": 10, "b": 5}'
```

```json
{
  "id": "3f7a1c2d-...",
  "operation": "add",
  "a": 10.0,
  "b": 5.0,
  "result": 15.0,
  "timestamp": "2025-02-19T10:30:00Z"
}
```

### Divide by Zero (validation in action)

```bash
curl -X POST http://localhost:8080/calculate \
  -H "Content-Type: application/json" \
  -d '{"operation": "divide", "a": 10, "b": 0}'
```

```json
{
  "detail": "Division by zero is not allowed"
}
```

### Get History

```bash
curl http://localhost:8080/history
```

```json
{
  "total": 2,
  "records": [...]
}
```

---

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# With coverage report
pytest tests/ --cov=app --cov-report=term-missing

# Fail if coverage drops below 80%
pytest tests/ --cov=app --cov-fail-under=80
```

Expected output:
```
tests/test_calculator.py ....................   [ 20 passed ]
tests/test_main.py .........................   [ 25 passed ]

Coverage: 95%
```

---

## CI/CD Pipeline

```
Push to main
    └── GitHub Actions
        ├── Job 1: python-ci      → lint + test + coverage
        ├── Job 2: docker-build   → build image + push to Artifact Registry
        ├── Job 3: deploy-dev     → auto deploy to Cloud Run (dev)
        └── Job 4: deploy-prod    → manual approval → Cloud Run (prod)
```

Reusable workflows live in the [platform-workflows](https://github.com/your-org/platform-workflows) repo.
Authentication to GCP uses **Workload Identity Federation (OIDC)** — no static keys stored anywhere.

---

## Infrastructure

All GCP resources are managed via Terraform in the [infra](https://github.com/your-org/infra) repo.

| Resource | Tool |
|----------|------|
| Artifact Registry | Terraform |
| Cloud Run (dev + prod) | Terraform |
| GKE Cluster | Terraform |
| Workload Identity Federation | Terraform |
| Monitoring + Alerts | Terraform |

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ENV` | Environment name | `local` |
| `LOG_LEVEL` | Logging level | `info` |

No secrets required to run locally.

---

## Deployment Targets

| Environment | Platform | URL |
|-------------|----------|-----|
| Dev | Cloud Run | Auto-deployed on merge to main |
| Prod | Cloud Run | Requires manual approval |
| Dev (K8s) | GKE | Deployed via `kubectl` / GitHub Actions |

---

## Design Decisions

**Separation of concerns** — `calculator.py` contains pure functions with zero FastAPI dependency. Business logic can be tested independently of the web framework.

**Multi-stage Docker build** — the test stage runs `pytest` inside the build. A failed test means a failed image build, making it impossible to push a broken image.

**Pydantic enum validation** — invalid operations (`sqrt`, `log`, etc.) return a `422 Unprocessable Entity` from Pydantic before your code even runs.

**Test isolation** — the `autouse=True` pytest fixture clears the in-memory store before every test, ensuring no test can affect another.

---

## License

MIT
