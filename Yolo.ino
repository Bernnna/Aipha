#include <Servo.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

Servo servo;
LiquidCrystal_I2C lcd(0x27, 16, 2);  // Cambia la dirección si es necesario (usa un escáner I2C)
int servoPin = 7;
int ledPin = 8;
int bSi = 2;
int bNo = 3;

void setup() {
  Serial.begin(9600);
  servo.attach(servoPin);
  pinMode(ledPin, OUTPUT);
  pinMode(bSi, INPUT_PULLUP);
  pinMode(bNo, INPUT_PULLUP);
  lcd.init();
  lcd.backlight();

  lcd.print("Esperando...");
}

void loop() {
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    if (cmd.startsWith("ANGLE:")) {
      int ang = cmd.substring(6).toInt();
      ang = constrain(ang, 0, 180);

      servo.write(ang);
      delay(1000);
      digitalWrite(ledPin, HIGH);

      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Celular detectado");
      lcd.setCursor(0, 1);
      lcd.print("Proseguir?");

      bool responded = false;
      while (!responded) {
        if (digitalRead(bSi) == LOW) {
          Serial.println("BOTON: SI");
          lcd.clear();
          lcd.print("Continuando...");
          delay(500);
          digitalWrite(ledPin, LOW);
          lcd.clear();
          lcd.print("Esperando...");
          responded = true;
        }
        if (digitalRead(bNo) == LOW) {
          Serial.println("BOTON: No");
          lcd.clear();
          lcd.print("Continuando...");
          delay(500);
          digitalWrite(ledPin, LOW);
          lcd.clear();
          lcd.print("Esperando...");
          responded = true;
        }
      }
    }

    else if (cmd == "NO_PHONE") {
      digitalWrite(ledPin, LOW);
      servo.write(0);
      lcd.clear();
      lcd.print("Esperando...");
    }
  }
}

