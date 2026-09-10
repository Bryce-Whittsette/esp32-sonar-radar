#include "config.h"
#include "measurement.h"
#include <Arduino.h>
#include <esp_arduino_version.h>

namespace {
int angle = config::sweepEnabled ? config::minAngle : 90;
int direction = 1;
uint32_t movedAt = 0;
uint32_t sampledAt = 0;
uint32_t sequence = 0;
uint16_t samples[3] = {};
unsigned int sampleCount = 0;
bool ready = false;

void moveServo(int degrees) {
  const uint32_t pulseUs =
      config::servoMinUs + (config::servoMaxUs - config::servoMinUs) *
                               static_cast<uint32_t>(degrees) / 180UL;
  const uint32_t duty =
      pulseUs * ((1UL << config::pwmBits) - 1) / (1000000UL / config::pwmHz);
#if ESP_ARDUINO_VERSION_MAJOR >= 3
  ledcWrite(config::servoPin, duty);
#else
  ledcWrite(0, duty);
#endif
}

uint16_t measure() {
  digitalWrite(config::triggerPin, LOW);
  delayMicroseconds(2);
  digitalWrite(config::triggerPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(config::triggerPin, LOW);
  return sonar::distanceMm(
      pulseIn(config::echoPin, HIGH, config::echoTimeoutUs));
}
} // namespace

void setup() {
  Serial.begin(115200);
  pinMode(config::triggerPin, OUTPUT);
  digitalWrite(config::triggerPin, LOW);
  pinMode(config::echoPin, INPUT);
  if (config::sweepEnabled) {
#if ESP_ARDUINO_VERSION_MAJOR >= 3
    if (!ledcAttach(config::servoPin, config::pwmHz, config::pwmBits)) {
      Serial.println("# error: servo PWM initialization failed");
      return;
    }
#else
    if (ledcSetup(0, config::pwmHz, config::pwmBits) == 0) {
      Serial.println("# error: servo PWM initialization failed");
      return;
    }
    ledcAttachPin(config::servoPin, 0);
#endif
    moveServo(angle);
  }
  Serial.println("# sonar-v1: sequence,angle_deg,distance_mm,status");
  movedAt = sampledAt = millis();
  ready = true;
}

void loop() {
  if (!ready) {
    delay(20);
    return;
  }
  const uint32_t now = millis();
  if (!sonar::elapsed(now, movedAt, config::settleMs) ||
      !sonar::elapsed(now, sampledAt, config::sampleIntervalMs)) {
    delay(1);
    return;
  }
  sampledAt = now;
  samples[sampleCount++] = measure();
  if (sampleCount != 3)
    return;
  const uint16_t distance =
      sonar::medianReturn(samples[0], samples[1], samples[2]);
  Serial.printf("v1,%lu,%d,%u,%s\n", static_cast<unsigned long>(sequence++),
                angle, static_cast<unsigned int>(distance),
                distance ? "ok" : "no_return");
  sampleCount = 0;
  if (config::sweepEnabled) {
    angle = sonar::nextAngle(angle, direction, config::minAngle,
                             config::maxAngle, config::angleStep);
    moveServo(angle);
  }
  movedAt = millis();
}
