from ultralytics import YOLO
import cv2
import time
import serial
from datetime import datetime
import requests
import csv
import os


arduino = serial.Serial('COM8', 9600, timeout=1)
time.sleep(2)
print("Conectado al Arduino UNO en COM8.")


model = YOLO("yolo11n.pt")


cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FPS, 30)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1080)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

if not cap.isOpened():
    print("No se pudo acceder a la cámara.")
    exit()

print("Cámara lista. Presioná 'q' para salir.")


target_fps = 30
frame_time = 1 / target_fps
phone_detected_prev = False
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))


csv_path = os.path.join(os.getcwd(), "registro.csv")
if not os.path.exists(csv_path):
    with open(csv_path, mode="w", newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Fecha y Hora", "Ubicación", "Evento", "Ángulo"])
    print(f"Archivo CSV creado en: {csv_path}")
else:
    print(f"Registrando en CSV existente: {csv_path}")


while True:
    start = time.time()
    ret, frame = cap.read()
    if not ret:
        break

    
    results = model(frame, conf=0.5)
    annotated = results[0].plot()

    detected_phone = False
    angulo = 90

    for box in results[0].boxes:
        cls = int(box.cls[0])
        if cls == 67:  
            detected_phone = True

            x1, y1, x2, y2 = box.xyxy[0]
            x_center = (x1 + x2) / 2
            angulo = int((x_center / frame_width) * 180)
            angulo = max(0, min(180, angulo))
            break


    if detected_phone and not phone_detected_prev:
        print(f"Celular detectado (ángulo {angulo}°) → enviando al Arduino...")
        cmd = f"ANGLE:{angulo}\n".encode()
        arduino.write(cmd)
        phone_detected_prev = True

    elif not detected_phone and phone_detected_prev:
        print("Celular ya no detectado → limpiando LCD...")
        arduino.write(b"NO_PHONE\n")
        phone_detected_prev = False

    
    if arduino.in_waiting > 0:
        try:
            line = arduino.readline().decode(errors="ignore").strip()
            if line:
                print("Recibido del Arduino:", line)

                if line.startswith("BOTON:"):
                    hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    
                    try:
                        response = requests.get("https://ipinfo.io/json", timeout=5)
                        data = response.json()
                        lugar = data.get("country", "Desconocido")
                        if lugar == "AR":  
                            lugar = "Argentina"
                        elif not lugar:
                            lugar = "Desconocido"
                    except Exception as e:
                        print("No se pudo obtener la ubicación:", e)
                        lugar = "Desconocido"

                    
                    with open(csv_path, mode="a", newline='', encoding="utf-8") as file:
                        writer = csv.writer(file)
                        writer.writerow([hora, lugar, line, angulo])

                    print(f"Guardado en CSV: {hora} | {lugar} | {line} | {angulo}°")
        except Exception as e:
            print("Error al leer el puerto serial:", e)

    
    cv2.imshow("Detección YOLO", annotated)

    
    elapsed = time.time() - start
    delay = max(0, frame_time - elapsed)
    time.sleep(delay)

    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
arduino.close()
cv2.destroyAllWindows()
print("Programa finalizado.")
