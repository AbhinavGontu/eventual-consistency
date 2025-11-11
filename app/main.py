from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .orchestrator import SagaOrchestrator, SagaStep, StepResult

app = FastAPI()

# --- Mock Steps ---

class InventoryStep(SagaStep):
    async def execute(self, context: dict) -> StepResult:
        item = context.get("item")
        if item == "out_of_stock_item":
            return StepResult(success=False, error="Item Out of Stock")
        print(f"[Inventory] Reserved {item}")
        return StepResult(success=True, data={"inventory_id": "inv_123"})

    async def compensate(self, context: dict) -> bool:
        print(f"[Inventory] Released reservation for {context.get('item')}")
        return True

class PaymentStep(SagaStep):
    async def execute(self, context: dict) -> StepResult:
        max_limit = 100
        amount = context.get("amount", 0)
        if amount > max_limit:
            return StepResult(success=False, error="Credit Limit Exceeded")
        print(f"[Payment] Charged ${amount}")
        return StepResult(success=True, data={"payment_id": "pay_987"})

    async def compensate(self, context: dict) -> bool:
        print(f"[Payment] Refunded ${context.get('amount')}")
        return True

class ShippingStep(SagaStep):
    async def execute(self, context: dict) -> StepResult:
        # Simulate logic
        print(f"[Shipping] Created shipment label")
        return StepResult(success=True, data={"tracking": "ups_123"})

    async def compensate(self, context: dict) -> bool:
        print(f"[Shipping] Cancelled shipment label")
        return True

# --- API ---

class OrderRequest(BaseModel):
    item: str
    amount: int

@app.post("/order")
async def create_order(order: OrderRequest):
    saga = SagaOrchestrator()
    
    # Define Workflow
    saga.add_step(InventoryStep("ReserveInventory"))
    saga.add_step(PaymentStep("ProcessPayment"))
    saga.add_step(ShippingStep("ArrangeShipping"))

    result = await saga.run(order.dict())
    
    if result["status"] == "FAILED":
        return result # Return failure details but 200 OK as request was handled
    
    return result
