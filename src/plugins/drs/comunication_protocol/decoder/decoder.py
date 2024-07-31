
class Decoder:

    def decode(self, command_number, command_body):
        """Decodes a command number."""
        try:
            return getattr(self, f"_decode_{command_number.name}")(command_body)
        except AttributeError:
            print(f" Command number {command_number} is not supported.")
            return {}
