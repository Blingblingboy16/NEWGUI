// ESP32 LED Control via Serial
// Controls RGB LED connected to GPIO pins

#define RED_PIN 12
#define GREEN_PIN 13
#define BLUE_PIN 14

void setup() {
  // Initialize serial communication
  Serial.begin(115200);

  // Set LED pins as output
  pinMode(RED_PIN, OUTPUT);
  pinMode(GREEN_PIN, OUTPUT);
  pinMode(BLUE_PIN, OUTPUT);

  // Set up PWM channels for LEDs
  ledcSetup(0, 5000, 8); // Channel 0, 5kHz, 8-bit resolution
  ledcAttachPin(RED_PIN, 0);

  ledcSetup(1, 5000, 8); // Channel 1
  ledcAttachPin(GREEN_PIN, 1);

  ledcSetup(2, 5000, 8); // Channel 2
  ledcAttachPin(BLUE_PIN, 2);

  // Turn off LEDs initially
  setLEDColor(0, 0, 0);
  Serial.println("ESP32 LED Control Ready");
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command.startsWith("LED:")) {
      // Parse LED command: LED:status,brightness,r,g,b
      String params = command.substring(4);
      int parts[5];
      int partIndex = 0;
      int startIndex = 0;

      for (int i = 0; i <= params.length(); i++) {
        if (i == params.length() || params.charAt(i) == ',') {
          if (partIndex < 5) {
            parts[partIndex] = params.substring(startIndex, i).toInt();
            partIndex++;
          }
          startIndex = i + 1;
        }
      }

      if (partIndex == 5) {
        int status = parts[0];
        int brightness = parts[1];
        int r = parts[2];
        int g = parts[3];
        int b = parts[4];

        if (status == 1) {
          // Scale RGB by brightness percentage
          r = (r * brightness) / 100;
          g = (g * brightness) / 100;
          b = (b * brightness) / 100;
          setLEDColor(r, g, b);
          Serial.println("LED Updated");
        } else {
          setLEDColor(0, 0, 0);
          Serial.println("LED OFF");
        }
      }
    } else if (command == "PING") {
      Serial.println("PONG");
    }
  }
}

void setLEDColor(int r, int g, int b) {
  ledcWrite(0, r); // Red
  ledcWrite(1, g); // Green
  ledcWrite(2, b); // Blue
}
