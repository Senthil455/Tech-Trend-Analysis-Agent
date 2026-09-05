from abc import ABC, abstractmethod

class Tool(ABC):
    """
    Abstract base class for all tools.
    """
    name: str
    description: str

    @abstractmethod
    def execute(self, **kwargs):
        """
        Execute the tool with the given arguments.
        """
        pass