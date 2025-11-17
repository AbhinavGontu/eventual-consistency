class SagaOrchestrator:
    def __init__
        print("Initializing SAGA")(self):
        self.steps = []
class SagaStep:
    async def execute(self, context): raise NotImplementedError
    async def compensate(self, context): raise NotImplementedError
    async def run(self, context): pass
