#include <WiFi.h>
#include <WebServer.h>
#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <ArduinoOTA.h>

// === IMU & FILTER (accel for optional roll display, gyro for yaw straight tracking) ===
#define ROLL_SIGN  +1
float filteredRoll = 0.0;
const float alpha = 0.12;

// === MOTOR PINS (TB6612) ===
#define AIN1  25
#define AIN2  26
#define PWMA  27
#define BIN1  33
#define BIN2  32
#define PWMB  14

// === WIFI (Home first, Work fallback) ===
const char* ssid_home     = "MBPriv";
const char* password_home = "mbsecur3";
const char* ssid_work     = "TMOBILE-9DD1";
const char* password_work = "mcmahan12";

// === STRAIGHT TRACKING (yaw hold with gyro - active only when moving straight, no turn command) ===
float yawKp = 2.0;           // main correction gain (tune in UI)
float yawKd = 0.5;           // rate damping (optional)
float gyroZoffset = 0.0;
float currentYaw = 0.0;
float targetYaw = 0.0;
bool holdingStraight = false;
int yawSign = 1;             // flip sign if correction is backwards

float throttle = 0.0;        // base speed command (throttle / speed)
int steering = 0;            // turn command from UI
int steeringTrim = 0;

bool straightHoldEnabled = true;  // master enable for yaw correction / straight tracking
float roll = 0;              // for optional display / debug (from accel)
unsigned long lastUpdateTime = 0;

const float YAW_DEADBAND = 2.0f;
const int STRAIGHT_THRESHOLD = 12; // |steer| below this = straight for hold

Adafruit_MPU6050 mpu;
WebServer server(80);

void setTankMotors(int left, int right) {
  if (left > 0) { digitalWrite(AIN1, HIGH); digitalWrite(AIN2, LOW); }
  else if (left < 0) { digitalWrite(AIN1, LOW);  digitalWrite(AIN2, HIGH); }
  else { digitalWrite(AIN1, LOW); digitalWrite(AIN2, LOW); }
  analogWrite(PWMA, abs(left));

  if (right > 0) { digitalWrite(BIN1, HIGH); digitalWrite(BIN2, LOW); }
  else if (right < 0) { digitalWrite(BIN1, LOW);  digitalWrite(BIN2, HIGH); }
  else { digitalWrite(BIN1, LOW); digitalWrite(BIN2, LOW); }
  analogWrite(PWMB, abs(right));
}

void updateIMU() {
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);

  // Keep accel-based roll for info/display (not used for control anymore)
  float rawRoll = atan2(a.acceleration.y, a.acceleration.z) * 180.0 / PI * ROLL_SIGN;
  filteredRoll = alpha * rawRoll + (1.0 - alpha) * filteredRoll;
  roll = filteredRoll;

  // Yaw from gyro Z (integrated). Use for straight tracking correction.
  unsigned long now = millis();
  float dt = (now - lastUpdateTime) / 1000.0;
  if (dt <= 0 || dt > 0.5) dt = 0.01;
  lastUpdateTime = now;

  float gyroZ = (g.gyro.z - gyroZoffset) * (180.0 / PI);  // rad/s to deg/s (Adafruit already in rad/s)
  currentYaw += gyroZ * dt * yawSign;
}

void calibrateGyro() {
  Serial.println("Calibrating gyro - keep still for 1s...");
  float sum = 0;
  const int samples = 200;
  for (int i = 0; i < samples; i++) {
    sensors_event_t a, g, temp;
    mpu.getEvent(&a, &g, &temp);
    sum += g.gyro.z;
    delay(5);
  }
  gyroZoffset = sum / samples;
  Serial.printf("Gyro Z offset: %.4f rad/s\n", gyroZoffset);
  currentYaw = 0;
  targetYaw = 0;
  holdingStraight = false;
}

void updateStraightTracking() {
  // Base command from UI (throttle = forward/back speed, steering = turn command)
  int base = (int)throttle;
  int steer = steering + steeringTrim;

  int leftCmd = base + steer;
  int rightCmd = base - steer;

  // Heading hold / straight correction ONLY when enabled, moving, and NOT commanded to turn
  if (straightHoldEnabled && abs(base) > 10 && abs(steer) < STRAIGHT_THRESHOLD) {
    if (!holdingStraight) {
      targetYaw = currentYaw;
      holdingStraight = true;
    }

    float yawError = (currentYaw - targetYaw) * yawSign;
    if (abs(yawError) < YAW_DEADBAND) yawError = 0;

    // Simple P + small D (using current gyro rate as proxy)
    sensors_event_t a, g, temp;
    mpu.getEvent(&a, &g, &temp);  // fresh gyro for rate (cheap since called infrequently)
    float gyroRate = g.gyro.z * (180.0 / PI) * yawSign;

    float correction = (yawKp * yawError) + (yawKd * gyroRate);
    correction = constrain(correction, -80, 80);

    leftCmd  += (int)correction;
    rightCmd -= (int)correction;
  } else {
    holdingStraight = false;
  }

  leftCmd = constrain(leftCmd, -255, 255);
  rightCmd = constrain(rightCmd, -255, 255);

  setTankMotors(leftCmd, rightCmd);
}

const char index_html[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body { font-family: Arial; text-align: center; background: #222; color: white; }
    body, .button, .grid {
      -webkit-user-select: none;
      -moz-user-select: none;
      -ms-user-select: none;
      user-select: none;
      touch-action: manipulation;
    }
    .button { width: 80px; height: 80px; font-size: 24px; margin: 10px; border-radius: 12px; }
    .grid { display: grid; grid-template-columns: repeat(3, 1fr); max-width: 300px; margin: auto; }
    .slider-container { margin: 15px 0; }
    .value { font-size: 18px; color: #0f0; }
  </style>
</head>
<body>
  <h2>Sentry Bot - Straight Tracking</h2>
  
  <div style="margin: 20px 0;">
    <button onclick="toggleHold()" id="holdBtn" class="button" style="width:160px; background:#4CAF50;">STRAIGHT HOLD ON</button>
  </div>

  <div class="grid">
    <div></div>
    <button class="button" onmousedown="pressButton('forward')" onmouseup="releaseButton()" ontouchstart="pressButton('forward')" ontouchend="releaseButton()">↑</button>
    <div></div>
    <button class="button" onmousedown="pressButton('left')" onmouseup="releaseButton()" ontouchstart="pressButton('left')" ontouchend="releaseButton()">←</button>
    <button class="button" onclick="stopAll()" style="background:#555;">STOP</button>
    <button class="button" onmousedown="pressButton('right')" onmouseup="releaseButton()" ontouchstart="pressButton('right')" ontouchend="releaseButton()">→</button>
    <div></div>
    <button class="button" onmousedown="pressButton('back')" onmouseup="releaseButton()" ontouchstart="pressButton('back')" ontouchend="releaseButton()">↓</button>
    <div></div>
  </div>

  <div class="slider-container">
    <label>Throttle / Speed: <span id="leanVal">0</span></label><br>
    <input type="range" min="-180" max="180" value="0" step="5" oninput="updateLean(this.value)">
  </div>

  <div class="slider-container">
    <label>Steering Trim: <span id="trimVal">0</span></label><br>
    <input type="range" min="-40" max="40" value="0" step="1" oninput="updateTrim(this.value)">
  </div>

  <div class="slider-container">
    <label>Yaw Kp: <span id="kpVal">2.0</span></label><br>
    <input type="range" min="0" max="8" value="2.0" step="0.1" oninput="updatePID('kp', this.value)">
  </div>
  <div class="slider-container">
    <label>Yaw Kd: <span id="kdVal">0.5</span></label><br>
    <input type="range" min="0" max="3" value="0.5" step="0.1" oninput="updatePID('kd', this.value)">
  </div>

  <h3>Yaw Err / Hold: <span id="yaw" class="value">0.0 | FREE</span></h3>

  <div>
    <button onclick="calGyro()">Cal Gyro (still)</button>
    <button onclick="resetHeading()">Reset Heading</button>
  </div>

  <script>
    let holding = true;
    let leanAngle = 0;
    let trim = 0;

    function updateLean(val) {
      leanAngle = parseFloat(val);
      document.getElementById('leanVal').innerText = leanAngle;
      fetch('/setlean?angle=' + leanAngle);
    }

    function updateTrim(val) {
      trim = parseInt(val);
      document.getElementById('trimVal').innerText = trim;
      fetch('/settrim?value=' + trim);
    }

    function updatePID(type, val) {
      if (type === 'kp') {
        document.getElementById('kpVal').innerText = parseFloat(val).toFixed(1);
        fetch('/setpid?kp=' + val + '&kd=' + document.getElementById('kdVal').innerText);
      } else {
        document.getElementById('kdVal').innerText = parseFloat(val).toFixed(1);
        fetch('/setpid?kp=' + document.getElementById('kpVal').innerText + '&kd=' + val);
      }
    }

    function toggleHold() {
      holding = !holding;
      const btn = document.getElementById('holdBtn');
      if (holding) {
        btn.innerText = 'STRAIGHT HOLD ON';
        btn.style.background = '#4CAF50';
      } else {
        btn.innerText = 'STRAIGHT HOLD OFF';
        btn.style.background = '#f44336';
        fetch('/balance?state=0');
        return;
      }
      fetch('/balance?state=1');
    }

    function pressButton(dir) {
      let thr = 0;
      let steer = 0;
      if (dir === 'forward') thr = 120;
      if (dir === 'back') thr = -120;
      if (dir === 'left') steer = 60;
      if (dir === 'right') steer = -60;

      fetch('/setlean?angle=' + thr);
      fetch('/steer?value=' + steer);
    }

    function releaseButton() {
      fetch('/setlean?angle=0');
      fetch('/steer?value=0');
    }

    function stopAll() {
      fetch('/balance?state=0');
      fetch('/setlean?angle=0');
      fetch('/steer?value=0');
    }

    function calGyro() {
      fetch('/calgyro');
    }

    function resetHeading() {
      fetch('/balance?state=0');
      setTimeout(() => { fetch('/balance?state=1'); }, 150);
    }

    setInterval(() => {
      fetch('/roll')
        .then(r => r.text())
        .then(t => {
          document.getElementById('yaw').innerText = t;
        });
    }, 300);
  </script>
</body>
</html>
)rawliteral";

void handleRoot() { server.send(200, "text/html", index_html); }
void handleSetLean() { if (server.hasArg("angle")) throttle = server.arg("angle").toFloat(); server.send(200, "text/plain", "OK"); }  // base speed/throttle
void handleSteer() { if (server.hasArg("value")) steering = server.arg("value").toInt(); server.send(200, "text/plain", "OK"); }
void handleSetTrim() { if (server.hasArg("value")) steeringTrim = server.arg("value").toInt(); server.send(200, "text/plain", "OK"); }
void handleSetPID() { 
  if (server.hasArg("kp")) yawKp = server.arg("kp").toFloat(); 
  if (server.hasArg("kd")) yawKd = server.arg("kd").toFloat(); 
  server.send(200, "text/plain", "OK"); 
}
void handleBalance() { 
  if (server.hasArg("state")) { 
    straightHoldEnabled = server.arg("state").toInt() == 1; 
    if (!straightHoldEnabled) holdingStraight = false; 
  } 
  server.send(200, "text/plain", "OK"); 
}
void handleRoll() {
  // Return yaw error + hold state for the display
  float err = (currentYaw - targetYaw) * yawSign;
  String state = holdingStraight ? "HOLD" : "FREE";
  server.send(200, "text/plain", String(err, 1) + " | " + state);
}

void setup() {
  Serial.begin(115200);
  Wire.begin(21, 22);

  pinMode(AIN1, OUTPUT); pinMode(AIN2, OUTPUT); pinMode(PWMA, OUTPUT);
  pinMode(BIN1, OUTPUT); pinMode(BIN2, OUTPUT); pinMode(PWMB, OUTPUT);

  if (!mpu.begin()) { Serial.println("MPU6050 not found!"); while (1); }
  mpu.setAccelerometerRange(MPU6050_RANGE_4_G);
  delay(100);
  calibrateGyro();  // auto zero gyro at boot (bot should be still)
  lastUpdateTime = millis();

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid_home, password_home);
  Serial.print("Connecting to home WiFi");
  unsigned long start = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - start < 8000) { delay(500); Serial.print("."); }
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("\nTrying work WiFi...");
    WiFi.begin(ssid_work, password_work);
    start = millis();
    while (WiFi.status() != WL_CONNECTED && millis() - start < 8000) { delay(500); Serial.print("."); }
  }
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nConnected! IP: " + WiFi.localIP().toString());
  } else {
    Serial.println("\nWiFi connection failed!");
  }
  Serial.println("Straight tracking mode (yaw hold on straight moves). Use UI to toggle hold, tune YawKp/Kd.");

  // === OTA Update Support ===
  ArduinoOTA.setHostname("sentrybot");
  ArduinoOTA.onStart([]() {
    String type;
    if (ArduinoOTA.getCommand() == U_FLASH) {
      type = "sketch";
    } else {  // U_SPIFFS
      type = "filesystem";
    }
    Serial.println("Start updating " + type);
  });
  ArduinoOTA.onEnd([]() {
    Serial.println("\nEnd");
  });
  ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
    Serial.printf("Progress: %u%%\r", (progress / (total / 100)));
  });
  ArduinoOTA.onError([](ota_error_t error) {
    Serial.printf("Error[%u]: ", error);
    if (error == OTA_AUTH_ERROR) Serial.println("Auth Failed");
    else if (error == OTA_BEGIN_ERROR) Serial.println("Begin Failed");
    else if (error == OTA_CONNECT_ERROR) Serial.println("Connect Failed");
    else if (error == OTA_RECEIVE_ERROR) Serial.println("Receive Failed");
    else if (error == OTA_END_ERROR) Serial.println("End Failed");
  });
  ArduinoOTA.begin();
  Serial.println("OTA ready (hostname: sentrybot)");

  server.on("/", handleRoot);
  server.on("/setlean", handleSetLean);
  server.on("/steer", handleSteer);
  server.on("/settrim", handleSetTrim);
  server.on("/setpid", handleSetPID);
  server.on("/balance", handleBalance);
  server.on("/roll", handleRoll);
  server.on("/calgyro", []( ) { calibrateGyro(); server.send(200, "text/plain", "Gyro calibrated"); });
  server.begin();
  Serial.println("Web server started");
}

void loop() {
  ArduinoOTA.handle();
  server.handleClient();
  updateIMU();
  updateStraightTracking();
  delay(10);
}