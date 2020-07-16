from abc import ABC, abstractmethod

class State(ABC):
    @abstractmethod
    def __init__(self, name, state_function = None):
        self.state_name = name
        self.state_function = state_function

