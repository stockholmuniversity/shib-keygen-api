from abc import ABCMeta, abstractmethod
from dataclasses import dataclass


@dataclass
class PEM(metaclass=ABCMeta):
    private: str
    public: str


@dataclass
class CSR(metaclass=ABCMeta):
    common_name: str
    path: str


class Plugin(metaclass=ABCMeta):
    @classmethod
    @abstractmethod
    def export(cls, pem: PEM, csr: CSR) -> bool:
        pass

    @classmethod
    @abstractmethod
    def status(cls) -> bool:
        pass
