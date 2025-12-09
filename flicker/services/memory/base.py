from typing import Literal, Callable
from abc import ABC, abstractmethod


"""
Design of Memory System
=========================
Layer 0. Raw Information (Data Source)
Layer 1. Extracted Entities (e.g. Facts)
Layer 2. Relations (Knowledge Graphs)
"""


class AbstractDataChunk(ABC):
    @abstractmethod
    def getChunkId(self) -> str:
        ...

    @abstractmethod
    def getContent(self) -> str:
        ...


class AbstractDataSource(ABC):
    """ base class for all data sources """

    @abstractmethod
    def startUpdate(self, on_finished: Callable[[], None] | None = None):
        ...

    @abstractmethod
    def save(self) -> None:
        ...
