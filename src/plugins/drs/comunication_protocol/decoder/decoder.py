
class Decoder:

    @classmethod
    def decode(cls, command_number, command_body):
        """Decodes a command number."""
        try:
            return getattr(cls, f"_decode_{command_number.name}")(command_body)
        except AttributeError:
            print(f" Command number {command_number} is not supported.")
            return {}
