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

    # https://docs.python.org/3.11/library/pathlib.html#operators
    # Apparently it's a feature that Path() from pathlib ignores previous
    # path when merging to paths and the latter "is absolute" i.e. has a /
    # first. This is not a great place to fix it, but an easy one.
    def __post_init__(self) -> None:
        self.path = self.path.lstrip("/")


class Plugin(metaclass=ABCMeta):
    @classmethod
    @abstractmethod
    def export(cls, pem: PEM, csr: CSR) -> bool:
        pass

    @classmethod
    @abstractmethod
    def status(cls) -> bool:
        pass
