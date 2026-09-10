# ESP32 sonar radar

A servo sweeps an ultrasonic sensor and streams angle/distance readings over USB. The desktop viewer plots those readings on a semicircular scope and can record them to CSV.

This is acoustic ranging, commonly presented as a “radar” project. It does not transmit radio waves. The firmware was developed from an earlier single-sensor Arduino distance sketch.

**Reference configuration:** classic ESP32 DevKit/WROOM, HC-SR04, and a positional hobby servo. The firmware compiles for this target. Physical wiring, servo calibration, and measurement accuracy have not yet been verified on the owner's hardware.

## Hardware

| Connection | Destination |
| --- | --- |
| HC-SR04 Trig | ESP32 GPIO 18 |
| HC-SR04 Echo | 1 kΩ resistor → GPIO 19 junction → 2 kΩ resistor → ground |
| HC-SR04 VCC | 5 V |
| HC-SR04 GND | Common ground |
| Servo signal | ESP32 GPIO 23 |
| Servo power | External regulated supply appropriate for the servo |
| Servo ground | Common ground with sensor, supply, and ESP32 |

The HC-SR04 Echo signal is 5 V; **do not connect it directly to an ESP32 input**. The divider above reduces it to approximately 3.3 V. Do not power the servo from the ESP32's 3.3 V pin. Avoid tying separate 5 V supplies together; share their grounds. Check your board pinout and servo supply requirements before powering it.

`include/config.h` contains the pin assignment, angle limits, pulse range, and timing. Sweep is enabled by default. Set `sweepEnabled = false` for a fixed sensor without a servo; readings are then labeled 90°. GPIO 18/19/23 are reference pins for the classic ESP32, not universal choices for every ESP32 family.

## Build and run

Install [PlatformIO Core](https://docs.platformio.org/en/latest/core/installation/index.html), then:

```sh
pio run
pio run --target upload
pio device monitor --baud 115200
```

The project pins Espressif32 6.12.0. Close the serial monitor before starting the viewer; one program should own the port at a time.

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r viewer/requirements.txt
python viewer/radar.py --demo
python -m serial.tools.list_ports
python viewer/radar.py --port /dev/cu.usbserial-0001
```

Use your actual serial device (`COM3`, for example, on Windows). Python must include Tk support. Python.org desktop distributions usually include it; Linux distributions may package it separately as `python3-tk`.

Add `--csv readings.csv` to record. Existing files are never overwritten. Demo mode uses visibly labeled synthetic measurements and needs no connected board.

## Sampling and protocol

The servo moves between 15° and 165° in 3° increments. Each angle settles before sampling. Three readings are spaced at least 65 ms apart; two valid echoes are required. Three valid echoes produce a median, while two are averaged. Missing or out-of-range echoes produce `no_return`, not a zero-distance obstacle. Echo waits are bounded to 25 ms.

The servo pulse range defaults to 1000 to 2000 µs. Angles are **commanded positions**, not measured positions. Calibrate the pulse range and physical angle before making accuracy claims. A full sweep is intentionally slow because of settling and repeated measurements. Beam width, target material, temperature, and reflections affect distance estimates.

At 115200 baud, each line is:

```text
v1,42,90,1234,ok
v1,43,93,0,no_return
```

Fields: protocol, unsigned sequence, degrees, millimeters, status. Sequence wraps after 2³² samples and restarts on boot. Lines starting with `#` are diagnostics. The viewer ignores boot noise and malformed lines, bounds its queue, removes missing returns, and expires old points after 30 seconds. The plotted 4 m range is a display bound, not a tested accuracy specification.

## Tests

```sh
c++ -std=c++11 -Wall -Wextra -Werror -Iinclude tests/test_measurement.cpp -o /tmp/sonar-tests
/tmp/sonar-tests
python -m unittest discover -s tests -v
```

Tests cover distance conversion, invalid echoes, filtering, sweep bounds, millisecond-counter rollover, and serial validation. GitHub Actions also compiles the firmware. `docs/hardware-check.md` records the remaining bench procedure.

## References

- [HC-SR04 datasheet](https://cdn.sparkfun.com/datasheets/Sensors/Proximity/HCSR04.pdf)
- [Espressif LEDC API](https://docs.espressif.com/projects/arduino-esp32/en/latest/api/ledc.html)
- [PlatformIO ESP32 platform](https://docs.platformio.org/en/latest/platforms/espressif32.html)

MIT licensed.
