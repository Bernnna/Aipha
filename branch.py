import serial
import time

# ⚙️ Ajusta el puerto COM según tu Arduino
# (por ejemplo COM3 en Windows o /dev/ttyACM0 en Linux)
puerto = "COM8"
baudrate = 9600

# 📁 Archivo donde se guardarán los registros
archivo = "registro.txt"

try:
    with serial.Serial(puerto, baudrate, timeout=1) as arduino, open(archivo, "a") as f:
        print("Esperando datos del Arduino...")
        while True:
            linea = arduino.readline().decode("utf-8").strip()
            if linea:
                print("→", linea)
                f.write(linea + "\n")
                f.flush()
except serial.SerialException:
    print("❌ No se pudo conectar al puerto serial.")
except KeyboardInterrupt:
    print("\n✅ Finalizado por el usuario.")