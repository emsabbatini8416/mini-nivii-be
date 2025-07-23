# 🚀 Nivii Challenge Backend

Scalable API that converts **natural language** into SQL queries on sales data using **OpenAI** + **FastAPI**, now with **intelligent chart suggestions** for data visualization.

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
| `/ask` | POST | **Natural language question + Smart chart suggestion** |

## 💬 Usage Examples

### Natural Language Query with Smart Chart Suggestion
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the top 5 best-selling products?"}'

# Response includes:
# - sql: Generated SQL query
# - data: Query results  
# - chart_suggestion: Smart chart recommendation based on query pattern
```

### Direct SQL Query  
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"sql": "SELECT COUNT(*) FROM sales"}'
```

## 📊 Smart Chart Suggestions

The API now intelligently suggests the most appropriate chart type based on your natural language question and the generated SQL query using **rule-based pattern matching**:

### Supported Chart Types
- **Bar Chart**: For comparisons, rankings, and grouped data
- **Line Chart**: For trends over time and temporal data
- **Pie Chart**: For proportions and percentages  
- **Table**: For detailed data inspection

### Example Response
```json
{
  "sql": "SELECT product_name, SUM(quantity) as total_sold FROM sales GROUP BY product_name ORDER BY total_sold DESC LIMIT 5",
  "data": {
    "columns": ["product_name", "total_sold"],
    "rows": [["Alfajor Sin Azucar Suelto", 4566.0], ["Alf. 150 aniv. Suelto", 3795.0], ...]
  },
  "chart_suggestion": {
    "chart_type": "bar",
    "title": "Top Results",
    "description": "Bar chart recommended for rankings"
  },
  "cached": true,
  "row_count": 5
}
```

## 🏗️ Scalable Architecture

✅ **Redis Cache** - Distributed cache for fast responses  
✅ **Streaming CSV** - Efficient loading without full `pd.read_csv()`  
✅ **Multi-Worker** - 4 concurrent Gunicorn workers  
✅ **Health Checks** - Automatic service monitoring  
✅ **Connection Pooling** - Optimized DB connection management  
✅ **Smart Chart Suggestions** - Rule-based visualization recommendations

## 📊 Tech Stack

- **FastAPI** + **Uvicorn** - High-performance async API
- **OpenAI GPT-4** - Natural language → SQL conversion  
- **Redis** - Scalable distributed cache
- **SQLAlchemy** - ORM with connection pooling
- **SQLite** - Database with 24K+ records
- **Docker** - Multi-stage containerization

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
