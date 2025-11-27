import asyncio
from typing import List, Callable, Any, Optional
from pydantic import BaseModel
from .models import StepResult

class SagaStep:
    def __init__(self, name: str):
        self.name = name
    async def execute(self, context: dict) -> StepResult: raise NotImplementedError
    async def compensate(self, context: dict) -> bool: raise NotImplementedError

class SagaOrchestrator:
    def __init__(self):
        self.steps: List[SagaStep] = []
        self.completed_steps: List[SagaStep] = []
    
    def add_step(self, step: SagaStep):
        self.steps.append(step)

    async def run(self, initial_payload: dict = {}) -> dict:
        self.context = initial_payload
        for step in self.steps:
            result = await step.execute(self.context)
            if result.success:
                self.completed_steps.append(step)
            else:
                await self.rollback()
                return {"status": "FAILED"}
        return {"status": "SUCCESS"}

    async def rollback(self):
        for step in reversed(self.completed_steps):
            await step.compensate(self.context)
