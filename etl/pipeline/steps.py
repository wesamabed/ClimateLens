from abc import ABC, abstractmethod
from etl.config import ETLConfig

class ETLStep(ABC):
    """
    Strategy / Template:
    Each step implements `execute()`.
    """
    def __init__(self, config: ETLConfig):
        self.config = config

    @abstractmethod
    def execute(self) -> None:
        ...

class DownloadStep(ETLStep):
    def execute(self) -> None:
        # TODO: implement CSV download logic
        pass

class TransformStep(ETLStep):
    def execute(self) -> None:
        # TODO: implement CSV→JSON transforms
        pass

class LoadStep(ETLStep):
    def execute(self) -> None:
        # TODO: implement bulk-insert into MongoDB
        pass
