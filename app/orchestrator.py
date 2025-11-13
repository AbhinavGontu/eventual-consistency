class SagaOrchestrator:
    def __init__(self):
        self.steps = []
class SagaStep:
    async def execute(self, context): raise NotImplementedError
    async def compensate(self, context): raise NotImplementedError
