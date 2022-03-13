#!/usr/bin/env python




from operator import index
from unicodedata import decimal


C_HEADER = '7E'
C_MODULE_ADDRESS_ADDRESS = '00'
C_DATA_TYPE = '00'
C_RESPONSE_FLAG = '00'
C_END = '7E'


def s16(value):
    return -(value & 0x8000) | (value & 0x7fff)
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


print("prueba HEX")
# Convert integer to a binary value
int_value = 14
binary_value = str(bin(int_value))[2:]
print("binario: " + str(binary_value))


hexadecimal = "0B"
end_length = len(hexadecimal) * 2

hex_as_int = int(hexadecimal, 16)
hex_as_binary = bin(hex_as_int)
padded_binary = hex_as_binary[2:].zfill(8)
opt=1
temp = []
for bit in reversed(padded_binary):  
  if (bit=='0' and opt<=4):
     temp.append('Connected, ') 
  elif (bit=='1' and opt<=4):
      temp.append('Disconnected, ')
  elif (bit=='0' and opt>4):
    temp.append('Transsmision normal')
  elif (bit=='1' and opt>4):
    temp.append('Transsmision failure')
  opt=opt+1
print(temp)    
opt1 = "<br>OPT1: " + temp[0] + temp[4] 
opt2 = "<br>OPT2: " + temp[1] + temp[5]
opt3 = "<br>OPT2: " + temp[2] + temp[6]
opt4 = "<br>OPT2: " + temp[3] + temp[7] 
r = opt1 + opt2 + opt3 + opt4
print(r)

#hexadecimal = '6a990000'
#hexadecimal = '469a1a19'
#hexInvertido = hexadecimal[2:4] + hexadecimal[0:2]
#print("hexInvertido: " +  hexInvertido)
#hex_as_int = int(hexInvertido, 16)
#decSigned = s16(hex_as_int)
#print("s16: " + str(decSigned))

#rbm = decSigned / 256
#print("rbm: " + str(rbm))
#print("rbm redondeado: " + str(round(rbm,2)))


Result = 'b0274100862e410027294100a4294100212a41009e2a41001b2b4100982b4100152c4100922c41000f2d41008c2d4100092e4100862e4100032f4100802f4100|value=9225898788974403130110845956364562120997112066723351610997596041335379875634024178232190495388798004273667055590894356927412519834984712995268791695786240'
channel = 1
i = 0
tmp = ''
while channel <= 16:
    byte = Result[i:i+8]
    byteInvertido = byte[6:8] + byte[4:6] + byte[2:4] + byte[0:2] 
    print(byteInvertido)
    hex_as_int = int(byteInvertido, 16)
    print(hex_as_int)
    r = hex_as_int / 10000
    valor1 = '{:,.4f}'.format(r-10).replace(",", "@").replace(".", ",").replace("@", ".")
    valor2 = '{:,.4f}'.format(r).replace(",", "@").replace(".", ",").replace("@", ".")
    print(r)
    tmp += "<br> CH " + str(channel).zfill(3) + " - "+  valor1 + " MHz UL - " + valor2 + " MHz DL " 
    channel += 1
    i += 8
print(tmp)


Result = '0034'
byte01toInt = int(Result[0:2], 16)/4
byte02toInt = int(Result[2:4], 16)/4
print("Byte01: " + str(byte01toInt))
print("Byte02: " + str(byte02toInt))
valor1 = '{:,.2f}'.format(byte01toInt).replace(",", "@").replace(".", ",").replace("@", ".")
valor2 = '{:,.2f}'.format(byte02toInt).replace(",", "@").replace(".", ",").replace("@", ".")
print("Byte01: " + str(valor1))
print("Byte02: " + str(valor2))




hex= '01010101010101010101010101010101'
i = 0
result = ''
channel = 1
while channel <= 16:
    hex_as_int = int(hex[i:i+2], 16)
    if hex_as_int == 1:
        result += "<br> CH " + str(channel).zfill(2) + " ON\n"
    else:
        result += "<br> CH " + str(channel).zfill(2) + " OFF\n"
    i += 2
    channel += 1
    print(hex_as_int)
print(result)    



hex = "6666"
byte1 = hex[0:2]
byte2 = hex[2:4]

# Code to convert hex to binary
res1 = "{0:08b}".format(int(byte1, 16))
print(res1)

res2 = "{0:08b}".format(int(byte2, 16))
print(res2)
binario = res1 + res2
index = 0
for i,  in binario:
    index += 1
    if (i == '1' ):
        print('CH ' +  str(index) + ' ON') 
    else:
        print('CH ' + str(index) + ' OFF') 
