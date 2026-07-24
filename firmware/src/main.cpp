/*
 * Cypher ESP32 — Pure Motor Controller
 *
 * Receives commands over UART from the Raspberry Pi and drives the
 * TB6612FNG motors. Enforces a 1.5-second safety timeout.
 *
 * No WiFi, no web server, no OTA. All higher-level control lives on the Pi.
 *
 * Protocol: see docs/UART_PROTOCOL.md
 */

#include <Arduino.h>

// === UART Communication with Raspberry Pi ===
#define UART_BAUD 115200
unsigned long lastCommandTime = 0;
const unsigned long COMMAND_TIMEOUT = 1500; // 1.5 seconds safety timeout

String inputString = "";
bool stringComplete = false;

// === MOTOR PINS (TB6612FNG) ===
#define AIN1 25
#define AIN2 26
#define PWMA 27
#define BIN1 33
#define BIN2 32
#define PWMB 14

// === MOTOR STATE ===
int throttle = 0;     // -255 to 255
int steering = 0;     // -255 to 255
int steeringTrim = 0; // reserved for future mechanical trim

// === MOTOR CONTROL ===
void setTankMotors(int left, int right) {
  // Left motor
  if (left > 0) {
    digitalWrite(AIN1, HIGH);
    digitalWrite(AIN2, LOW);
  } else if (left < 0) {
    digitalWrite(AIN1, LOW);
    digitalWrite(AIN2, HIGH);
  } else {
    digitalWrite(AIN1, LOW);
    digitalWrite(AIN2, LOW);
  }
  analogWrite(PWMA, abs(left));

  // Right motor
  if (right > 0) {
    digitalWrite(BIN1, HIGH);
    digitalWrite(BIN2, LOW);
  } else if (right < 0) {
    digitalWrite(BIN1, LOW);
    digitalWrite(BIN2, HIGH);
  } else {
    digitalWrite(BIN1, LOW);
    digitalWrite(BIN2, LOW);
  }
  analogWrite(PWMB, abs(right));
}

void updateMotors() {
  int left  = throttle + steering + steeringTrim;
  int right = throttle - steering - steeringTrim;

  left  = constrain(left, -255, 255);
  right = constrain(right, -255, 255);

  setTankMotors(left, right);
}

// === UART Command Handler ===
void processCommand(String cmd) {
  cmd.trim();
  lastCommandTime = millis();

  if (cmd.startsWith("MOVE:")) {
    // Format: MOVE:throttle,steering
    int commaIndex = cmd.indexOf(',');
    if (commaIndex > 0) {
      throttle = cmd.substring(5, commaIndex).toInt();
      steering = cmd.substring(commaIndex + 1).toInt();
      updateMotors();
      Serial2.println("ACK:MOVE");
    }
  }
  else if (cmd == "STOP") {
    throttle = 0;
    steering = 0;
    updateMotors();
    Serial2.println("ACK:STOP");
  }
  else if (cmd == "HEARTBEAT") {
    Serial2.println("HEARTBEAT");
  }
  else if (cmd == "STATUS?") {
    String mode = "MANUAL";
    Serial2.printf("STATUS:%s,%d,%d\n", mode.c_str(), throttle, steering);
  }
  else if (cmd.length() > 0) {
    Serial2.println("ERR:UNKNOWN_CMD");
  }
}

void setup() {
  Serial.begin(115200);
  Serial2.begin(UART_BAUD);

  delay(200);
  Serial.println();
  Serial.println("=== Cypher ESP32 — Motor Controller ===");
  Serial.println("UART ready. Waiting for commands from Pi.");
  Serial.println("Safety timeout: 1500 ms");

  // Motor pins
  pinMode(AIN1, OUTPUT);
  pinMode(AIN2, OUTPUT);
  pinMode(PWMA, OUTPUT);
  pinMode(BIN1, OUTPUT);
  pinMode(BIN2, OUTPUT);
  pinMode(PWMB, OUTPUT);

  // Start stopped
  setTankMotors(0, 0);
  lastCommandTime = millis();   // prevent immediate timeout on boot
}

void loop() {
  // === Read commands from Raspberry Pi ===
  while (Serial2.available()) {
    char inChar = (char)Serial2.read();
    inputString += inChar;
    if (inChar == '\n') {
      stringComplete = true;
    }
  }

  if (stringComplete) {
    processCommand(inputString);
    inputString = "";
    stringComplete = false;
  }

  // === Safety Timeout ===
  if (millis() - lastCommandTime > COMMAND_TIMEOUT) {
    if (throttle != 0 || steering != 0) {
      throttle = 0;
      steering = 0;
      updateMotors();
      // Uncomment for debug visibility:
      // Serial.println("Safety stop triggered");
    }
  }

  delay(5);   // keep loop responsive without busy-waiting
}
