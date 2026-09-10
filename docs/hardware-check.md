# Bench verification

Status: not yet performed on physical hardware.

1. Record the exact ESP32 board, sensor revision, servo model, power supply, and pin assignment.
2. With power disconnected, check common ground and the Echo divider. Verify the divider voltage before attaching Echo to the ESP32.
3. Start with sweep disabled. Measure a flat target at 10, 25, 50, and 100 cm; record reference and reported distances with at least ten readings each.
4. Remove the target and confirm `no_return` rather than a near-zero obstacle.
5. Disconnect power, attach the servo on its own suitable supply, and check a conservative sweep with the horn clear of obstructions. Calibrate min/max pulses without driving into mechanical stops.
6. Check USB disconnect/reconnect, serial boot messages, viewer stale-data indication, and CSV recording.
7. Only after these pass, add a real wiring photograph and measured error table to the README. Do not present demo measurements as a hardware result.
