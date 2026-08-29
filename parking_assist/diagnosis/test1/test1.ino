int pins[] = {16, 18, 19, 21, 22, 23};

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("\n=== GPIO Output Test ===");
  Serial.println("Connect a jumper from each pin to GPIO 34 (input only) to verify.\n");

  for (int p : pins) {
    pinMode(p, OUTPUT);
  }
  pinMode(34, INPUT);
}

void loop() {
  for (int p : pins) {
    // 全部LOWにしてから対象だけHIGH
    for (int q : pins) digitalWrite(q, LOW);
    delay(10);
    digitalWrite(p, HIGH);
    delay(10);
    int read34 = digitalRead(34);
    Serial.printf("GPIO %2d set HIGH -> GPIO34 reads %s %s\n",
                  p, read34 ? "HIGH" : "LOW ",
                  read34 ? "OK (jumper connected)" : "");
  }
  Serial.println("---");
  delay(2000);
}