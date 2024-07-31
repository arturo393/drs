from src.plugins.drs.comunication_protocol.decoder.ltel_decoder import LtelDecoder
from src.plugins.drs.comunication_protocol.decoder.santone_decoder import SantoneDecoder


class DecoderFacade:
    @staticmethod
    def decode(command_number, command_body):
        decoders = {LtelDecoder, SantoneDecoder}
        fail = False
        for dec in decoders:
            try:
                return dec.decode(command_number, command_body)
            except AttributeError as e:
                fail = True
            except Exception as e:
                fail = True
        
        if fail:
            raise AttributeError
