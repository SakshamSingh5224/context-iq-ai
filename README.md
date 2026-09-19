# ContextIQ AI

An operational risk and decision-intelligence platform. ContextIQ AI takes an operation (title, priority, location), combines it with live weather data, computes a **deterministic risk score**, and asks an **LLM copilot** (Groq) for a concise 3-step intervention strategy. Every assessment is stored, so you get a running risk history.

**Stack:** FastAPI · SQLAlchemy + SQLite · React 18 + Vite + Tailwind CSS 4 · Recharts · Groq · Open-Meteo · Docker · Render · Vercel

---

## How it works

```
React (Vite)  ──HTTP/JSON──▶  FastAPI  ──▶  SQLite (operations, risk events)
                                 ├──▶ Open-Meteo API  (live weather)
                                 ├──▶ Risk engine     (weighted score)
                                 └──▶ Groq LLM        (intervention strategy)
```

Risk score: `R = 0.35·Internal + 0.30·External + 0.20·TimePressure + 0.15·Historical`, mapped to **low / medium / high / critical**.

- **Internal** risk comes from the operation's priority.
- **External** risk comes from precipitation and wind speed at the operation's coordinates.
- **Time pressure** and **historical** risk are currently static placeholders.

## Project structure

```
context-iq-ai/
├── backend/
│   ├── main.py              # FastAPI app, routes, CORS
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── services/            # risk_engine, external_data (weather), copilot (Groq)
│   ├── test_*.py            # pytest suite
│   └── Dockerfile
├── frontend/
│   ├── src/                 # App, api client, components (RiskGauge, AssessmentCard, RiskEventsTable)
│   ├── nginx.conf
│   └── Dockerfile
├── docker-compose.yml
└── .env.example
```

## Run with Docker (recommended)

Requires Docker Desktop.

```bash
cp .env.example .env          # Windows: copy .env.example .env
# edit .env and set GROQ_API_KEY
docker compose up --build
```

| Service     | URL                        |
| ----------- | -------------------------- |
| Frontend    | http://localhost:3000      |
| Backend API | http://localhost:8000      |
| API docs    | http://localhost:8000/docs |

Stop with `docker compose down` (add `-v` to also wipe the database volume).

## Run without Docker

**Backend**

```bash
cd backend
python -m venv venv
venv\Scripts\activate         # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
copy .env.example .env        # macOS/Linux: cp .env.example .env  (then add GROQ_API_KEY)
uvicorn main:app --reload
```

**Frontend**

```bash
cd frontend
npm install
copy .env.example .env        # macOS/Linux: cp .env.example .env
npm run dev                   # http://localhost:5173
```

**Tests**

```bash
cd backend
pytest -v
```

## API

| Method | Endpoint                                   | Description                                   |
| ------ | ------------------------------------------ | --------------------------------------------- |
| GET    | `/`                                        | Health check                                  |
| POST   | `/api/v1/operations`                       | Create an operation                           |
| POST   | `/api/v1/operations/{id}/assess`           | Score risk, save the event, get AI strategy   |
| GET    | `/api/v1/risk-events`                      | Latest risk events across all operations      |
| GET    | `/api/v1/operations/{id}/risk-history`     | Risk events for one operation                 |

Interactive docs: `/docs` (Swagger UI).

## Environment variables

| Variable            | Where    | Purpose                                                        |
| ------------------- | -------- | -------------------------------------------------------------- |
| `GROQ_API_KEY`      | Backend  | Enables the AI copilot strategy                                |
| `DATABASE_URL`      | Backend  | Optional. Defaults to `sqlite:///./contextiq.db`               |
| `ALLOWED_ORIGINS`   | Backend  | Comma-separated CORS origins (production)                      |
| `ALLOWED_ORIGIN_REGEX` | Backend | Optional regex for extra origins, e.g. Vercel previews      |
| `VITE_API_BASE_URL` | Frontend | Backend base URL, baked in at build time                       |

## Deployment

- **Backend → Render** (Docker runtime, root directory `backend`). Set `GROQ_API_KEY` and `ALLOWED_ORIGINS`.
- **Frontend → Vercel** (Vite preset, root directory `frontend`). Set `VITE_API_BASE_URL` to the Render URL.

> SQLite on Render's free tier is ephemeral: data resets on each deploy. Use a persistent disk or PostgreSQL for durable data.

## Roadmap

- [ ] Real time-pressure and historical-risk inputs
- [ ] Authentication
- [ ] PostgreSQL support
- [ ] CI with GitHub Actions
