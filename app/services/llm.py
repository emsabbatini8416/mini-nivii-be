import os
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
