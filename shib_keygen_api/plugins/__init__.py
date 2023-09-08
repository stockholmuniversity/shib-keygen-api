from abc import ABCMeta, abstractmethod


class Plugin(metaclass=ABCMeta):
    @classmethod
    @abstractmethod
    def export(cls) -> bool:
        pass

    @classmethod
    @abstractmethod
    def status(cls) -> bool:
        pass
