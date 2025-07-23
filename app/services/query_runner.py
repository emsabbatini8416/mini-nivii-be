from sqlalchemy.orm import Session
from sqlalchemy import text

def run_query(session: Session, sql: str):
    result = session.execute(text(sql))
    columns = list(result.keys())
    rows = result.fetchall()
    return {
        "columns": columns,
        "rows": [list(row) for row in rows]
    }
