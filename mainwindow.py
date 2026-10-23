from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import pyqtgraph as pg
import os

from generator import AFG1022
from oscilloscope import TBS1202B
from measurement import MeasurementThread
import csv
import os
from datetime import datetime


class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("AM Lab")
        self.resize(1500,900)

        # Instrumentos

        self.generator = AFG1022()

        self.scope = TBS1202B()

        # Hilos

        self.measureThread = None


        self.create_widgets()

        self.create_layout()

        self.create_connections()

        self.actualizar_canales()

        self.lastX = None
        self.lastY = None

        self.saving = False
        self.csv_file = None
        self.csv_writer = None

    #################################################################

    def create_widgets(self):

        #########################
        # CONTROLES
        #########################

        self.gbControls=QGroupBox("Controles")

        self.lblModCH=QLabel("Canal de moduladora")

        self.lblFreq1=QLabel("Frecuencia CH1")
        self.lblAmp1=QLabel("Amplitud CH1")

        self.lblFreq2=QLabel("Frecuencia CH2")
        self.lblAmp2=QLabel("Amplitud CH2")

        self.cbModCH=QComboBox()
        self.cbModCH.addItems(["1","2"])

        self.sbFreq1=QSpinBox()
        self.sbFreq1.setRange(1,2500)
        self.sbFreq1.setValue(50)
        self.sbFreq1.setSuffix(" kHz")

        self.sbAmp1=QDoubleSpinBox()
        self.sbAmp1.setDecimals(1)
        self.sbAmp1.setRange(0.01,10)
        self.sbAmp1.setValue(1)
        self.sbAmp1.setSuffix(" Vpp")

        self.sbFreq2=QSpinBox()
        self.sbFreq2.setRange(1,2500)
        self.sbFreq2.setValue(400)
        self.sbFreq2.setSuffix(" kHz")

        self.sbAmp2=QDoubleSpinBox()
        self.sbAmp2.setDecimals(1)
        self.sbAmp2.setRange(0.01,10)
        self.sbAmp2.setValue(1)
        self.sbAmp2.setSuffix(" Vpp")

        self.btOutput1=QPushButton("Output CH1")

        self.btOutput1.setCheckable(True)

        self.btOutput2=QPushButton("Output CH2")

        self.btOutput2.setCheckable(True)

        self.cb_timebase = QComboBox()

        timebase_values = [
            ("2.5 ns/div", 2.5e-9),
            ("5 ns/div",   5e-9),
            ("10 ns/div",  10e-9),
            ("25 ns/div",  25e-9),
            ("50 ns/div",  50e-9),
            ("100 ns/div", 100e-9),
            ("250 ns/div", 250e-9),
            ("500 ns/div", 500e-9),

            ("1 us/div",   1e-6),
            ("2.5 us/div", 2.5e-6),
            ("5 us/div",   5e-6),
            ("10 us/div",  10e-6),
            ("25 us/div",  25e-6),
            ("50 us/div",  50e-6),
            ("100 us/div", 100e-6),
            ("250 us/div", 250e-6),
            ("500 us/div", 500e-6),

            ("1 ms/div",   1e-3),
            ("2.5 ms/div", 2.5e-3),
            ("5 ms/div",   5e-3),
            ("10 ms/div",  10e-3),
            ("25 ms/div",  25e-3),
            ("50 ms/div",  50e-3),
            ("100 ms/div", 100e-3),
            ("250 ms/div", 250e-3),
            ("500 ms/div", 500e-3),

            ("1 s/div",    1),
            ("2.5 s/div",  2.5),
            ("5 s/div",    5),
            ("10 s/div",   10),
            ("25 s/div",   25),
            ("50 s/div",   50)
        ]

        for text, value in timebase_values:
            self.cb_timebase.addItem(text, value)

        #########################
        # Resistencia de salida
        #########################

        self.resistencia_label = QLabel("Resistencia de carga:")
        self.resistencia_spinBox = QSpinBox()
        self.resistencia_spinBox.setRange(1, 1000000)
        self.resistencia_spinBox.setValue(560)
        self.resistencia_spinBox.setSuffix(" Ω")

        self.resistencia_layout = QHBoxLayout()
        self.resistencia_layout.addWidget(self.resistencia_label)
        self.resistencia_layout.addWidget(self.resistencia_spinBox)

        #########################
        # OSCILOSCOPIO
        #########################

        self.gbScope=QGroupBox("Señal temporal")

        self.plotWidget=pg.PlotWidget()

        self.plotWidget.setBackground("k")

        self.plotWidget.showGrid(True,True)

        self.plotWidget.setLabel("left","Voltaje","V")

        self.plotWidget.setLabel("bottom","Tiempo","s")

        self.wave=self.plotWidget.plot([],[],pen=pg.mkPen("lightgreen",width=2))

        #########################
        # FFT
        #########################
        self.gbSpectrum=QGroupBox("Espectro de frecuencias")
        self.spectrumWidget=pg.PlotWidget()
        self.spectrumWidget.setBackground("k")
        
        self.spectrumWidget.showGrid(True,True)

        self.spectrumWidget.setLabel("left","Magnitud","dBm")

        self.spectrumWidget.setLabel("bottom","Frecuencia","Hz")

        #self.spectrumWidget.setLogMode(x=True, y=False)

        self.spectrum=self.spectrumWidget.plot([],[],pen=pg.mkPen("lightgreen",width=2))


        #########################
        # MEDICIONES
        #########################

        self.gbMeasurements=QGroupBox("Mediciones")

        self.lblmTitle=QLabel("Modulación")

        self.lblVCarrierTitle=QLabel("Amplitud Carrier")

        self.lblVLSBTitle=QLabel("Amplitud LSB")

        self.lblVUSBTitle=QLabel("Amplitud USB")

        self.lblFCarrierTitle=QLabel("Frecuencia Carrier")
        
        self.lblFLSBTitle=QLabel("Frecuencia LSB")

        self.lblFUSBTitle=QLabel("Frecuencia USB")

        self.lblResolutionTitle=QLabel("Resolución (kHz)")

        self.lblm=QLabel("---")

        self.lblVCarrier=QLabel("---")

        self.lblVLSB=QLabel("---")

        self.lblVUSB=QLabel("---")

        self.lblFCarrier=QLabel("---")

        self.lblFLSB=QLabel("---")

        self.lblFUSB=QLabel("---")

        self.lblResolution=QLabel("---")


        font=QFont()

        font.setPointSize(14)

        font.setBold(True)

        self.lblm.setFont(font)

        self.lblVCarrier.setFont(font)

        self.lblVLSB.setFont(font)

        self.lblVUSB.setFont(font)

        self.lblFCarrier.setFont(font)
        
        self.lblFLSB.setFont(font)

        self.lblFUSB.setFont(font)

        self.lblResolution.setFont(font)


        #########################
        # BOTONES
        #########################

        self.btMeasure=QPushButton("Iniciar Medición")
        self.btMeasure.setCheckable(True)

        self.btcsv=QPushButton("Guardar medición")
        self.btcsv.setCheckable(True)

        #################################################################

    def create_layout(self):

        ###############################################################
        # GENERADOR
        ###############################################################

        ControlsLayout = QGridLayout()

        ControlsLayout.addWidget(self.lblModCH,0,0)
        ControlsLayout.addWidget(self.cbModCH,0,1)

        ControlsLayout.addWidget(self.lblFreq1,1,0)
        ControlsLayout.addWidget(self.sbFreq1,1,1)

        ControlsLayout.addWidget(self.lblAmp1,2,0)
        ControlsLayout.addWidget(self.sbAmp1,2,1)

        ControlsLayout.addWidget(self.btOutput1,3,0,1,2)

        ControlsLayout.addWidget(self.lblFreq2,4,0)
        ControlsLayout.addWidget(self.sbFreq2,4,1)

        ControlsLayout.addWidget(self.lblAmp2,5,0)
        ControlsLayout.addWidget(self.sbAmp2,5,1)

        ControlsLayout.addWidget(self.btOutput2,6,0,1,2)

        ControlsLayout.addWidget(QLabel("Time/Div:"),7,0)
        ControlsLayout.addWidget(self.cb_timebase,7,1)

        ControlsLayout.setColumnStretch(1,1)

        self.gbControls.setLayout(ControlsLayout)

        ###############################################################
        # MEDICIONES
        ###############################################################

        measurementLayout = QGridLayout()

        measurementLayout.addWidget(self.lblmTitle,0,0)
        measurementLayout.addWidget(self.lblm,0,1)

        measurementLayout.addWidget(self.lblVCarrierTitle,1,0)
        measurementLayout.addWidget(self.lblVCarrier,1,1)

        measurementLayout.addWidget(self.lblVLSBTitle,3,0)
        measurementLayout.addWidget(self.lblVLSB,3,1)

        measurementLayout.addWidget(self.lblVUSBTitle,4,0)
        measurementLayout.addWidget(self.lblVUSB,4,1)

        measurementLayout.addWidget(self.lblFCarrierTitle,5,0)
        measurementLayout.addWidget(self.lblFCarrier,5,1)

        measurementLayout.addWidget(self.lblFLSBTitle,6,0)
        measurementLayout.addWidget(self.lblFLSB,6,1)

        measurementLayout.addWidget(self.lblFUSBTitle,7,0)
        measurementLayout.addWidget(self.lblFUSB,7,1)

        measurementLayout.addWidget(self.lblResolutionTitle,8,0)
        measurementLayout.addWidget(self.lblResolution,8,1)

        measurementLayout.setColumnStretch(1,1)

        self.gbMeasurements.setLayout(measurementLayout)


        ###############################################################
        # PANEL IZQUIERDO
        ###############################################################

        leftLayout = QVBoxLayout()

        leftLayout.addWidget(self.gbControls)
        leftLayout.addLayout(self.resistencia_layout)
        leftLayout.addWidget(self.gbMeasurements)

        leftLayout.addStretch()

        leftLayout.addWidget(self.btMeasure)

        leftLayout.addWidget(self.btcsv)

        leftWidget = QWidget()
        leftWidget.setLayout(leftLayout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(leftWidget)

        ###############################################################
        # PANEL DERECHO
        ###############################################################

        rightLayout = QVBoxLayout()

        rightLayout.addWidget(self.gbScope)
        rightLayout.addWidget(self.gbSpectrum)

        self.gbScope.setLayout(QVBoxLayout())
        self.gbScope.layout().addWidget(self.plotWidget)

        self.gbSpectrum.setLayout(QVBoxLayout())
        self.gbSpectrum.layout().addWidget(self.spectrumWidget)

        rightWidget = QWidget()
        rightWidget.setLayout(rightLayout)

        ###############################################################
        # SPLITTERS
        ###############################################################
        splitter_graficos = QSplitter()
        splitter_graficos.setOrientation(Qt.Vertical)
        splitter_graficos.addWidget(self.gbScope)
        splitter_graficos.addWidget(self.gbSpectrum)
        splitter_graficos.setSizes([400,300])

        splitter = QSplitter()
        splitter.setOrientation(Qt.Horizontal)
        splitter.addWidget(scroll)
        splitter.addWidget(rightWidget)
        splitter.setSizes([350,1100])

        ###############################################################
        # CENTRAL
        ###############################################################
        rightLayout.addWidget(splitter_graficos)
        self.setCentralWidget(splitter)

        #################################################################

    def create_connections(self):

        ##########################################
        # ComboBox Canal de moduladora
        ##########################################

        self.cbModCH.currentIndexChanged.connect(self.actualizar_canales)

        ##########################################
        # SpinBox Canal 1
        ##########################################

        self.sbFreq1.valueChanged.connect(self.set_freq_ch1)
        self.sbAmp1.valueChanged.connect(self.set_amp_ch1)

        ##########################################
        # SpinBox Canal 2
        ##########################################

        self.sbFreq2.valueChanged.connect(self.set_freq_ch2)
        self.sbAmp2.valueChanged.connect(self.set_amp_ch2)

        ##########################################
        # ComboBox Timebase
        ##########################################
        self.cb_timebase.currentIndexChanged.connect(self.timebase_changed)
        ##########################################
        # Botones Output
        ##########################################

        self.btOutput1.clicked.connect(self.output1_clicked)
        self.btOutput2.clicked.connect(self.output2_clicked)

        ##########################################

        self.btMeasure.toggled.connect(self.measurement_toggled)

        self.btcsv.toggled.connect(self.toggle_saving)

        ##########################################

        self.create_menu()

        self.create_toolbar()

        #################################################################

    def create_menu(self):
    
        menuArchivo = self.menuBar().addMenu("Archivo")

        menuInstrumentos = self.menuBar().addMenu("Instrumentos")

        menuAyuda = self.menuBar().addMenu("Ayuda")

        ########################################

        self.actionSalir = QAction("Salir", self)

        self.actionConnectGenerator = QAction("Conectar Generador", self)

        self.actionConnectScope = QAction("Conectar Osciloscopio", self)

        self.actionAbout = QAction("Acerca de", self)

        self.actionAutoset = QAction("Autoset", self)

        ########################################

        menuArchivo.addAction(self.actionSalir)

        menuInstrumentos.addAction(self.actionConnectGenerator)

        menuInstrumentos.addAction(self.actionConnectScope)

        menuInstrumentos.addAction(self.actionAutoset)

        menuAyuda.addAction(self.actionAbout)

        ########################################

        self.actionSalir.triggered.connect(self.close)

        self.actionConnectGenerator.triggered.connect(self.connect_generator)

        self.actionConnectScope.triggered.connect(self.connect_scope)

        self.actionAbout.triggered.connect(self.show_about)

        self.actionAutoset.triggered.connect(self.scope.autoset)
        
        #################################################################
    
    def create_toolbar(self):

        tb = self.addToolBar("Principal")

        tb.setMovable(False)

        tb.addAction(self.actionConnectGenerator)

        tb.addAction(self.actionConnectScope)

        tb.addSeparator()

        tb.addAction(self.actionAutoset)

        tb.addAction(self.actionSalir)

        #################################################################

    def connect_generator(self):

        ok = self.generator.connect()

        if ok:
            self.status.showMessage("Generador conectado")
            self.set_amp_ch1(self.sbAmp1.value)
            self.set_amp_ch2(self.sbAmp2.value)
            self.set_freq_ch1(self.sbFreq1.value)
            self.set_freq_ch2(self.sbFreq2.value)
        else:
            QMessageBox.warning(self,"Error","No se encontró generador")

    #################################################################

    def connect_scope(self):

        ok = self.scope.connect()

        if ok:
            self.status.showMessage("Osciloscopio conectado")
        else:
            QMessageBox.warning(self,"Error","No se encontró osciloscopio")

    #################################################################

    def show_about(self):

        QMessageBox.information(self,"AM Lab","AM Lab\nControl SCPI de\ngenerador + osciloscopio")

    #################################################################

    def closeEvent(self, event):
        self.generator.disconnect()
        self.scope.disconnect()
        event.accept()

    #################################################################

    def set_freq_ch1(self, value):
        
        if self.generator.connected:
            self.generator.set_frequency_ch1(value)
        
        if self.cbModCH.currentText() == "1":
            self.fm = value
        else:
            self.fc = value

    #################################################################

    def set_amp_ch1(self, value):

        if self.generator.connected:
            self.generator.set_amplitude_ch1(value)

        if self.cbModCH.currentText() == "1":
            self.vm = value
        else:
            self.vc = value

    #################################################################

    def set_freq_ch2(self, value):

        if self.generator.connected:
            self.generator.set_frequency_ch2(value)
        
        if self.cbModCH.currentText() == "2":
            self.fm = value
        else:
            self.fc = value

    #################################################################

    def set_amp_ch2(self, value):

        if self.generator.connected:
            self.generator.set_amplitude_ch2(value)
        
        if self.cbModCH.currentText() == "2":
            self.vm = value
        else:
            self.vc = value

    #################################################################

    def output1_clicked(self):

        self.generator.output1(self.btOutput1.isChecked())

    #################################################################

    def output2_clicked(self):

        self.generator.output2(self.btOutput2.isChecked())

    #################################################################

    def actualizar_canales(self):

        if self.cbModCH.currentText() == "1":
            self.fm = self.sbFreq1.value()
            self.vm = self.sbAmp1.value()
            self.fc = self.sbFreq2.value()
            self.vc = self.sbAmp2.value()

        else:
            self.fc = self.sbFreq1.value()
            self.vc = self.sbAmp1.value()
            self.fm = self.sbFreq2.value()
            self.vm = self.sbAmp2.value()


    #################################################################
    def toggle_saving(self):

        if not self.saving:

            # -----------------------------
            # INICIAR ESCRITURA DE CSV
            # -----------------------------

            filename = datetime.now().strftime(
                "measurement_%Y%m%d_%H%M%S.csv"
            )

            filepath = os.path.join(
                "datos",
                filename
            )

            os.makedirs("datos", exist_ok=True)

            self.csv_file = open(
                filepath,
                "w",
                newline=""
            )

            self.csv_writer = None

            self.saving = True

            self.btcsv.setText("Detener guardado")

        else:

            # -----------------------------
            # DETENER GRABACIÓN
            # -----------------------------

            self.saving = False

            if self.csv_file is not None:
                self.csv_file.close()

            self.csv_file = None
            self.csv_writer = None

            self.btcsv.setText("Guardar medición")

    #################################################################

    def measurement_toggled(self, checked):
    
            if checked:
    
                self.btMeasure.setText("Detener medición")
                self.start_measurement()
    
            else:
    
                self.btMeasure.setText("Iniciar medición")
                if self.measureThread and self.measureThread.isRunning():
                    self.stop_measurement()

    def start_measurement(self):

        if not self.scope.connected:
            QMessageBox.warning(self,"Error","Conecte primero el osciloscopio.")
            self.btMeasure.setChecked(False)
            return
        
        self.measureThread = MeasurementThread(self.scope)
        self.measureThread.fc = self.fc
        self.measureThread.fm = self.fm
        self.measureThread.r = self.resistencia_spinBox.value()

        self.measureThread.waveformReady.connect(self.update_waveform)
        self.measureThread.spectrumReady.connect(self.update_spectrum)
        self.measureThread.measurementsReady.connect(self.update_measurements)
        self.measureThread.error.connect(self.show_error)
        self.measureThread.start()

    #################################################################

    def stop_measurement(self):

        if self.measureThread:
            self.measureThread.stop()
            self.measureThread.wait()


    #################################################################


    def update_waveform(self,x,y):

            if x is None:
                return

            self.lastX = x
            self.lastY = y

            self.wave.setData(x, y)

    def update_spectrum(self, frequency, magnitude):

        if frequency is None or magnitude is None:
            return

        self.lastSpectrumX = frequency
        self.lastSpectrumY = magnitude

        self.spectrum.setData(frequency, magnitude)


    def update_measurements(self,m):

        self.lblm.setText(f"{m['modulation_percent']:.2f} %")
        self.lblVCarrier.setText(f"{m['carrier_voltage']:.2f} V")
        self.lblVLSB.setText(f"{m['lsb_voltage']:.2f} V")
        self.lblVUSB.setText(f"{m['usb_voltage']:.2f} V")
        self.lblFCarrier.setText(f"{m['carrier_frequency']:.2f} Hz")
        self.lblFLSB.setText(f"{m['lsb_frequency']:.2f} Hz")
        self.lblFUSB.setText(f"{m['usb_frequency']:.2f} Hz")
        self.lblResolution.setText(f"{m['fft_resolution_hz']} Hz")

        if not self.saving:
            return

        # --------------------------------
        # Datos para guardar
        # --------------------------------

        row = m.copy()

        row["output_resistance_ohm"] = self.measureThread.r
        row["carrier_input_voltage"] = self.vc
        row["modulating_input_voltage"] = self.vm

        # --------------------------------
        # Crear escritor en la primera medición
        # --------------------------------

        if self.csv_writer is None:

            self.csv_writer = csv.DictWriter(
                self.csv_file,
                fieldnames=row.keys()
            )

            self.csv_writer.writeheader()

        # --------------------------------
        # Guardar medición
        # --------------------------------
        self.csv_writer.writerow(row)

        # Guardar inmediatamente
        self.csv_file.flush()


    def timebase_changed(self):
        
        value = self.cb_timebase.currentData()
        self.scope.set_time_scale(value)


    def show_error(self,msg):

        self.status.showMessage(msg)
