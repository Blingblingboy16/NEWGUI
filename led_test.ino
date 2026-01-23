#include <Adafruit_NeoPixel.h>

// ---------- CONFIG ----------
#define PIN_NEO_PIXEL 6
#define NUM_PIXELS 16
#define DEFAULT_BRIGHTNESS 128

// ---------- OBJECT ----------
Adafruit_NeoPixel strip(NUM_PIXELS, PIN_NEO_PIXEL, NEO_GRB + NEO_KHZ800);

// ---------- STATE ----------
uint8_t r = 0, g = 0, b = 0;
uint8_t brightness = DEFAULT_BRIGHTNESS;

// ---------- SETUP ----------
void setup() {
  Serial.begin(9600);

  strip.begin();
  strip.setBrightness(brightness);
  strip.show();  // all off

  Serial.println("NEOPIXEL_READY");
}

// ---------- LOOP ----------
void loop() {
  handleSerial();
}

// ---------- FUNCTIONS ----------
void handleSerial() {
  if (!Serial.available()) return;

  String msg = Serial.readStringUntil('\n');
  msg.trim();

  // Example: COLOR,255,0,0
  if (msg.startsWith("COLOR")) {
    int c1 = msg.indexOf(',');
    int c2 = msg.indexOf(',', c1 + 1);
    int c3 = msg.indexOf(',', c2 + 1);

    r = msg.substring(c1 + 1, c2).toInt();
    g = msg.substring(c2 + 1, c3).toInt();
    b = msg.substring(c3 + 1).toInt();

    setAllPixels(r, g, b);

    Serial.print("COLOR_SET,");
    Serial.print(r); Serial.print(",");
    Serial.print(g); Serial.print(",");
    Serial.println(b);
  }

  // Example: BRIGHT,150
  else if (msg.startsWith("BRIGHT")) {
    int comma = msg.indexOf(',');
    brightness = msg.substring(comma + 1).toInt();
    brightness = constrain(brightness, 0, 255);

    strip.setBrightness(brightness);
    strip.show();

    Serial.print("BRIGHT_SET,");
    Serial.println(brightness);
  }

  // Example: OFF
  else if (msg == "OFF") {
    setAllPixels(0, 0, 0);
    Serial.println("OFF_OK");
  }
}

void setAllPixels(uint8_t r, uint8_t g, uint8_t b) {
  for (int i = 0; i < strip.numPixels(); i++) {
    strip.setPixelColor(i, strip.Color(r, g, b));
  }
  strip.show();
}
