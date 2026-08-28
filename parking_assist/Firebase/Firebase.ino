#include <WiFi.h>
#include <Firebase_ESP_Client.h>
#include <addons/TokenHelper.h>
#include <addons/RTDBHelper.h>

// ========================================
// Wi-Fi configuration
// ========================================
// Replace these values before testing
#define WIFI_SSID "YOUR_WIFI_SSID"
#define WIFI_PASSWORD "YOUR_WIFI_PASSWORD"

// ========================================
// Firebase configuration
// ========================================
// Use the Firebase configuration from
// ESP32_Firebase_Code_Example.txt
#define API_KEY "YOUR_FIREBASE_API_KEY"
#define DATABASE_URL "YOUR_FIREBASE_DATABASE_URL"
#define USER_EMAIL "YOUR_FIREBASE_USER_EMAIL"
#define USER_PASSWORD "YOUR_FIREBASE_USER_PASSWORD"

FirebaseData fbdo;
FirebaseAuth auth;
FirebaseConfig config;


// ========================================
// HC-SR04 GPIO
// ========================================

// Left sensor
const int LEFT_TRIG = 5;
const int LEFT_ECHO = 18;

// Center sensor
const int CENTER_TRIG = 19;
const int CENTER_ECHO = 21;

// Right sensor
const int RIGHT_TRIG = 22;
const int RIGHT_ECHO = 23;


// ========================================
// Upload interval
// ========================================

unsigned long lastSend = 0;
const unsigned long SEND_INTERVAL = 1000;


// ========================================
// Measure distance
// ========================================

long getDistance(int trigPin, int echoPin) {

  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);

  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);

  digitalWrite(trigPin, LOW);

  long duration = pulseIn(
    echoPin,
    HIGH,
    30000
  );

  // No echo received
  if (duration == 0) {
    return -1;
  }

  // Convert echo time to distance (cm)
  long distance = duration * 0.034 / 2;

  return distance;
}


// ========================================
// Upload sensor data to Firebase
// ========================================

void uploadToFirebase(
  long left,
  long center,
  long right
) {

  if (!Firebase.ready()) {

    Serial.println(
      "Firebase is not ready."
    );

    return;
  }


  FirebaseJson json;

  json.set("Left", left);
  json.set("Center", center);
  json.set("Right", right);


  if (Firebase.RTDB.setJSON(
        &fbdo,
        "/Parking/Current",
        &json)) {

    Serial.println(
      "Firebase upload successful."
    );

  } else {

    Serial.print(
      "Firebase upload failed: "
    );

    Serial.println(
      fbdo.errorReason()
    );
  }
}


// ========================================
// Setup
// ========================================

void setup() {

  Serial.begin(115200);

  delay(1000);


  // ========================================
  // HC-SR04 pin settings
  // ========================================

  pinMode(
    LEFT_TRIG,
    OUTPUT
  );

  pinMode(
    LEFT_ECHO,
    INPUT
  );


  pinMode(
    CENTER_TRIG,
    OUTPUT
  );

  pinMode(
    CENTER_ECHO,
    INPUT
  );


  pinMode(
    RIGHT_TRIG,
    OUTPUT
  );

  pinMode(
    RIGHT_ECHO,
    INPUT
  );


  // ========================================
  // Wi-Fi connection
  // ========================================

  WiFi.mode(WIFI_STA);

  WiFi.begin(
    WIFI_SSID,
    WIFI_PASSWORD
  );


  Serial.print(
    "Connecting to Wi-Fi"
  );


  while (
    WiFi.status() != WL_CONNECTED
  ) {

    delay(500);

    Serial.print(".");
  }


  Serial.println();

  Serial.println(
    "Wi-Fi connected."
  );


  Serial.print(
    "ESP32 IP address: "
  );

  Serial.println(
    WiFi.localIP()
  );


  // ========================================
  // Firebase connection
  // ========================================

  config.api_key =
    API_KEY;

  config.database_url =
    DATABASE_URL;

  config.token_status_callback =
    tokenStatusCallback;


  auth.user.email =
    USER_EMAIL;

  auth.user.password =
    USER_PASSWORD;


  Firebase.begin(
    &config,
    &auth
  );


  Firebase.reconnectWiFi(true);


  Serial.println(
    "Firebase initialized."
  );
}


// ========================================
// Main loop
// ========================================

void loop() {

  // Read Left sensor
  long left = getDistance(
    LEFT_TRIG,
    LEFT_ECHO
  );

  delay(30);


  // Read Center sensor
  long center = getDistance(
    CENTER_TRIG,
    CENTER_ECHO
  );

  delay(30);


  // Read Right sensor
  long right = getDistance(
    RIGHT_TRIG,
    RIGHT_ECHO
  );


  // ========================================
  // Serial Monitor
  // ========================================

  Serial.print(
    "Left: "
  );

  Serial.print(left);


  Serial.print(
    " cm | Center: "
  );

  Serial.print(center);


  Serial.print(
    " cm | Right: "
  );

  Serial.print(right);

  Serial.println(" cm");


  // ========================================
  // Upload every second
  // ========================================

  if (
    millis() - lastSend
    >= SEND_INTERVAL
  ) {

    lastSend = millis();


    uploadToFirebase(
      left,
      center,
      right
    );
  }


  delay(200);
}