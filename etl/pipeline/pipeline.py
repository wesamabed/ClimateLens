# etl/pipeline/pipeline.py
from typing import Any, List
from etl.pipeline.protocols import Step

class Pipeline:
    """
    Chains a sequence of Steps: Download → Transform → Load
    """
    def __init__(self, steps: List[Step[Any, Any]]):
        self.steps = steps

    def run(self) -> Any:
        data = None
        for step in self.steps:
            data = step.execute(data)
        return data
