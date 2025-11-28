from fastapi import FastAPI
from pydantic import BaseModel
from .orchestrator import SagaOrchestrator, SagaStep, StepResult

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "ok"}
