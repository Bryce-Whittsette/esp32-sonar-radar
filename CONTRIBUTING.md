# Contributing

Thanks for helping improve the ESP32 sonar radar.

## Development checks

Install PlatformIO and use Python 3.10 or newer.

```sh
pio run
c++ -std=c++11 -Wall -Wextra -Werror -Iinclude tests/test_measurement.cpp -o /tmp/sonar-tests
/tmp/sonar-tests
python -m unittest discover -s tests -v
```

The desktop viewer can be exercised without hardware:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r viewer/requirements.txt
python viewer/radar.py --demo
```

## Hardware changes

Document the exact ESP32 board, sensor, servo, power arrangement, wiring, and calibration used. Keep 5 V signals away from ESP32 GPIO and use a common ground. Do not describe commanded servo angles or uncalibrated ultrasonic readings as measured accuracy.

## Pull requests

Keep firmware, protocol, and viewer changes compatible when possible. Add tests for protocol parsing or measurement logic, run the checks above, update user-facing documentation, and add a concise entry under **Unreleased** in `CHANGELOG.md`. Include bench-test evidence when a claim depends on physical hardware.
