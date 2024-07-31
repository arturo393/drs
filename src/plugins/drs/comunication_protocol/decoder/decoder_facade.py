from src.plugins.drs.comunication_protocol.decoder.ltel_decoder import LtelDecoder
from src.plugins.drs.comunication_protocol.decoder.santone_decoder import SantoneDecoder

class DecoderFacade:
    def __init__(self):
        self.decoders = {LtelDecoder, SantoneDecoder}

    def decode(self, command_number, command_body):
        fail = False
        for dec in self.decoders:
            try:
                return dec.decode(command_number, command_body)
            except AttributeError:
                fail = True
        
        if fail:
            raise AttributeError
