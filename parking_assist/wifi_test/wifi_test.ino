#include <WiFi.h>
#include <WebServer.h>

const char* ssid = "msmne";
const char* password = "takamitakaka";

WebServer server(80);

int count = 1;

void handleRoot() {
  server.send(200, "text/plain", String(count));
}

void setup() {
  Serial.begin(115200);

  WiFi.begin(ssid, password);

  Serial.print("Wi-Fiに接続中");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.println("Wi-Fi接続成功！");
  Serial.print("ESP32のIPアドレス: ");
  Serial.println(WiFi.localIP());

  server.on("/", handleRoot);
  server.begin();

  Serial.println("Webサーバー開始");
}

void loop() {
  server.handleClient();

  count++;

  delay(1000);
}