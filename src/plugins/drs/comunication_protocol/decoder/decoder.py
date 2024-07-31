
class Decoder:

    @classmethod
    def decode(cls, command_number, command_body):
        """Decodes a command number."""
        return getattr(cls, f"_decode_{command_number.name}")(command_body)
