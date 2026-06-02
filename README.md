# Raspberry Pi Camera App

Aplicación de cámara para Raspberry Pi con grabación de video y streaming web en tiempo real.

## Características

- Streaming de video en vivo desde el navegador
- Grabación de video en formato H264/MP4
- Captura de fotos
- Interfaz web responsive
- Control completo desde el navegador

## Requisitos

- Raspberry Pi (3, 4 o 5)
- Módulo de cámara oficial (Camera Module v2 o v3)
- Raspberry Pi OS (Bullseye o Bookworm)
- Python 3.9+

## Instalación

```bash
# Clonar el repositorio
git clone https://github.com/rafachem9/raspberrypi-camera.git
cd raspberrypi-camera

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la aplicación
python app.py
```

Luego abre el navegador en: `http://<ip-de-tu-raspberry>:5000`

## Habilitar la cámara

```bash
sudo raspi-config
# Interface Options > Camera > Enable
```

## Estructura

```
├── app.py              # Servidor Flask principal
├── camera.py           # Módulo de control de cámara
├── requirements.txt    # Dependencias Python
├── templates/
│   └── index.html      # Interfaz web
└── recordings/         # Videos y fotos guardados
```
