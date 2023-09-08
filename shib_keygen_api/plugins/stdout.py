from shib_keygen_api.plugins import Plugin


class Stdout(Plugin):
    @classmethod
    def export(cls) -> bool:
        return False

    @classmethod
    def status(cls) -> bool:
        return True
