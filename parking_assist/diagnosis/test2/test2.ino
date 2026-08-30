int testPin = 16;   // ← テストしたいピンをここで変える

void setup() {
  Serial.begin(115200);
  delay(1000);
  pinMode(testPin, OUTPUT);
  pinMode(34, INPUT);
  Serial.printf("\nTesting GPIO %d  (jumper to GPIO34)\n", testPin);
}

void loop() {
  digitalWrite(testPin, HIGH);
  delay(100);
  int hi = digitalRead(34);

  digitalWrite(testPin, LOW);
  delay(100);
  int lo = digitalRead(34);

  if (hi == HIGH && lo == LOW) {
    Serial.printf("GPIO %d : OK  (HIGH/LOW both detected)\n", testPin);
  } else {
    Serial.printf("GPIO %d : FAIL  (HIGH=%d LOW=%d)\n", testPin, hi, lo);
  }
  delay(1000);
}