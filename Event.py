from abc import ABC, abstractmethod
from enum import Enum
import datetime
import uuid

class Event(ABC):
    @abstractmethod
    def __init__(self, event_type : Enum):
        self.event_id = uuid.uuid4()
        self.event_type = event_type
        self.creation_timestamp = datetime.datetime.now().timestamp()
