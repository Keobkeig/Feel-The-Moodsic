#include <Wire.h>
#include <FastLED.h>

#define NUM_LEDS 256    // 16x16 LED matrix
#define DATA_PIN 3     // Pin connected to the data input of the LED matrix
#define MATRIX_WIDTH 16 // Matrix width
#define MATRIX_HEIGHT 16 // Matrix height

CRGB leds[NUM_LEDS];  // Array to hold LED colors

void setup() {
  Serial.begin(9600);

  // Initialize LED matrix
  FastLED.addLeds<WS2812B, DATA_PIN, GRB>(leds, NUM_LEDS);
  FastLED.setBrightness(50);  // Set brightness (0-255)

  delay(2000);  // Wait for 2 seconds before continuing
}

void loop() {
  static int r = 0, g = 0, b = 0;
  if (Serial.available()) {
    String data = Serial.readStringUntil('\n');
    if (data.indexOf(",") != -1) {
      sscanf(data.c_str(), "%d,%d,%d", &r, &g, &b);
    }
  }

  // Apply heavier breathing animation with center darkness
  applyHeavierBreathingAnimation(r, g, b);
  FastLED.show();
  delay(20); // Faster breathing
}

void applyHeavierBreathingAnimation(int red, int green, int blue) {
  static float breathValue = 0.0;
  static float breathDirection = 0.02; // Faster breathing

  // Calculate breathing value using a sine wave
  breathValue += breathDirection;
  if (breathValue > 1.0 || breathValue < 0.0) {
    breathDirection = -breathDirection;
  }

  // Apply heavier breathing effect to RGB values
  int breathingRed = red + (sin(breathValue * PI * 2) * 40); // Larger variation
  int breathingGreen = green + (cos(breathValue * PI * 2) * 40); // Larger variation
  int breathingBlue = blue + (sin(breathValue * PI * 2 + PI / 2) * 40); // Larger variation

  // Clamp RGB values to 0-255 range
  breathingRed = constrain(breathingRed, 0, 255);
  breathingGreen = constrain(breathingGreen, 0, 255);
  breathingBlue = constrain(breathingBlue, 0, 255);

  for (int i = 0; i < NUM_LEDS; i++) {
    // Calculate distance from the center
    int x = i % MATRIX_WIDTH - MATRIX_WIDTH / 2;
    int y = i / MATRIX_WIDTH - MATRIX_HEIGHT / 2;
    float distance = sqrt(x * x + y * y);

    // Calculate darkness factor based on distance
    float darknessFactor = distance / (MATRIX_WIDTH / 2.0);
    if (darknessFactor > 1.0) darknessFactor = 1.0; // Clamp to 1.0

    // Apply darkness and breathing effect to the LED
    leds[i] = CRGB(breathingRed, breathingGreen, breathingBlue);
    leds[i].fadeToBlackBy(darknessFactor * 80); // Adjust darkness intensity
  }
}