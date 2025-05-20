
class DummyStep:
    def __init__(self,x): self.x=x
    def execute(self,data): return self.x

def test_pipeline_order():
    from etl.pipeline.pipeline import Pipeline
    p = Pipeline([DummyStep(1), DummyStep(2), DummyStep(3)])
    assert p.run() == 3

def test_load_step_logs(caplog):
    import logging
    from etl.pipeline.load_step import LoadStep
    # Dummy loader that records calls
    class L:
        def __init__(self): self.called=False
        def load(self, recs): self.called=True
    loader = L()
    logger = logging.getLogger("test_load_step")
    logger.setLevel(logging.INFO)
    step = LoadStep(None, loader, logger)
    step.execute([{"a":1}])
    assert loader.called
    assert "Loading 1 records" in caplog.text
