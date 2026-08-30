struct Sensor {
  const char* name;
  int trig;
  int echo;
};

Sensor sensors[] = {
  {"LEFT",   16, 18},
  {"CENTER", 19, 21},
  {"RIGHT",  22, 23}
};

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("\n=== Sensor Diagnostic ===\n");

  for (auto &s : sensors) {
    pinMode(s.trig, OUTPUT);
    pinMode(s.echo, INPUT);
    digitalWrite(s.trig, LOW);
  }
  delay(100);

  // ECHOピンのアイドル状態を確認
  Serial.println("--- Idle state of ECHO pins ---");
  for (auto &s : sensors) {
    int v = digitalRead(s.echo);
    Serial.printf("%-7s ECHO(GPIO%2d) = %s %s\n",
      s.name, s.echo, v == LOW ? "LOW " : "HIGH",
      v == LOW ? "OK" : "<-- ABNORMAL (wiring problem?)");
  }
  Serial.println();
}

void loop() {
  for (auto &s : sensors) {
    digitalWrite(s.trig, LOW);
    delayMicroseconds(4);
    digitalWrite(s.trig, HIGH);
    delayMicroseconds(10);
    digitalWrite(s.trig, LOW);

    // ECHOが立ち上がるのを待つ
    unsigned long t0 = micros();
    while (digitalRead(s.echo) == LOW) {
      if (micros() - t0 > 30000) {
        Serial.printf("%-7s NO RESPONSE  -> TRIG(%d) not working, or sensor/power problem\n",
                      s.name, s.trig);
        goto next;
      }
    }

    // ECHOが下がるのを待つ = パルス幅を測る
    {
      unsigned long start = micros();
      while (digitalRead(s.echo) == HIGH) {
        if (micros() - start > 30000) {
          Serial.printf("%-7s ECHO STUCK HIGH -> ECHO(%d) wiring or voltage divider problem\n",
                        s.name, s.echo);
          goto next;
        }
      }
      unsigned long dur = micros() - start;
      float cm = dur / 58.0;
      Serial.printf("%-7s OK  %6.1f cm  (pulse %lu us)\n", s.name, cm, dur);
    }

    next:
    delay(60);
  }
  Serial.println("---");
  delay(1000);
}