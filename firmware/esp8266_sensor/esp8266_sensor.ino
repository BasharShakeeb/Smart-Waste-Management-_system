#include <ESP8266WiFi.h>
#include <WiFiClientSecure.h>
#include <ESP8266HTTPClient.h>

// 🔹 بيانات الواي فاي
const char* ssid = "bashar";
const char* password = "bashar12";

// 🔹 رابط السيرفر (موقعك)
const char* serverUrl = "https://smart-waste-management-system-1-hi0q.onrender.com/api/bins/1/sensor-readings";
// 🔹 أرجل الحساس
#define TRIG D5
#define ECHO D6 

void setup() {
  Serial.begin(115200);

  pinMode(TRIG, OUTPUT);
  pinMode(ECHO, INPUT);

  // الاتصال بالواي فاي
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nConnected!");
}

void loop() {
  long duration;
  float distance;

  // إرسال نبضة
  digitalWrite(TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG, LOW);

  // استقبال النبضة
  duration = pulseIn(ECHO, HIGH);

  // حساب المسافة (cm)
  distance = duration * 0.034 / 2;

  Serial.print("Distance: ");
  Serial.println(distance);

  // إرسال البيانات للسيرفر
  if (WiFi.status() == WL_CONNECTED) {

    WiFiClientSecure client;
    client.setInsecure();  // مهم لتفادي مشاكل SSL

    HTTPClient http;
    http.begin(client, serverUrl);
    http.addHeader("Content-Type", "application/json");

    // JSON data
    String json = "{\"distance\": " + String(distance) + "}";

    int httpResponseCode = http.POST(json);

    Serial.print("HTTP Response Code: ");
    Serial.println(httpResponseCode);

    http.end();
  } else {
    Serial.println("WiFi Disconnected");
  }

  delay(5000); // كل 5 ثواني
}