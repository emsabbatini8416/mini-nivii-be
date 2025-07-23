import re
import logging
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_session
from app.services.cache import cache_service, cache_result

logger = logging.getLogger(__name__)

def validate_sql_safety(sql: str) -> bool:
    """
    Validates that the SQL query is safe (only SELECT).
    Critical for scalability and security with multiple users.
    """
    # Clean query
    sql_clean = sql.strip().upper()
    
    # Only allow SELECT
    if not sql_clean.startswith('SELECT'):
        logger.warning(f"Unsafe query detected: {sql[:50]}...")
        return False
    
    # Forbidden words to prevent SQL injection
    forbidden_patterns = [
        r'\bDROP\b', r'\bDELETE\b', r'\bINSERT\b', r'\bUPDATE\b',
        r'\bALTER\b', r'\bCREATE\b', r'\bTRUNCATE\b', r'\bEXEC\b',
        r'\bSYSTEM\b', r'\bSHUTDOWN\b'
    ]
    
    for pattern in forbidden_patterns:
        if re.search(pattern, sql_clean):
            logger.warning(f"Forbidden pattern detected: {pattern}")
            return False
    
    return True

@cache_result(prefix="sql_query", ttl=300)
async def run_query(sql: str) -> Dict[str, Any]:
    """
    Executes query with automatic cache for scalability.
    Avoids re-executing identical queries for 5 minutes.
    """
    logger.info(f"Executing SQL query: {sql[:50]}...")
    
    session = get_session()
    try:
        result = session.execute(text(sql))
        columns = list(result.keys())
        rows = result.fetchall()
        
        query_result = {
            "columns": columns,
            "rows": [list(row) for row in rows]
        }
        
        logger.info(f"Query executed successfully: {len(rows)} rows")
        return query_result
        
    except Exception as e:
        logger.error(f"Error executing query: {e}")
        raise
    finally:
        session.close()

def run_query_paginated(sql: str, page: int = 1, page_size: int = 100) -> Dict[str, Any]:
    """
    Executes query with pagination for large datasets.
    Improves scalability by avoiding loading all results.
    """
    if page < 1:
        page = 1
    if page_size > 1000:  # Limit page size
        page_size = 1000
    
    offset = (page - 1) * page_size
    
    # Modify SQL to add LIMIT and OFFSET
    paginated_sql = f"{sql} LIMIT {page_size} OFFSET {offset}"
    
    result = run_query(paginated_sql)
    
    # Add pagination metadata
    result["pagination"] = {
        "page": page,
        "page_size": page_size,
        "has_more": len(result["rows"]) == page_size
    }
    
    return result

@cache_result(prefix="stats", ttl=600)
async def get_query_stats() -> Dict[str, List[Any]]:
    """
    Gets database statistics with cache.
    Cache for 10 minutes for efficiency.
    """
    stats = {}
    
    # Basic statistics queries
    stat_queries = {
        "total_sales": "SELECT COUNT(*) FROM sales",
        "total_revenue": "SELECT SUM(total) FROM sales", 
        "unique_products": "SELECT COUNT(DISTINCT product_name) FROM sales",
        "date_range": """
            SELECT 
                MIN(date) as earliest_date,
                MAX(date) as latest_date
            FROM sales
        """
    }
    
    for stat_name, sql in stat_queries.items():
        try:
            result = run_query(sql)
            stats[stat_name] = result["rows"][0] if result["rows"] else [0]
        except Exception as e:
            logger.error(f"Error getting statistic {stat_name}: {e}")
            stats[stat_name] = [0]
    
    return stats
