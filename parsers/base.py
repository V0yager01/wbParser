from abc import ABC, abstractmethod


class ParserBase(ABC):
    @abstractmethod
    def parse(self):
        raise NotImplementedError
