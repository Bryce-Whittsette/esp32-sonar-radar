#pragma once
#include <stdint.h>

namespace sonar {
// Round-trip travel time at approximately 20 C. Zero means no usable return.
inline uint16_t distanceMm(uint32_t pulseUs) {
  if (pulseUs == 0 || pulseUs > 25000)
    return 0;
  const uint32_t mm = (pulseUs * 343UL + 1000UL) / 2000UL;
  return mm >= 20 && mm <= 4000 ? static_cast<uint16_t>(mm) : 0;
}

inline uint16_t medianReturn(uint16_t a, uint16_t b, uint16_t c) {
  // Require a majority of valid echoes; one stray return is not a detection.
  uint16_t values[3] = {a, b, c};
  unsigned int count = 0;
  for (auto value : values)
    if (value != 0)
      values[count++] = value;
  if (count < 2)
    return 0;
  for (unsigned int i = 0; i < count; ++i)
    for (unsigned int j = i + 1; j < count; ++j)
      if (values[j] < values[i]) {
        auto tmp = values[i];
        values[i] = values[j];
        values[j] = tmp;
      }
  return count == 3 ? values[1]
                    : static_cast<uint16_t>((values[0] + values[1]) / 2);
}

inline int nextAngle(int angle, int &direction, int low, int high, int step) {
  int next = angle + direction * step;
  if (next >= high) {
    direction = -1;
    return high;
  }
  if (next <= low) {
    direction = 1;
    return low;
  }
  return next;
}

inline bool elapsed(uint32_t now, uint32_t then, uint32_t interval) {
  return static_cast<uint32_t>(now - then) >= interval;
}
} // namespace sonar
