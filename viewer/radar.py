"""Desktop serial plotter. Use --demo for deterministic synthetic measurements."""

import argparse
import math
import queue
import threading
import time
import tkinter as tk
from tkinter import ttk

from protocol import Reading, parse_line


class Radar:
    def __init__(self, root, port=None, demo=False, csv_path=None):
        self.root = root
        self.demo = demo
        self.port = port
        self.stop = threading.Event()
        self.events = queue.Queue(maxsize=256)
        self.points = {}
        self.latest = None
        self.last_received = 0.0
        self.demo_sequence = 0
        self.demo_angle = 15
        self.demo_direction = 1
        # The recording file stays open until the window closes.
        self.csv = open(csv_path, "x", encoding="utf-8") if csv_path else None  # noqa: SIM115
        if self.csv:
            self.csv.write("received_unix,sequence,angle_deg,distance_mm,status\n")
        root.title("Sonar / ESP32")
        root.geometry("960x650")
        root.minsize(640, 460)
        top = ttk.Frame(root, padding=20)
        top.pack(fill="x")
        ttk.Label(top, text="SONAR / ESP32", font=("Helvetica", 18, "bold")).pack(
            side="left"
        )
        ttk.Label(top, text="DEMO · synthetic data" if demo else port).pack(
            side="right"
        )
        self.canvas = tk.Canvas(root, background="#111e25", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=20)
        self.status = tk.StringVar(value="Waiting for measurements…")
        ttk.Label(root, textvariable=self.status, padding=20).pack(fill="x")
        self.canvas.bind("<Configure>", lambda event: self.draw())
        root.protocol("WM_DELETE_WINDOW", self.close)
        if port:
            threading.Thread(target=self.read_serial, daemon=True).start()
        root.after(50, self.tick)

    def enqueue(self, event):
        try:
            self.events.put_nowait(event)
        except queue.Full:
            pass  # Keep memory bounded if rendering falls behind.

    def read_serial(self):
        try:
            import serial

            with serial.Serial(self.port, 115200, timeout=0.5) as connection:
                pending = bytearray()
                discarding = False
                while not self.stop.is_set():
                    chunk = connection.read(128)
                    for value in chunk:
                        if value == 10:
                            if not discarding:
                                reading = parse_line(
                                    pending.decode("ascii", errors="replace")
                                )
                                if reading:
                                    self.enqueue(reading)
                            pending.clear()
                            discarding = False
                        elif not discarding:
                            pending.append(value)
                            if len(pending) > 128:
                                pending.clear()
                                discarding = True
        except (ImportError, OSError, ValueError) as error:
            self.enqueue(f"Serial connection stopped: {error}")

    def tick(self):
        if self.stop.is_set():
            return
        if self.demo:
            angle = self.demo_angle
            distance = (
                int(1450 + 200 * math.sin(math.radians(angle * 3)))
                if 40 <= angle <= 135
                else 0
            )
            self.enqueue(
                Reading(
                    self.demo_sequence,
                    angle,
                    distance,
                    "ok" if distance else "no_return",
                )
            )
            self.demo_sequence += 1
            if angle >= 165:
                self.demo_direction = -1
            if angle <= 15:
                self.demo_direction = 1
            self.demo_angle += self.demo_direction * 3
        while True:
            try:
                event = self.events.get_nowait()
            except queue.Empty:
                break
            if isinstance(event, str):
                self.status.set(event)
                self.last_received = 0
                continue
            self.latest = event
            self.last_received = time.monotonic()
            if event.status == "ok":
                self.points[event.angle] = (event.distance_mm, self.last_received)
            else:
                self.points.pop(event.angle, None)
            distance = (
                f"{event.distance_mm / 10:.1f} cm"
                if event.status == "ok"
                else "No return"
            )
            self.status.set(
                f"{event.angle}°   ·   {distance}   ·   Sample {event.sequence}   ·   Range 4 m"
            )
            if self.csv:
                self.csv.write(
                    f"{time.time():.3f},{event.sequence},{event.angle},{event.distance_mm},{event.status}\n"
                )
                self.csv.flush()
        if self.last_received and time.monotonic() - self.last_received > 3:
            self.status.set("No recent data. Check the USB connection and firmware.")
        self.draw()
        self.root.after(65 if self.demo else 50, self.tick)

    def draw(self):
        canvas = self.canvas
        canvas.delete("all")
        width, height = canvas.winfo_width(), canvas.winfo_height()
        cx, cy = width / 2, height - 40
        radius = max(1, min(width / 2 - 45, height - 65))
        for fraction in (0.25, 0.5, 0.75, 1):
            r = radius * fraction
            canvas.create_arc(
                cx - r,
                cy - r,
                cx + r,
                cy + r,
                start=0,
                extent=180,
                style="arc",
                outline="#38505c",
            )
            canvas.create_text(
                cx + 8,
                cy - r + 12,
                text=f"{4 * fraction:g} m",
                fill="#a3b4bc",
                anchor="w",
            )
        for angle in range(0, 181, 30):
            radians = math.radians(angle)
            x, y = cx + radius * math.cos(radians), cy - radius * math.sin(radians)
            canvas.create_line(cx, cy, x, y, fill="#29404c")
            canvas.create_text(x, y - 15, text=f"{angle}°", fill="#a3b4bc")
        now = time.monotonic()
        for angle, (distance, received) in list(self.points.items()):
            if now - received > 30:
                del self.points[angle]
                continue
            r = radius * distance / 4000
            radians = math.radians(angle)
            x, y = cx + r * math.cos(radians), cy - r * math.sin(radians)
            color = "#8bc5ab" if now - received < 10 else "#527b6b"
            canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill=color, outline="")
        if self.latest:
            radians = math.radians(self.latest.angle)
            canvas.create_line(
                cx,
                cy,
                cx + radius * math.cos(radians),
                cy - radius * math.sin(radians),
                fill="#cfddd8",
                width=2,
            )
        canvas.create_text(cx, cy + 20, text="SENSOR", fill="#a3b4bc")

    def close(self):
        self.stop.set()
        if self.csv:
            self.csv.close()
        self.root.destroy()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument(
        "--port", help="Serial device, for example /dev/cu.usbserial-0001 or COM3"
    )
    source.add_argument("--demo", action="store_true")
    parser.add_argument(
        "--csv",
        help="Record readings to a new file; refuses to overwrite an existing file",
    )
    args = parser.parse_args()
    root = tk.Tk()
    try:
        Radar(root, args.port, args.demo, args.csv)
        root.mainloop()
    except (OSError, tk.TclError) as error:
        parser.exit(1, f"Viewer failed: {error}\n")


if __name__ == "__main__":
    main()
