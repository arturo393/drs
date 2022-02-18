#!/usr/bin/env python




C_HEADER = '7E'
C_MODULE_ADDRESS_ADDRESS = '00'
C_DATA_TYPE = '00'
C_RESPONSE_FLAG = '00'
C_END = '7E'



#----------------------------------------------------
#-- Armar trama de escritura o lectura
    #------- PARAMETROS DE ENTRADA ------------------
    # Interface: ID de PA ó DSP, Ej. 0x07 => DSP , 0x08 => PA, En la trama MODULE_ADDRESS_FUNCTION
    # CmdNumber: 80 = Send ; 00 = Receive
    # CmdBodyLenght: Indentica si lee o escribe
    # CmdData: dato a escribir <integer en hex>
    # Crc: Bytes de control
#---------------------------------------------------
def get_plot(Interface, CmdNumber, CmdBodyLenght, CmdData, Crc):
    CmdNumber_hex = CmdNumber.encode('utf8').hex()
    CmdBodyLenght_hex = CmdBodyLenght.encode('utf8').hex()
    CmdData_hex = CmdData.encode('utf8').hex()
    Crc_hex = Crc.encode('utf8').hex()
    
    return C_HEADER + Interface + C_MODULE_ADDRESS_ADDRESS + C_DATA_TYPE + CmdNumber_hex + C_RESPONSE_FLAG + CmdBodyLenght_hex + CmdData_hex + Crc_hex + C_END



cont = bytes.fromhex('7E 08 00 00 4638 00 3032 4646 4232 3832 7E').decode('utf-8')
print(cont)

print("Imprimiendo cadena bytes")

tr = 'Hola undo'
cadena = "B2".encode('utf8')   #COnvertir un texto a una cadena de byte
cad_h = cadena.hex()         #Convierte una cadena de byte a hexadecimal 
print(cad_h)
#cadena_hex = ''
#for i in range(len(cadena)):
#	cadena_hex = cadena_hex  + str(hex(ord(cadena[i])))

#print(cadena_hex)


#print(b'484f4c41204d554e444f'.decode('utf8'))

cont = bytes.fromhex(cad_h).decode('utf-8')
print(cont)

cont = bytes.fromhex('4232').decode('utf-8')
print(cont)

print(hex(ord('~')))
