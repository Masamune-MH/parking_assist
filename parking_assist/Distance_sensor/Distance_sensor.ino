int leftDistance = 45;
int centerDistance = 52;
int rightDistance = 70;

void setup() {
  Serial.begin(115200);
}

void loop() {
  Serial.print("Left: ");
  Serial.print(leftDistance);
  Serial.print(" cm, ");

  Serial.print("Center: ");
  Serial.print(centerDistance);
  Serial.print(" cm, ");

  Serial.print("Right: ");
  Serial.print(rightDistance);
  Serial.println(" cm");

  delay(1000);
}