#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>

// --- إعدادات الواي فاي ---
const char* ssid = "bashar";
const char* password = "bashar12";

// --- إعدادات السيرفر الخلفي ---
const char* serverUrl = "http://10.119.134.63:5000/api/bins/2/sensor-readings"; 
const float binDepth = 100.0; // عمق الصندوق

// --- تعريف الأرجل ---
const int trigPin = D1; 
const int echoPin = D2;

// --- مؤقت الإرسال ---
unsigned long lastTime = 0;
unsigned long timerDelay = 6000; // 6 ثواني

void setup() {
  Serial.begin(115200);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  delay(1000); // تثبيت الحساس

  // الاتصال بالواي فاي
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected to WiFi!");
}

void loop() {
  if ((millis() - lastTime) > timerDelay) {

    if (WiFi.status() == WL_CONNECTED) {

      // ---- قياس المسافة ----
      digitalWrite(trigPin, LOW);
      delayMicroseconds(2);
      digitalWrite(trigPin, HIGH);
      delayMicroseconds(10);
      digitalWrite(trigPin, LOW);

      long duration = pulseIn(echoPin, HIGH);
      Serial.print("Raw duration: ");
      Serial.println(duration);

      float distanceCm = duration * 0.017;
      Serial.printf("Distance: %.2f cm\n", distanceCm);

      // ---- تحقق من القراءة ----
      if (distanceCm <= 0 || distanceCm > binDepth) {
        Serial.println("Invalid distance reading, skipping send.");
      } else {
        int fillLevel = constrain((int)((1.0 - distanceCm / binDepth) * 100), 0, 100);
        Serial.printf("Fill Level: %d%%\n", fillLevel);

        // ---- إرسال البيانات ----
        WiFiClient client;
        HTTPClient http;
        http.begin(client, serverUrl);
        http.addHeader("Content-Type", "application/json");

        String payload = "{\"fill_level\":" + String(fillLevel) + 
                         ",\"battery_level\":100" +
                         ",\"signal_strength\":" + String(WiFi.RSSI()) + 
                         ",\"temperature\":25.0,\"humidity\":50.0}";

        int httpCode = http.POST(payload);
        if (httpCode > 0) {
          Serial.printf("HTTP POST successful, code: %d\n", httpCode);
        } else {
          Serial.printf("HTTP POST failed, code: %d. Retrying...\n", httpCode);
          delay(1000);
          httpCode = http.POST(payload);
          if (httpCode > 0) {
            Serial.printf("Retry successful, code: %d\n", httpCode);
          } else {
            Serial.printf("Retry failed, code: %d\n", httpCode);
          }
        }
        http.end();
      }

    } else {
      Serial.println("WiFi disconnected. Reconnecting...");
      WiFi.reconnect();
    }

    lastTime = millis();
  }
}

