from PyQt5.QtCore import *
import time


class MeasurementThread(QThread):

    waveformReady = pyqtSignal(object, object)

    spectrumReady = pyqtSignal(object, object)

    measurementsReady = pyqtSignal(dict)

    error = pyqtSignal(str)

    connected = pyqtSignal()

    disconnected = pyqtSignal()

    def __init__(self, scope):

        super().__init__()

        self.scope = scope

        self.fc = 400

        self.fm = 40

        self.r = 560

        self.running = False

    ########################################################

    def stop(self):

        self.running = False

    ########################################################

    def run(self):

        self.running = True

        while self.running:

            try:

                x, y = self.scope.read_waveform()

                if x is None or y is None:
                    time.sleep(0.5)
                    continue

                self.waveformReady.emit(x, y)

                measurement, fft = self.scope.measure_am_fft(self.fc, self.fm, x, y, self.r)

                self.measurementsReady.emit(measurement)

                self.spectrumReady.emit(fft['frequency'], fft['magnitude'])

            except Exception as e:

                self.error.emit(str(e))

            time.sleep(0.5)