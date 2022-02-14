        print('Tamano CmdData_hex: %d' % len(CmdData_hex))

        if  int(len(CmdData_hex)/2) > CmdBodyLenght:
            sys.stderr.write("Cmd data no corresponde a la cantidad de bytes indicados en CmdBodyLenght\n")      
            sys.exit(2) 


        byte_pend = int (CmdBodyLenght - (len(CmdData_hex)/2))
        print('byte_pend: %s' % byte_pend)
        if byte_pend > 0:
            for i in range(byte_pend):
                CmdData_hex = CmdData_hex + '00'
        print('CmdData_hex: %s' % CmdData_hex) 