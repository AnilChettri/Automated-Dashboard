# 🧠 Decision Intelligence System

> Not just a dashboard — a **decision intelligence platform** powered by AI, ML, and real-time analytics.

## Architecture

```
Frontend (React) ──→ FastAPI Backend ──→ PostgreSQL/SQLite
                                    ──→ ML Models (sklearn, XGBoost, Prophet)
                                    ──→ OpenAI API (GPT-4.1 + Embeddings)
                                    ──→ FAISS Vector Store
```

## Quick Start

### 1. Setup Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate       # Windows
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy and edit .env
cp ../.env.example ../.env
# Add your OPENAI_API_KEY
```

### 3. Seed Database

```bash
python -m scripts.seed_data
```

### 4. Run Server

```bash
uvicorn app.main:app --reload --port 8000
```

### 5. Access API

- **Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health**: [http://localhost:8000/health](http://localhost:8000/health)

## Features

| Feature | Status | Description |
|---------|--------|-------------|
| 📊 KPI Dashboard | ✅ | Revenue, orders, customers, AOV with trends |
| 📈 Revenue Trends | ✅ | Daily/weekly/monthly with period comparison |
| 🏆 Top Products | ✅ | Best sellers by revenue or quantity |
| 👥 Customer Segments | ✅ | RFM-based segmentation (K-Means) |
| 🔮 Churn Prediction | 🔄 | XGBoost churn probability |
| 📉 Forecasting | 🔄 | Prophet time series forecasting |
| 🤖 Ask Your Data | 🔄 | NL → SQL via GPT-4.1 |
| 💡 Auto Insights | 🔄 | AI-generated business insights |
| 🎯 Recommendations | 🔄 | Rule + ML hybrid recommendations |
| ⚡ Alerts | 🔄 | Anomaly detection & notifications |

## API Endpoints

### Analytics
- `GET /api/analytics/kpi?period=30d` — KPI metrics
- `GET /api/analytics/revenue-trend?period=30d&granularity=daily` — Revenue trend
- `GET /api/analytics/top-products?limit=10` — Top products
- `GET /api/analytics/segments` — Customer segments
- `GET /api/analytics/rfm` — RFM distribution

### AI Chat
- `GET /api/chat/status` — Chat availability
- `POST /api/chat/ask` — Ask a question (NL → SQL)

### Insights
- `GET /api/insights/latest` — Latest AI insights
- `POST /api/insights/{id}/rate?rating=5` — Rate insight

### Database
- `GET /api/db/stats` — Table row counts

## Deployment

Configured for **Render** deployment. See `render.yaml`.

## License

MIT
