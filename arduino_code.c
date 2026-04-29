#include <Adafruit_NeoPixel.h>
#include <DHT.h>
#include <Wire.h>
#include "SCMD.h"
#include "SCMD_config.h"

// ================= PIN MAPPING (FEATHER S2) =================
#define FAN_PIN    12      // MOSFET for Fan
#define LED_PIN    10      // NeoPixel Ring
#define DHT_PIN     8      // DHT11 Data (Labeled A5)
#define NUM_PIXELS 16     
#define DHTTYPE    DHT11  

SCMD myMotorDriver; 
Adafruit_NeoPixel ring(NUM_PIXELS, LED_PIN, NEO_GRB + NEO_KHZ800);
DHT dht(DHT_PIN, DHTTYPE);

// State Variables
bool sensorsEnabled = true;
unsigned long sensorLast = 0;

void setup() {
  Serial.begin(115200);
  
  // WAIT for Serial (Crucial for Feather S2 Native USB)
  while (!Serial) { delay(10); }

  // Power up NeoPixel rail
  pinMode(NEOPIXEL_POWER, OUTPUT);
  digitalWrite(NEOPIXEL_POWER, HIGH); 

  Wire.begin();
  ring.begin();
  ring.setBrightness(50);
  ring.show(); 
  dht.begin();

  // Initialize Qwiic Motor Driver
  myMotorDriver.settings.commInterface = I2C_MODE;
  myMotorDriver.settings.I2CAddress = 0x5D; // Default Address
  
  Serial.println("Checking Motor Driver...");
  if (myMotorDriver.begin() != 0xA9) {
    Serial.println("ERROR: Motor Driver not found. Check Qwiic cable and 9V power.");
  } else {
    Serial.println("Motor Driver Connected!");
  }
  myMotorDriver.enable(); 

  // Setup PWM for Fan MOSFET
  ledcAttach(FAN_PIN, 1000, 8);

  Serial.println("--- SYSTEM ONLINE (WITH DRIVER) ---");
  Serial.println("Commands: PING, LED:s,b,r,g,b , FAN:spd , PUMP:spd , MOTOR:spd");
}

void loop() {
  if (Serial.available() > 0) {
    String msg = Serial.readStringUntil('\n');
    msg.trim();
    
    // ECHO for debugging
    Serial.print("Received: ["); Serial.print(msg); Serial.println("]");
    handleCommand(msg);
  }

  // DHT Sensor Update
  if (sensorsEnabled && (millis() - sensorLast >= 2000)) {
    float h = dht.readHumidity();
    float t = dht.readTemperature();
    if (!isnan(h)) {
      Serial.print("DHT_DATA,"); Serial.print(t); Serial.print(","); Serial.println(h);
    }
    sensorLast = millis();
  }
}

void handleCommand(String msg) {
  if (msg == "PING") {
    Serial.println("PONG");
  } 
  
  // LED:status,bright,r,g,b
  else if (msg.startsWith("LED:")) {
    String data = msg.substring(4);
    int s = getVal(data, 0);
    int br = getVal(data, 1);
    int r = getVal(data, 2);
    int g = getVal(data, 3);
    int b = getVal(data, 4);

    ring.setBrightness(br);
    if (s == 1) {
      for(int i=0; i<NUM_PIXELS; i++) ring.setPixelColor(i, ring.Color(r, g, b));
    } else {
      for(int i=0; i<NUM_PIXELS; i++) ring.setPixelColor(i, 0);
    }
    ring.show();
    Serial.println("ACK:LED");
  }

  // FAN:speed (0-255) -> MOSFET
  else if (msg.startsWith("FAN:")) {
    int spd = msg.substring(4).toInt();
    ledcWrite(FAN_PIN, spd);
    Serial.println("ACK:FAN");
  }

  // PUMP:speed (0-255) -> Driver Port 0
  else if (msg.startsWith("PUMP:")) {
    int spd = msg.substring(5).toInt();
    myMotorDriver.setDrive(0, 0, spd); 
    Serial.println("ACK:PUMP");
  }

  // MOTOR:speed (0-255) -> Driver Port 1
  else if (msg.startsWith("MOTOR:")) {
    int spd = msg.substring(6).toInt();
    myMotorDriver.setDrive(1, 0, spd); 
    Serial.println("ACK:MOTOR");
  }
}

// Parsing Helper
int getVal(String data, int index) {
  int found = 0;
  int strIndex[] = {0, -1};
  int maxIndex = data.length() - 1;
  for (int i = 0; i <= maxIndex && found <= index; i++) {
    if (data.charAt(i) == ',' || i == maxIndex) {
      found++;
      strIndex[0] = strIndex[1] + 1;
      strIndex[1] = (i == maxIndex) ? i + 1 : i;
    }
  }
  return found > index ? data.substring(strIndex[0], strIndex[1]).toInt() : 0;
}