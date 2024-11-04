const int relayPin = 7; // Pin connected to the relay

void setup() {
  pinMode(relayPin, OUTPUT);
  digitalWrite(relayPin, LOW); // Relay off initially
  Serial.begin(9600); // Start serial communication
}

void loop() {
  if (Serial.available() > 0) {
    String message = Serial.readStringUntil('\n');
    if (message == "activate_relay") {
      digitalWrite(relayPin, HIGH); // Turn on the relay
      delay(2000); // Keep the relay on for 2 seconds (or adjust as needed)
      digitalWrite(relayPin, LOW); // Turn off the relay
    }
  }
}
