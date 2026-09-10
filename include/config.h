#pragma once

// Classic ESP32 DevKit/WROOM pin assignment; review before wiring another
// board.
namespace config {
constexpr int triggerPin = 18;
constexpr int echoPin = 19; // HC-SR04 Echo must pass through a voltage divider.
constexpr int servoPin = 23;
constexpr bool sweepEnabled = true;
constexpr int minAngle = 15;
constexpr int maxAngle = 165;
constexpr int angleStep = 3;
constexpr unsigned long sampleIntervalMs = 65;
constexpr unsigned long settleMs = 100;
constexpr unsigned long echoTimeoutUs = 25000;
constexpr unsigned int servoMinUs = 1000;
constexpr unsigned int servoMaxUs = 2000;
constexpr unsigned int pwmHz = 50;
constexpr unsigned int pwmBits = 16;
static_assert(minAngle >= 0 && maxAngle <= 180 && minAngle < maxAngle,
              "Invalid sweep limits");
static_assert(angleStep > 0 && angleStep <= maxAngle - minAngle,
              "Invalid sweep step");
static_assert(triggerPin != echoPin && triggerPin != servoPin &&
                  echoPin != servoPin,
              "Pins must be distinct");
} // namespace config
