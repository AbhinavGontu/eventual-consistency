import pytest
import asyncio
from app.orchestrator import SagaOrchestrator, SagaStep, StepResult

# --- Mocks ---
class MockStep(SagaStep):
    def __init__(self, name, should_fail=False):
        super().__init__(name)
        self.should_fail = should_fail
        self.executed = False
        self.compensated = False

    async def execute(self, context):
        self.executed = True
        if self.should_fail:
            return StepResult(success=False, error="Mock Failure Simulated")
        return StepResult(success=True)

    async def compensate(self, context):
        self.compensated = True
        return True

@pytest.mark.asyncio
async def test_full_success_flow():
    saga = SagaOrchestrator()
    step1 = MockStep("Step1")
    step2 = MockStep("Step2")
    
    saga.add_step(step1)
    saga.add_step(step2)
    
    result = await saga.run({})
    
    assert result["status"] == "SUCCESS"
    assert step1.executed
    assert step2.executed
    assert not step1.compensated
    assert not step2.compensated

@pytest.mark.asyncio
async def test_rollback_flow():
    saga = SagaOrchestrator()
    step1 = MockStep("Step1")
    step2 = MockStep("Step2", should_fail=True) # Fails
    step3 = MockStep("Step3") # Should not run
    
    saga.add_step(step1)
    saga.add_step(step2)
    saga.add_step(step3)
    
    result = await saga.run({})
    
    assert result["status"] == "FAILED"
    assert step1.executed
    assert step2.executed
    assert not step3.executed # Stopped early
    
    assert step1.compensated # Rolled back
    assert not step2.compensated # Failed step doesn't need compensation usually, or depends on implementation. Here logic is: only compensate COMPLETED steps.
