import pyvisa


class AFG1022:

    def __init__(self):

        self.rm = pyvisa.ResourceManager("@sim")
        #self.rm = pyvisa.ResourceManager("@py")

        self.inst = None

        self.connected = False

    ##############################################################

    def connect(self):
    
        resources = self.rm.list_resources()

        for r in resources:

            if not r.startswith("USB"):
                continue

            try:

                inst = self.rm.open_resource(r)
                inst.timeout = 5000

                idn = inst.query("*IDN?")

                #print(idn)

                if "AFG1022" in idn:

                    self.inst = inst
                    self.connected = True

                    # Forma de onda
                    self.waveform_ch1()
                    self.waveform_ch2()

                    # Unidad de amplitud
                    self.set_amplitude_unit_ch1("VPP")
                    self.set_amplitude_unit_ch2("VPP")

                    self.set_offset_ch1(0)
                    self.set_offset_ch2(0)

                    self.set_phase_ch1(0)
                    self.set_phase_ch2(0)

                    return True

                inst.close()

            except Exception as e:
                print("ERROR:", e)

        return False
        
    ##############################################################

    def disconnect(self):

        if self.inst is not None:

            self.inst.close()

        self.inst = None
        self.connected = False

        if self.rm is not None:
            self.rm.close()

    ##############################################################
    # IDENTIFICACIÓN
    ##############################################################

    def idn(self):

        return self.inst.query("*IDN?")
    
    ##############################################################

    def reset(self):

        self.inst.write("*RST")

    ##############################################################

    def set_frequency_ch1(self,f):

        self.inst.write(f"SOURCE1:FREQUENCY:FIXED {f}kHZ")

    ##############################################################

    def set_frequency_ch2(self,f):

        self.inst.write(f"SOURCE2:FREQUENCY:FIXED {f}kHZ")

    ##############################################################

    def get_frequency_ch1(self):

        return float(self.inst.query("SOURCE1:FREQUENCY:FIXED?"))
    
    ##############################################################

    def get_frequency_ch2(self):

        return float(self.inst.query("SOURCE2:FREQUENCY:FIXED?"))
    
    ##############################################################

    def set_amplitude_ch1(self,v):

        self.inst.write(f"SOURCE1:VOLTAGE:LEVEL:IMMEDIATE:AMPLITUDE {v}")

    ##############################################################

    def set_amplitude_ch2(self,v):

        self.inst.write(f"SOURCE2:VOLTAGE:LEVEL:IMMEDIATE:AMPLITUDE {v}")

    ##############################################################

    def get_amplitude_ch1(self):

        return float(self.inst.query("SOURCE1:VOLTAGE:LEVEL:IMMEDIATE:AMPLITUDE?"))
    
    ##############################################################

    def get_amplitude_ch2(self):

        return float(self.inst.query("SOURCE2:VOLTAGE:LEVEL:IMMEDIATE:AMPLITUDE?"))
    
    ##############################################################

    ##############################################################
    # UNIDAD DE AMPLITUD
    ##############################################################

    def set_amplitude_unit_ch1(self, unit):
        self.inst.write(f"SOURCE1:VOLTAGE:UNIT {unit}")


    def set_amplitude_unit_ch2(self, unit):
        self.inst.write(f"SOURCE2:VOLTAGE:UNIT {unit}")

    ##############################################################
    # OUTPUT CH1
    ##############################################################

    def output1(self,on):

        if on:

            self.inst.write("OUTPUT1:STATE ON")

        else:

            self.inst.write("OUTPUT1:STATE OFF")


    ##############################################################
    # OUTPUT CH2
    ##############################################################

    def output2(self,on):

        if on:

            self.inst.write("OUTPUT2:STATE ON")

        else:

            self.inst.write("OUTPUT2:STATE OFF")


    ##############################################################
    # FORMA DE ONDA CH1
    ##############################################################

    def waveform_ch1(self,name="SIN"):

        self.inst.write(f"SOURCE1:FUNCTION:SHAPE {name}")


    ##############################################################
    # FORMA DE ONDA CH2
    ##############################################################

    def waveform_ch2(self,name="SIN"):

        self.inst.write(f"SOURCE2:FUNCTION:SHAPE {name}")

    ##############################################################

    def set_offset_ch1(self, v):
        self.inst.write(f"SOURCE1:VOLTAGE:LEVEL:IMMEDIATE:OFFSET {v}")

    def set_offset_ch2(self, v):
        self.inst.write(f"SOURCE2:VOLTAGE:LEVEL:IMMEDIATE:OFFSET {v}")

    def set_phase_ch1(self, phase):
        self.inst.write(f"SOURCE1:PHASE:ADJUST {phase}")

    def set_phase_ch2(self, phase):
        self.inst.write(f"SOURCE2:PHASE:ADJUST {phase}")