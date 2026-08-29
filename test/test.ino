int count = 1;

void setup() {
  Serial.begin(115200);
}

void loop() {
  Serial.println(count);
  count++;
  delay(1000);
}