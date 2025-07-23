# 🚀 Nivii Challenge Backend

Scalable API that c## 🏗️ Scalable Architecture

✅ **Redis Cache** - Distributed cache for fast responses  
✅ **Streaming CSV** - Efficient loading without full `pd.read_csv()`  
✅ **Multi-Worker** - 4 concurrent Gunicorn workers  
✅ **Health Checks** - Automatic service monitoring  
✅ **Connection Pooling** - Optimized DB connection management  

## 📊 Tech Stack

- **FastAPI** + **Uvicorn** - High-performance async API
- **OpenAI GPT** - Natural language → SQL conversion  
- **Redis** - Scalable distributed cache
- **SQLAlchemy** - ORM with connection pooling
- **SQLite** - Database with 24K+ records
- **Docker** - Multi-stage containerizationl language** into SQL queries on sales data using **OpenAI** + **FastAPI**.

## 🔥 Quick Start

### 1. Launch with Docker Compose
```bash
# Clone and enter directory
git clone <repo-url>
cd nivii-challenge-be

# Configure environment variables
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Launch entire stack
docker-compose up --build
```

### 2. Test the API
- **Swagger UI**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Statistics**: http://localhost:8000/stats

## 🎯 Main Endpoints

| Endpoint | Method | Description |
|----------|---------|-------------|
| `/docs` | GET | **Interactive Swagger UI** |
| `/health` | GET | System health check |
| `/stats` | GET | Data statistics |
| `/query` | POST | Direct SQL query |
| `/natural-query` | POST | **Natural language question** |

## 💬 Usage Example

```bash
# Natural language question
curl -X POST "http://localhost:8000/natural-query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the top 5 best-selling products?"}'

# Direct SQL query  
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"sql": "SELECT COUNT(*) FROM sales"}'
```

## 🏗️ Arquitectura Escalable

✅ **Redis Cache** - Cache distribuido para respuestas rápidas  
✅ **Streaming CSV** - Carga eficiente sin `pd.read_csv()` completo  
✅ **Multi-Worker** - 4 workers Gunicorn concurrentes  
✅ **Health Checks** - Monitoreo automático de servicios  
✅ **Connection Pooling** - Gestión optimizada de conexiones DB  

## � Stack Tecnológico

- **FastAPI** + **Uvicorn** - API async de alto rendimiento
- **OpenAI GPT** - Conversión lenguaje natural → SQL  
- **Redis** - Cache distribuido escalable
- **SQLAlchemy** - ORM con connection pooling
- **SQLite** - Base de datos con 24K+ registros
- **Docker** - Contenedorización multi-stage

## 📊 Data

**24,212 sales records** with columns:
- `date`, `week_day`, `hour` - Temporal information
- `ticket_number`, `waiter` - Identifiers
- `product_name`, `quantity`, `unitary_price`, `total` - Sales data

## 🔧 Local Development

```bash
# View logs in real time
docker-compose logs -f backend

# Stop services
docker-compose down

# Clean volumes (reset data)
docker-compose down --volumes
```

## 📄 License

MIT License
