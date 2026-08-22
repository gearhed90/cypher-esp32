/*
 * Cypher ESP32 — Motors + Pan/Tilt
 *
 * UART from Pi: motors + head.
 * Servos: hardware PWM, rate-limited, NVS-taught boot pose.
 * Motor safety timeout 1.5 s (servos not timed out).
 */

#include <Arduino.h>
#include <ESP32Servo.h>
#include <Preferences.h>

// === UART (must match Pi wiring) ===
#define UART_BAUD 115200
// Serial2: RX=19, TX=18  (Pi GPIO 8 TX -> 19, Pi GPIO 10 RX <- 18)

unsigned long lastCommandTime = 0;
const unsigned long COMMAND_TIMEOUT = 1500;

String inputString = "";
bool stringComplete = false;

// === MOTOR PINS (TB6612FNG) ===
#define AIN1 25
#define AIN2 26
#define PWMA 27
#define BIN1 33
#define BIN2 32
#define PWMB 14

// === SERVO PINS ===
#define PAN_PIN  13
#define TILT_PIN 12

// === SERVO LIMITS ===
const float PAN_MIN  = -45.0f;
const float PAN_MAX  =  45.0f;
const float TILT_MIN =  -9.0f;
const float TILT_MAX =   9.0f;

// Default boot if nothing saved in NVS
const float DEFAULT_BOOT_PAN  = 0.0f;
const float DEFAULT_BOOT_TILT = 0.0f;

// Sleep pose
const float SLEEP_PAN  =  0.0f;
const float SLEEP_TILT = -9.0f;

// Invert axes (dashboard controls were reversed)
const bool INVERT_PAN  = true;
const bool INVERT_TILT = true;

// Speed deg/s
const float SERVO_SPEED = 28.0f;

// === MOTOR STATE ===
int throttle = 0;
int steering = 0;
int steeringTrim = 0;

// === SERVO STATE ===
Servo panServo;
Servo tiltServo;
Preferences prefs;

float panCurrent  = 0.0f;
float tiltCurrent = 0.0f;
float panTarget   = 0.0f;
float tiltTarget  = 0.0f;
float bootPan     = DEFAULT_BOOT_PAN;
float bootTilt    = DEFAULT_BOOT_TILT;
unsigned long lastServoUpdate = 0;

float clamp(float v, float lo, float hi) {
  if (v < lo) return lo;
  if (v > hi) return hi;
  return v;
}

void setTankMotors(int left, int right) {
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

void setPanTarget(float angle) {
  panTarget = clamp(angle, PAN_MIN, PAN_MAX);
}

void setTiltTarget(float angle) {
  tiltTarget = clamp(angle, TILT_MIN, TILT_MAX);
}

void centerHead() {
  setPanTarget(0.0f);
  setTiltTarget(0.0f);
}

void sleepHead() {
  setPanTarget(SLEEP_PAN);
  setTiltTarget(SLEEP_TILT);
}

void goBootPose() {
  setPanTarget(bootPan);
  setTiltTarget(bootTilt);
}

void saveBootPose() {
  bootPan  = panCurrent;
  bootTilt = tiltCurrent;
  prefs.begin("cypher", false);
  prefs.putFloat("bootPan", bootPan);
  prefs.putFloat("bootTilt", bootTilt);
  prefs.end();
  Serial.printf("Boot pose saved: pan=%.1f tilt=%.1f\n", bootPan, bootTilt);
}

void loadBootPose() {
  prefs.begin("cypher", true);
  bootPan  = prefs.getFloat("bootPan", DEFAULT_BOOT_PAN);
  bootTilt = prefs.getFloat("bootTilt", DEFAULT_BOOT_TILT);
  prefs.end();
  bootPan  = clamp(bootPan, PAN_MIN, PAN_MAX);
  bootTilt = clamp(bootTilt, TILT_MIN, TILT_MAX);
}

void updateServos() {
  unsigned long now = millis();
  float dt = (now - lastServoUpdate) / 1000.0f;
  if (dt <= 0.0f) return;
  lastServoUpdate = now;

  float maxStep = SERVO_SPEED * dt;

  float panDiff = panTarget - panCurrent;
  if (fabs(panDiff) <= maxStep) panCurrent = panTarget;
  else panCurrent += (panDiff > 0 ? maxStep : -maxStep);

  float tiltDiff = tiltTarget - tiltCurrent;
  if (fabs(tiltDiff) <= maxStep) tiltCurrent = tiltTarget;
  else tiltCurrent += (tiltDiff > 0 ? maxStep : -maxStep);

  float panOut  = INVERT_PAN  ? -panCurrent  : panCurrent;
  float tiltOut = INVERT_TILT ? -tiltCurrent : tiltCurrent;
  panServo.write(panOut + 90.0f);
  tiltServo.write(tiltOut + 90.0f);
}

void processCommand(String cmd) {
  cmd.trim();
  lastCommandTime = millis();

  if (cmd.startsWith("MOVE:")) {
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
    Serial2.printf("STATUS:MANUAL,%d,%d,%.1f,%.1f\n",
                   throttle, steering, panCurrent, tiltCurrent);
  }
  else if (cmd.startsWith("PT:")) {
    int comma = cmd.indexOf(',');
    if (comma > 0) {
      float p = cmd.substring(3, comma).toFloat();
      float t = cmd.substring(comma + 1).toFloat();
      setPanTarget(p);
      setTiltTarget(t);
      Serial2.println("ACK:PT");
    }
  }
  else if (cmd.startsWith("PAN:")) {
    setPanTarget(cmd.substring(4).toFloat());
    Serial2.println("ACK:PAN");
  }
  else if (cmd.startsWith("TILT:")) {
    setTiltTarget(cmd.substring(5).toFloat());
    Serial2.println("ACK:TILT");
  }
  else if (cmd == "PT_CENTER") {
    centerHead();
    Serial2.println("ACK:PT_CENTER");
  }
  else if (cmd == "PT_SLEEP") {
    sleepHead();
    Serial2.println("ACK:PT_SLEEP");
  }
  else if (cmd == "PT_SAVE_BOOT") {
    // Wait until near target so we save settled pose
    saveBootPose();
    Serial2.println("ACK:PT_SAVE_BOOT");
  }
  else if (cmd == "PT_BOOT") {
    goBootPose();
    Serial2.println("ACK:PT_BOOT");
  }
  else if (cmd.length() > 0) {
    Serial2.println("ERR:UNKNOWN_CMD");
  }
}

void setup() {
  Serial.begin(115200);
  Serial2.begin(UART_BAUD, SERIAL_8N1, 19, 18);  // RX=19, TX=18

  delay(200);
  Serial.println();
  Serial.println("=== Cypher ESP32 — Motors + Pan/Tilt ===");
  Serial.println("UART Serial2 RX=19 TX=18");
  Serial.printf("Servo invert pan=%d tilt=%d\n", INVERT_PAN, INVERT_TILT);

  pinMode(AIN1, OUTPUT);
  pinMode(AIN2, OUTPUT);
  pinMode(PWMA, OUTPUT);
  pinMode(BIN1, OUTPUT);
  pinMode(BIN2, OUTPUT);
  pinMode(PWMB, OUTPUT);
  setTankMotors(0, 0);

  ESP32PWM::allocateTimer(0);
  ESP32PWM::allocateTimer(1);
  panServo.setPeriodHertz(50);
  tiltServo.setPeriodHertz(50);
  panServo.attach(PAN_PIN, 500, 2500);
  tiltServo.attach(TILT_PIN, 500, 2500);

  loadBootPose();
  panCurrent = panTarget = bootPan;
  tiltCurrent = tiltTarget = bootTilt;
  lastServoUpdate = millis();
  updateServos();
  Serial.printf("Boot pose: pan=%.1f tilt=%.1f\n", bootPan, bootTilt);

  lastCommandTime = millis();
}

void loop() {
  while (Serial2.available()) {
    char inChar = (char)Serial2.read();
    inputString += inChar;
    if (inChar == '\n') stringComplete = true;
  }

  if (stringComplete) {
    processCommand(inputString);
    inputString = "";
    stringComplete = false;
  }

  updateServos();

  if (millis() - lastCommandTime > COMMAND_TIMEOUT) {
    if (throttle != 0 || steering != 0) {
      throttle = 0;
      steering = 0;
      updateMotors();
    }
  }

  delay(5);
}
