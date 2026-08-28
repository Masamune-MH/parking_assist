#include <WiFi.h>
#include <WebServer.h>

// =========================
// Wi-Fi
// =========================

const char* ssid = "msmne";
const char* password = "takamitakaka";

WebServer server(80);


// =========================
// HC-SR04 GPIO
// =========================

// 左
const int LEFT_TRIG = 16;
const int LEFT_ECHO = 18;

// 中央
const int CENTER_TRIG = 19;
const int CENTER_ECHO = 21;

// 右
const int RIGHT_TRIG = 22;
const int RIGHT_ECHO = 23;


// =========================
// 距離測定
// =========================

long getDistance(int trigPin, int echoPin) {

  // TRIGをLOWにする
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);

  // 10μsだけHIGHにして超音波を発射
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  // ECHOがHIGHになっている時間を測定
  long duration = pulseIn(echoPin, HIGH, 30000);

  // タイムアウトした場合
  if (duration == 0) {
    return -1;
  }

  // 音速から距離(cm)を計算
  long distance = duration * 0.034 / 2;

  return distance;
}


// =========================
// PCからアクセスされたとき
// =========================

void handleRoot() {

  long left = getDistance(LEFT_TRIG, LEFT_ECHO);

  delay(30);

  long center = getDistance(CENTER_TRIG, CENTER_ECHO);

  delay(30);

  long right = getDistance(RIGHT_TRIG, RIGHT_ECHO);

  String message = "";

  message += "Left: ";
  message += left;
  message += " cm\n";

  message += "Center: ";
  message += center;
  message += " cm\n";

  message += "Right: ";
  message += right;
  message += " cm\n";

  server.send(200, "text/plain", message);
}


// =========================
// setup
// =========================

void setup() {

  Serial.begin(115200);

  // GPIO設定
  pinMode(LEFT_TRIG, OUTPUT);
  pinMode(LEFT_ECHO, INPUT);

  pinMode(CENTER_TRIG, OUTPUT);
  pinMode(CENTER_ECHO, INPUT);

  pinMode(RIGHT_TRIG, OUTPUT);
  pinMode(RIGHT_ECHO, INPUT);


  // Wi-Fi接続
  WiFi.begin(ssid, password);

  Serial.print("Wi-Fi接続中");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.println("Wi-Fi接続成功！");
  Serial.print("ESP32のIPアドレス: ");
  Serial.println(WiFi.localIP());


  // Webサーバー開始
  server.on("/", handleRoot);
  server.begin();

  Serial.println("Webサーバー開始");
}


// =========================
// loop
// =========================

void loop() {

  server.handleClient();

  // シリアルモニタにも距離を表示
  long left = getDistance(LEFT_TRIG, LEFT_ECHO);

  delay(30);

  long center = getDistance(CENTER_TRIG, CENTER_ECHO);

  delay(30);

  long right = getDistance(RIGHT_TRIG, RIGHT_ECHO);

  Serial.print("Left: ");
  Serial.print(left);
  Serial.print(" cm, ");

  Serial.print("Center: ");
  Serial.print(center);
  Serial.print(" cm, ");

  Serial.print("Right: ");
  Serial.print(right);
  Serial.println(" cm");

  delay(500);
}