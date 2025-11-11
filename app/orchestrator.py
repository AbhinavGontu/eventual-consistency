"""SAGA Orchestrator Module"""
import asyncio
from typing import List, Callable, Any, Optional
from pydantic import BaseModel

class StepResult(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None

class SagaStep:
    """
    Represents a single step in a distributed transaction.
    Must define an execute action and a compensate (undo) action.
    """
    def __init__(self, name: str):
        self.name = name

    async def execute(self, context: dict) -> StepResult:
        raise NotImplementedError

    async def compensate(self, context: dict) -> bool:
        raise NotImplementedError

class SagaOrchestrator:
    """
    Manages the lifecycle of a SAGA transaction.
    """
    def __init__(self):
        self.steps: List[SagaStep] = []
        self.completed_steps: List[SagaStep] = []
        self.context: dict = {}

    def add_step(self, step: SagaStep):
        self.steps.append(step)

    async def run(self, initial_payload: dict = {}) -> dict:
        self.context = initial_payload
        print(f"INFO: Starting SAGA with {len(self.steps)} steps.")

        for step in self.steps:
            print(f"Executing step: {step.name}...")
            try:
                result = await step.execute(self.context)
                
                if result.success:
                    self.completed_steps.append(step)
                    # Update context with result data if needed
                    if result.data:
                        self.context.update(result.data)
                    print(f"Step {step.name} SUCCEEDED.")
                else:
                    print(f"Step {step.name} FAILED: {result.error}")
                    await self.rollback()
                    return {"status": "FAILED", "error": result.error, "context": self.context}

            except Exception as e:
                print(f"Exception in step {step.name}: {str(e)}")
                await self.rollback()
                return {"status": "FAILED", "error": str(e), "context": self.context}

        return {"status": "SUCCESS", "context": self.context}

    async def rollback(self):
        """
        Executes compensating transactions in reverse order.
        """
        print("Initiating ROLLBACK...")
        # Iterate backwards
        for step in reversed(self.completed_steps):
            print(f"Compensating step: {step.name}...")
            success = await step.compensate(self.context)
            if success:
                print(f"Compensation for {step.name} SUCCEEDED.")
            else:
                # CRITICAL: Compensation failure requires manual intervention / dead letter queue
                print(f"CRITICAL: Compensation for {step.name} FAILED.")
        
        print("Rollback COMPLETE.")
