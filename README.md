# AM Lab

Aplicación de escritorio desarrollada en **Python** para el control de instrumentos electrónicos mediante SCPI y el análisis de señales de **modulación de amplitud (AM)**.

El programa permite controlar un generador de funciones Tektronix AFG1022 y adquirir señales desde un osciloscopio Tektronix TBS1202B. A partir de las muestras adquiridas, realiza un análisis espectral mediante la Transformada Rápida de Fourier (FFT) para obtener los principales parámetros de la señal AM.

## Características

### Control del generador de funciones

- Conexión con el generador Tektronix AFG1022 mediante USB.
- Configuración independiente de frecuencia y amplitud para los dos canales.
- Selección de la señal moduladora entre CH1 y CH2.
- Configuración de la forma de onda senoidal.
- Control individual de las salidas de ambos canales.
- Configuración de amplitud en Vpp.

### Adquisición con el osciloscopio

- Conexión con el osciloscopio Tektronix TBS1202B mediante USB.
- Adquisición de la forma de onda.
- Conversión de las muestras digitales a valores de tensión y tiempo utilizando los parámetros de escala del osciloscopio.
- Configuración de la base de tiempos.
- Función Autoset.

### Análisis espectral de señales AM

El programa procesa las muestras adquiridas utilizando NumPy y aplica una ventana Hann antes de calcular la FFT.

A partir del espectro identifica la portadora y las bandas laterales:

- Portadora (Carrier).
- Banda lateral inferior (LSB).
- Banda lateral superior (USB).

Calcula los siguientes parámetros:

- Amplitud de la portadora y de las bandas laterales.
- Frecuencia de la portadora y de las bandas laterales.
- Índice de modulación.
- Porcentaje de modulación.
- Potencia de cada componente.
- Potencia total de las componentes identificadas.
- Potencias expresadas en dBm.
- Ancho de banda.
- Desbalance entre bandas laterales.
- Resolución frecuencial de la FFT.
- Frecuencia de muestreo.

### Registro de mediciones

- Visualización en tiempo real de la señal temporal.
- Visualización del espectro de frecuencias.
- Visualización de los parámetros calculados.
- Registro de mediciones en archivos CSV.
- Almacenamiento de parámetros de configuración asociados a cada medición.

## Interfaz gráfica

La interfaz está desarrollada con PyQt5 y utiliza PyQtGraph para representar las señales.

La ventana principal se organiza en tres sectores:

1. **Controles:** configuración del generador, canales, amplitudes, frecuencias y base de tiempos.
2. **Mediciones:** visualización de los parámetros obtenidos del análisis AM.
3. **Gráficos:** representación de la señal temporal y del espectro de frecuencias.

## Instrumentación

El proyecto está diseñado para trabajar con los siguientes instrumentos:

| Instrumento | Modelo | Función |
|---|---|---|
| Generador de funciones | Tektronix AFG1022 | Generación de portadora y señal moduladora |
| Osciloscopio digital | Tektronix TBS1202B | Adquisición de la señal AM |

La comunicación con los instrumentos se realiza mediante USB utilizando PyVISA y el backend PyVISA-py.

## Tecnologías utilizadas

- **Python:** lenguaje principal.
- **PyQt5:** desarrollo de la interfaz gráfica.
- **PyQtGraph:** visualización de señales.
- **NumPy:** procesamiento numérico y cálculo de FFT.
- **PyVISA:** comunicación con instrumentos de medición.
- **PyVISA-py:** backend de comunicación VISA.
- **PyUSB:** soporte para comunicación USB.

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/paquino363/medicion_am.git
cd medicion_am
```

### 2. Crear un entorno virtual (opcional)

```bash
python -m venv venv
```

Activarlo en Windows:

```bash
venv\Scripts\activate
```

Activarlo en Linux:

```bash
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install PyQt5 pyqtgraph numpy pyvisa pyvisa-py pyusb
```

## Ejecución

Desde la carpeta del proyecto, ejecutar:

```bash
python main.py
```

Una vez iniciada la aplicación:

1. Conectar el generador AFG1022 y el osciloscopio TBS1202B al equipo mediante USB.
2. Seleccionar **Conectar Generador** desde la barra de herramientas.
3. Seleccionar **Conectar Osciloscopio**.
4. Configurar las frecuencias y amplitudes de ambos canales.
5. Seleccionar el canal que se utilizará como señal moduladora.
6. Conectar físicamente las señales según el montaje experimental.
7. Iniciar la medición.
8. Activar el registro CSV si se desea guardar los resultados.

Los archivos CSV se almacenan automáticamente dentro de la carpeta `datos`.

## Estructura del proyecto

```text
medicion_am/
│
├── main.py
├── mainwindow.py
├── generator.py
├── oscilloscope.py
└── measurement.py
```

| Archivo | Descripción |
|---|---|
| `main.py` | Punto de entrada de la aplicación. Inicializa Qt y muestra la ventana principal. |
| `mainwindow.py` | Implementa la interfaz gráfica, los controles y la interacción con los instrumentos. |
| `generator.py` | Contiene la clase `AFG1022` para controlar el generador mediante SCPI. |
| `oscilloscope.py` | Contiene la clase `TBS1202B`, gestiona la adquisición de señales y realiza el análisis FFT. |
| `measurement.py` | Implementa el hilo de adquisición periódica y comunica los resultados con la interfaz mediante señales Qt. |

## Formato de los datos

Las mediciones se exportan en formato CSV. Entre los parámetros registrados se encuentran:

- Tensiones de portadora y bandas laterales.
- Frecuencias identificadas.
- Índice y porcentaje de modulación.
- Potencias en W y dBm.
- Ancho de banda.
- Desbalance entre bandas laterales.
- Resolución de FFT y frecuencia de muestreo.
- Resistencia de salida configurada.
- Amplitudes de entrada de portadora y moduladora.

## Consideraciones

- Es necesario disponer de los instrumentos compatibles y conectarlos mediante USB.
- La detección de instrumentos depende de la disponibilidad del backend VISA y de los permisos de acceso al dispositivo.
- La conexión física y la configuración de los instrumentos deben ser adecuadas para el montaje experimental.
- Las potencias calculadas se obtienen a partir de las amplitudes espectrales y de la resistencia de carga configurada.
