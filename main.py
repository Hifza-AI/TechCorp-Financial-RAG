import os
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# AUTOMATIC Absolute Path Setup taake modules aaram se load hon
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# 🎯 SAFE IMPORT: Agar query_router directly para hai ya retrieval folder ke andar hai, dono ko handle karega
try:
    from query_router import route_and_query
except ImportError:
    from retrieval.query_router import route_and_query

app = FastAPI(title="TechCorp Financial RAG API", version="1.0")

# Request Model
class QueryRequest(BaseModel):
    question: str

@app.post("/api/v1/query")
async def process_financial_query(request: QueryRequest):
    try:
        # Running your core flexible routing pipeline
        result = route_and_query(request.question)
        
        return {
            "status": "success",
            "type": result.get("type", "UNKNOWN"),
            "answer": result.get("answer", ""),
            "sql": result.get("sql", None),
            "citations": result.get("citations", None)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Clean running environment without multi-thread lockup
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)