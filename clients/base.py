from abc import ABC, abstractmethod


class AsyncClientBase(ABC):

    def __init__(self, headers: dict) -> None:
        self.headers = headers

    @abstractmethod
    def get_api_response(self):
        raise NotImplementedError
