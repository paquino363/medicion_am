import pyvisa
import numpy as np
from PyQt5.QtCore import QMutex


class TBS1202B:

    def __init__(self):

        self.rm = pyvisa.ResourceManager("@sim")
        #self.rm = pyvisa.ResourceManager("@py")

        self.visa_mutex = QMutex(QMutex.Recursive)

        self.inst = None

        self.connected = False

        #########################################################

    def connect(self):

        resources = self.rm.list_resources()

        for r in resources:

            # Solo probar USB
            if not r.startswith("USB"):
                continue

            try:
                inst = self.rm.open_resource(r)

                inst.timeout = 5000

                idn = inst.query("*IDN?")

                print(idn)

                if "TBS 1202B" in idn or "TBS2102B" in idn or "TBS1102C" in idn:

                    self.inst = inst
                    self.connected = True
                    self.prepare_waveform()

                    return True

                inst.close()

            except Exception as e:

                print("ERROR USB:", e)

        return False
    
        #########################################################

    def disconnect(self):

        if self.inst is not None:

            self.inst.close()

        self.inst = None
        self.connected = False

        if self.rm is not None:
            self.rm.close()

        #########################################################

    def idn(self):

        return self.inst.query("*IDN?")
    
        #########################################################

    def reset(self):

        self.inst.write("*RST")

        #########################################################

    def channel(self,ch):

        self.inst.write(f"DATA:SOURCE CH{ch}")

        #########################################################

    def prepare_waveform(self, ch=1):

        self.channel(ch)
        self.inst.write("DATA:ENC RPB")
        self.inst.write("DATA:WIDTH 1")
        self.inst.write("DATA:START 1")
        self.inst.write("DATA:STOP 2500")



        #########################################################
    # Obtiene los parámetros de calibración necesarios para interpretar correctamente los datos binarios de la forma de onda que
    # devuelve el comando CURVE? (secuencia de números enteros, por ejemplo, bytes de 0 a 255)
    # Si el osciloscopio devuelve un punto de datos "raw", el voltaje real se calcula como: voltaje = (raw - YOFF) × YMULT + YZERO
    # Y el tiempo de la muestra número i es: tiempo = i × XINCR
    def read_preamble(self):
        #Lee el factor de escala vertical [V/nivel (voltios por nivel de digitalización)].
        ymult = float(self.inst.query("WFMPRE:YMULT?"))
        #Lee el nivel de referencia en voltios V.
        yzero = float(self.inst.query("WFMPRE:YZERO?"))
        #Lee el desplazamiento vertical de los datos (nivel).
        yoff = float(self.inst.query("WFMPRE:YOFF?"))
        #Lee el tiempo entre dos muestras consecutivas. 1/xincr es la frecuencia de muestreo.
        xincr = float(self.inst.query("WFMPRE:XINCR?"))

        return ymult,yzero,yoff,xincr
    
        #########################################################

    def read_waveform(self):

        if not self.connected:
            return None, None

        self.visa_mutex.lock()

        try:

            ######################################################
            # Leer parámetros de escalado
            ######################################################

            ymult, yzero, yoff, xincr = self.read_preamble()

            ######################################################
            # Leer datos binarios
            ######################################################

            raw = self.inst.query_binary_values("CURVE?",datatype='B',container=np.array)

            ######################################################
            # Convertir a Voltios
            ######################################################

            y = (raw - yoff) * ymult + yzero

            ######################################################
            # Vector tiempo
            ######################################################

            x = np.arange(len(y)) * xincr

            return x, y

        finally:
            self.visa_mutex.unlock()

        #########################################################

    def measure_frequency(self):

        self.inst.write("MEASU:IMM:TYP FREQ")

        return float(self.inst.query("MEASU:IMM:VAL?"))

        #########################################################

    def measure_rms(self):

        self.inst.write("MEASU:IMM:TYP RMS")

        return float(self.inst.query("MEASU:IMM:VAL?"))
        
    
        #########################################################

    def read_measurements(self):

        data = {}

        data["frequency"] = self.measure_frequency()

        data["vmax"] = self.measure_vmax()

        data["vmin"] = self.measure_vmin()

        return data
    

    def get_time_scale(self):

        return float(self.inst.query("HORIZONTAL:SCALE?"))
    

    def set_time_scale(self, time_per_div):

        self.visa_mutex.lock()
        
        try:
            self.inst.write(f":HORizontal:MAIn:SCAle {time_per_div}")
        finally:
            self.visa_mutex.unlock()
        

    def get_voltage_scale(self, channel=1):

        return float(self.inst.query(f"CH{channel}:SCALE?"))


    def get_sample_interval(self):

        return float(self.inst.query("WFMPRE:XINCR?"))


    def autoset(self):

        self.visa_mutex.lock()

        try:
            self.inst.write("AUTOSET EXECUTE")
        finally:
            self.visa_mutex.unlock()


    def measure_am_fft(self, fc, fm, x, y, r):

        fc = fc * 1000
        fm = fm * 1000

        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float)

        # --------------------------------
        # Tiempo de muestreo
        # --------------------------------

        dt = np.mean(np.diff(x))

        if dt <= 0:
            raise RuntimeError("Vector de tiempo inválido.")

        fs = 1 / dt
        N = len(y)

        # --------------------------------
        # Quitar componente DC
        # --------------------------------

        y = y - np.mean(y)

        # --------------------------------
        # Ventana Hann
        # --------------------------------

        window = np.hanning(N)

        # Corrección de amplitud de la ventana
        coherent_gain = np.sum(window) / N

        y_windowed = y * window

        # --------------------------------
        # FFT
        # --------------------------------

        spectrum = np.fft.rfft(y_windowed)

        frequency = np.fft.rfftfreq(N, d=dt)

        magnitude = (
            2 * np.abs(spectrum)
            / (N * coherent_gain)
        )

        magnitude[0] /= 2

        # --------------------------------
        # RECORTAR FFT PARA EL GRÁFICO
        # --------------------------------

        f_min = fc - 3 * fm
        f_max = fc + 3 * fm

        mask_plot = (
            (frequency >= f_min) &
            (frequency <= f_max)
        )

        frequency = frequency[mask_plot]
        magnitude = magnitude[mask_plot]


        # --------------------------------
        # Resolución FFT
        # --------------------------------

        df = fs / N

        # --------------------------------
        # Frecuencias teóricas AM
        # --------------------------------

        f_lsb = fc - fm
        f_usb = fc + fm

        # --------------------------------
        # Buscar pico alrededor
        # de una frecuencia
        # --------------------------------

        def find_peak(target):

            # Ventana de búsqueda
            search_width = max(
                3 * df,
                fm * 0.15
            )

            mask = (
                (frequency >= target - search_width)
                &
                (frequency <= target + search_width)
            )

            indices = np.where(mask)[0]

            if len(indices) == 0:
                raise RuntimeError(
                    f"No se encontró la frecuencia {target} Hz."
                )

            index = indices[
                np.argmax(magnitude[indices])
            ]

            return (
                magnitude[index], frequency[index]
            )

        # --------------------------------
        # Buscar LSB / Carrier / USB
        # --------------------------------

        v_lsb, f_lsb = find_peak(f_lsb)

        v_carrier, f_carrier = find_peak(
            fc
        )

        v_usb, f_usb = find_peak(f_usb)

        # --------------------------------
        # Conversion a dBm
        # --------------------------------

        #magnitude_db = 20 * np.log10(magnitude / v_carrier)
        power_w = (magnitude ** 2) / (2 * r)
        power_dbm = 10 * np.log10(power_w / 1e-3)

        # --------------------------------
        # Índice de modulación
        # --------------------------------

        m = (v_lsb + v_usb) / v_carrier

        # --------------------------------
        # Potencias
        # --------------------------------

        p_lsb = (v_lsb ** 2) / (2 * r)
        p_carrier = (v_carrier ** 2) / (2 * r)
        p_usb = (v_usb ** 2) / (2 * r)
        p_total = p_carrier + p_lsb + p_usb

        p_lsb_dbm = 10 * np.log10(p_lsb / 1e-3)
        p_carrier_dbm = 10 * np.log10(p_carrier / 1e-3)
        p_usb_dbm = 10 * np.log10(p_usb / 1e-3)
        p_total_dbm = 10 * np.log10(p_total / 1e-3)

        # --------------------------------
        # Ancho de banda
        # --------------------------------

        bandwidth = f_usb - f_lsb

        # --------------------------------
        # Desbalance entre bandas laterales
        # --------------------------------

        sideband_imbalance = abs(
            20 * np.log10(v_usb / v_lsb)
        )

        # --------------------------------
        # Resultado
        # --------------------------------

        measurements = {

            "lsb_voltage": v_lsb,
            "carrier_voltage": v_carrier,
            "usb_voltage": v_usb,

            "lsb_frequency": f_lsb,
            "carrier_frequency": f_carrier,
            "usb_frequency": f_usb,

            "modulation_index": m,
            "modulation_percent": m * 100,

            "lsb_power_w": p_lsb,
            "carrier_power_w": p_carrier,
            "usb_power_w": p_usb,
            "total_power_w": p_total,

            "lsb_power_dbm": p_lsb_dbm,
            "carrier_power_dbm": p_carrier_dbm,
            "usb_power_dbm": p_usb_dbm,
            "total_power_dbm": p_total_dbm,

            "bandwidth": bandwidth,
            "sideband_imbalance": sideband_imbalance,

            "fft_resolution_hz": df,
            "sample_rate_hz": fs
        }

        fft = {
            
            "frequency": frequency,
            "magnitude": power_dbm
        }

        return measurements, fft