#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoOTA.h>

// === MOTOR PINS (TB6612) ===
#define AIN1 25
#define AIN2 26
#define PWMA 27
#define BIN1 33
#define BIN2 32
#define PWMB 14

// === WIFI ===
const char* ssid_home = "MBPriv";
const char* password_home = "mbsecur3";
const char* ssid_work = "TMOBILE-9DD1";
const char* password_work = "mcmahan12";

// === MOTOR STATE ===
int throttle = 0;     // -255 to 255
int steering = 0;     // -255 to 255
int steeringTrim = 0;

WebServer server(80);

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

// === WEB UI (Manual Only) ===
const char index_html[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body { font-family: Arial; text-align: center; background: #222; color: white; }
    .button { width: 90px; height: 90px; font-size: 28px; margin: 8px; border-radius: 12px; }
    .grid { display: grid; grid-template-columns: repeat(3, 1fr); max-width: 320px; margin: 20px auto; }
    .stop { background: #c33; color: white; font-weight: bold; }
    .slider-container { margin: 20px 0; }
  </style>
</head>
<body>
  <h2>Cypher - Manual Control</h2>

  <div class="grid">
    <div></div>
    <button class="button" onmousedown="sendCmd('forward')" onmouseup="sendCmd('stop')" ontouchstart="sendCmd('forward')" ontouchend="sendCmd('stop')">↑</button>
    <div></div>

    <button class="button" onmousedown="sendCmd('left')" onmouseup="sendCmd('stop')" ontouchstart="sendCmd('left')" ontouchend="sendCmd('stop')">←</button>
    <button class="button stop" onclick="sendCmd('stop')">STOP</button>
    <button class="button" onmousedown="sendCmd('right')" onmouseup="sendCmd('stop')" ontouchstart="sendCmd('right')" ontouchend="sendCmd('stop')">→</button>

    <div></div>
    <button class="button" onmousedown="sendCmd('back')" onmouseup="sendCmd('stop')" ontouchstart="sendCmd('back')" ontouchend="sendCmd('stop')">↓</button>
    <div></div>
  </div>

  <div class="slider-container">
    <label>Speed: <span id="speedVal">120</span></label><br>
    <input type="range" min="0" max="255" value="120" step="5" oninput="updateSpeed(this.value)">
  </div>

  <script>
    let speed = 120;

    function updateSpeed(val) {
      speed = parseInt(val);
      document.getElementById('speedVal').innerText = speed;
    }

    function sendCmd(cmd) {
      let thr = 0;
      let steer = 0;

      if (cmd === 'forward') thr = speed;
      if (cmd === 'back')    thr = -speed;
      if (cmd === 'left')    steer = -speed;
      if (cmd === 'right')   steer = speed;
      if (cmd === 'stop')    { thr = 0; steer = 0; }

      fetch('/control?throttle=' + thr + '&steering=' + steer);
    }
  </script>
</body>
</html>
)rawliteral";

// === WEB HANDLERS ===
void handleRoot() {
  server.send(200, "text/html", index_html);
}

void handleControl() {
  if (server.hasArg("throttle")) throttle = server.arg("throttle").toInt();
  if (server.hasArg("steering")) steering = server.arg("steering").toInt();
  updateMotors();
  server.send(200, "text/plain", "OK");
}

void setup() {
  Serial.begin(115200);
  delay(800);
  Serial.println("\n=== Cypher ESP32 Starting (Manual Mode) ===");

  // Motor pins
  pinMode(AIN1, OUTPUT); pinMode(AIN2, OUTPUT); pinMode(PWMA, OUTPUT);
  pinMode(BIN1, OUTPUT); pinMode(BIN2, OUTPUT); pinMode(PWMB, OUTPUT);

  // Start stopped
  setTankMotors(0, 0);

  // WiFi
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid_home, password_home);
  Serial.print("Connecting to WiFi");
  unsigned long start = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - start < 8000) {
    delay(400); Serial.print(".");
  }

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("\nTrying work WiFi...");
    WiFi.begin(ssid_work, password_work);
    start = millis();
    while (WiFi.status() != WL_CONNECTED && millis() - start < 8000) {
      delay(400); Serial.print(".");
    }
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi connected! IP: " + WiFi.localIP().toString());
  } else {
    Serial.println("\nWiFi connection failed!");
  }

  // OTA
  ArduinoOTA.setHostname("cypher-esp32");
  ArduinoOTA.begin();
  Serial.println("OTA ready");

  // Web server
  server.on("/", handleRoot);
  server.on("/control", handleControl);
  server.begin();
  Serial.println("Web server started");
}

void loop() {
  ArduinoOTA.handle();
  server.handleClient();
}
