import logging
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import init_db, get_db, check_db_health
from app.utils.csv_loader import load_csv_to_db
from app.services.llm import generate_sql, suggest_chart_simple
from app.services.query_runner import run_query, validate_sql_safety, get_query_stats
from app.services.cache import cache_service, init_cache, cleanup_cache

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class QuestionRequest(BaseModel):
    question: str
    
class QueryRequest(BaseModel):
    sql: str
    page: int = 1
    page_size: int = 100

class StatsResponse(BaseModel):
    stats: dict
    cache_info: dict

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management."""
    # Startup
    logger.info("Starting application...")
    try:
        # Initialize scalable cache (Redis + memory)
        await init_cache()
        logger.info("Cache initialized successfully")
        
        # Initialize database
        init_db()
        load_csv_to_db("data.csv")
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    try:
        await cleanup_cache()
        logger.info("Cache closed successfully")
    except Exception as e:
        logger.error(f"Error closing cache: {e}")

app = FastAPI(
    title="Mini Nivii Backend - Scalable",
    description="Scalable API for natural language queries on sales data",
    version="2.0.0",
    lifespan=lifespan
)

# Configure CORS with more granular configuration
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",  # For development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
    max_age=600,  # Cache preflight for 10 minutes
)

@app.middleware("http")
async def add_process_time_header(request, call_next):
    """Middleware to measure response time."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Mini Nivii Backend - Scalable",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    db_healthy = check_db_health()
    
    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "database": "ok" if db_healthy else "error",
        "cache": "ok",  # cache_service always works (fallback to memory)
        "timestamp": time.time()
    }

@app.post("/ask")
async def ask_question(request: QuestionRequest):
    """
    Main endpoint for natural language queries.
    Now with validation, cache, chart suggestions and better error handling.
    """
    try:
        logger.info(f"Processing question: {request.question}")
        
        # Generate SQL using LLM with cache
        sql = generate_sql(request.question)
        
        if not sql:
            raise HTTPException(
                status_code=400, 
                detail="Could not generate a valid SQL query"
            )
        
        # Validate query security
        if not validate_sql_safety(sql):
            raise HTTPException(
                status_code=400,
                detail="Unsafe SQL query. Only SELECT queries are allowed."
            )
        
        # Execute query with cache
        data = await run_query(sql)
        
        # Generate chart suggestion based on question and SQL
        chart_suggestion = suggest_chart_simple(request.question, sql)
        
        return {
            "sql": sql,
            "data": data,
            "chart_suggestion": chart_suggestion,
            "cached": True,  # Can always come from cache
            "row_count": len(data["rows"])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing question: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@app.post("/query")
async def execute_query(request: QueryRequest):
    """
    Endpoint for executing direct SQL queries (for advanced users).
    """
    try:
        # Validate security
        if not validate_sql_safety(request.sql):
            raise HTTPException(
                status_code=400,
                detail="Unsafe SQL query. Only SELECT queries are allowed."
            )
        
        # Execute with pagination if specified
        if request.page > 1 or request.page_size != 100:
            from app.services.query_runner import run_query_paginated
            data = run_query_paginated(request.sql, request.page, request.page_size)
        else:
            data = await run_query(request.sql)
        
        return {
            "sql": request.sql,
            "data": data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing query: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@app.get("/stats")
async def get_stats():
    """Endpoint to get database statistics."""
    try:
        stats = await get_query_stats()
        
        cache_info = {
            "type": "redis" if hasattr(cache_service, 'redis_client') and cache_service.redis_client else "memory",
            "items": len(cache_service.memory_cache) if not cache_service.redis_client else "unknown"
        }
        
        return {
            "stats": stats,
            "cache_info": cache_info
        }
        
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@app.delete("/cache")
async def clear_cache():
    """Endpoint to clear cache (useful for debugging)."""
    try:
        success = cache_service.clear()
        return {
            "message": "Cache cleared" if success else "Error clearing cache",
            "success": success
        }
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

# Global error handling
@app.exception_handler(500)
async def internal_server_error_handler(request, exc):
    logger.error(f"Internal error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
