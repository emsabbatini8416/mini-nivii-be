from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.database import init_db, get_session
from app.utils.csv_loader import load_csv_to_db
from app.services.llm import generate_sql
from app.services.query_runner import run_query

class QuestionRequest(BaseModel):
    question: str

app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()
    load_csv_to_db("/app/data.csv")

@app.post("/ask")
def ask_question(req: QuestionRequest):
    session = get_session()
    try:
        sql = generate_sql(req.question)
        data = run_query(session, sql)
        return {"sql": sql, "data": data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
