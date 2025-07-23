import os
from typing import Dict, Any
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

PROMPT = """
You are a SQL query generator. Convert natural language questions into valid SQL queries for a SQLite database.

Database: Single table 'sales' with sales data loaded from CSV
Columns: date, week_day, hour, ticket_number, waiter, product_name, quantity, unitary_price, total

Data structure:
- Each row = one product sold in a transaction
- ticket_number = unique identifier for each customer transaction
- To count customers, use COUNT(DISTINCT ticket_number)

RULES:
1. Return ONLY the SQL query, no explanations
2. Use proper SQLite syntax
3. For customer counts: COUNT(DISTINCT ticket_number)
4. For product sales: SUM(quantity) GROUP BY product_name

Examples:
"Cuantos clientes hay?" → SELECT COUNT(DISTINCT ticket_number) as total_clientes FROM sales;
"Total de ventas?" → SELECT SUM(total) as total_ventas FROM sales;

Question:"""

def generate_sql(question: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": PROMPT},
            {"role": "user", "content": question}
        ]
    )
    return response.choices[0].message.content.strip()

def suggest_chart_simple(question: str, sql_query: str) -> Dict[str, Any]:
    """
    Simple rule-based chart suggestion based on SQL query patterns.
    No OpenAI call needed - uses pattern matching.
    """
    sql_lower = sql_query.lower()
    question_lower = question.lower()
    
    # Default suggestion
    suggestion = {
        "chart_type": "table",
        "title": "Query Results",
        "description": "Table view for detailed data inspection"
    }
    
    # Rule-based suggestions
    if "group by" in sql_lower:
        if "product_name" in sql_lower:
            if "sum(" in sql_lower or "count(" in sql_lower:
                suggestion = {
                    "chart_type": "bar",
                    "title": "Product Sales Comparison",
                    "description": "Bar chart recommended for comparing products"
                }
        elif "week_day" in sql_lower or "day" in sql_lower:
            suggestion = {
                "chart_type": "bar",
                "title": "Sales by Day",
                "description": "Bar chart recommended for daily comparisons"
            }
        elif "hour" in sql_lower:
            suggestion = {
                "chart_type": "line",
                "title": "Sales by Hour",
                "description": "Line chart recommended for hourly trends"
            }
        elif "date" in sql_lower:
            suggestion = {
                "chart_type": "line",
                "title": "Sales Over Time",
                "description": "Line chart recommended for time series data"
            }
    
    # Check for top/ranking queries
    if any(word in question_lower for word in ["top", "best", "ranking", "mayor", "mejor"]):
        if "limit" in sql_lower:
            suggestion["chart_type"] = "bar"
            suggestion["title"] = f"Top Results"
            suggestion["description"] = "Bar chart recommended for rankings"
    
    # Check for percentage or proportion queries
    if any(word in question_lower for word in ["percentage", "proportion", "porcentaje", "proporción"]):
        suggestion["chart_type"] = "pie"
        suggestion["title"] = "Distribution"
        suggestion["description"] = "Pie chart recommended for proportions"
    
    return suggestion
