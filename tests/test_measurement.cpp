#include "measurement.h"
#include <cassert>

int main() {
  assert(sonar::distanceMm(0) == 0);
  assert(sonar::distanceMm(5831) == 1000);
  assert(sonar::distanceMm(10) == 0);
  assert(sonar::distanceMm(25001) == 0);
  assert(sonar::medianReturn(100, 4000, 102) == 102);
  assert(sonar::medianReturn(0, 100, 102) == 101);
  assert(sonar::medianReturn(0, 0, 102) == 0);
  assert(sonar::elapsed(10, UINT32_MAX - 20, 30));
  assert(!sonar::elapsed(10, UINT32_MAX - 20, 32));
  int angle = 15, direction = 1;
  bool reachedHigh = false, reachedLow = false;
  for (int i = 0; i < 150; ++i) {
    const int previous = angle;
    angle = sonar::nextAngle(angle, direction, 15, 165, 3);
    assert(angle >= 15 && angle <= 165 && angle != previous);
    if (angle == 165)
      reachedHigh = true;
    if (angle == 15)
      reachedLow = true;
  }
  assert(reachedHigh && reachedLow);
}
