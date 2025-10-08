"""Simple serial helper for the hand Arduino sketch.

Usage:
  - Interactive demo (no args): runs the example sequence.
  - Send a single command from the CLI, e.g.:
      python handSerial.py --channel 0 --angle 135 --port /dev/ttyACM0
  - Or specify --speed, --baud etc.
"""

import time
import argparse
import serial
import sys

def open_serial(port: str, baud: int):
    try:
        ser = serial.Serial(port, baud, timeout=1)
        time.sleep(2)
        ser.reset_input_buffer()
        return ser
    except Exception as e:
        print(f"ERROR: cannot open serial {port}: {e}", file=sys.stderr)
        return None

def send_line(ser, line: str):
    print(">>", line)
    ser.write((line + "\n").encode("utf-8"))
    time.sleep(0.02)
    # read back any response lines (optional)
    out = []
    while ser.in_waiting:
        out.append(ser.readline().decode(errors="ignore").rstrip())
    for l in out:
        print(l)

def interactive_demo(port, baud):
    ser = open_serial(port, baud)
    if not ser:
        return 2
    try:
        send_line(ser, "c 0")      # select channel 0
        send_line(ser, "s 45")     # set speed 45 deg/s
        send_line(ser, "a 135")    # ramp to 135°
        time.sleep(1.5)
        send_line(ser, "0 270")    # channel 0 → 270°
    finally:
        ser.close()
    return 0

def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--port", default=None, help="Serial port (e.g. /dev/ttyACM0 or COM3)")
    p.add_argument("--baud", type=int, default=115200)
    p.add_argument("--channel", type=int, help="Channel 0..15 to target")
    p.add_argument("--angle", type=float, help="Angle to send (0..SERVO_MAX_DEG)")
    p.add_argument("--speed", type=float, help="Speed in deg/sec")
    args = p.parse_args(argv)

    # Resolve default port if not provided
    port = args.port
    if port is None:
        import platform
        if platform.system() == "Windows":
            port = "COM5"
        elif platform.system() == "Darwin":
            port = "/dev/cu.usbmodem2101"
        else:
            port = "/dev/ttyACM0"

    # If no actionable args, run the demo
    if args.channel is None and args.angle is None and args.speed is None:
        return interactive_demo(port, args.baud)

    ser = open_serial(port, args.baud)
    if not ser:
        return 2
    try:
        if args.channel is not None and args.angle is not None:
            # send '<ch> <angle>' form
            send_line(ser, f"{args.channel} {int(args.angle)}")
        else:
            if args.channel is not None:
                # set current channel
                send_line(ser, f"c {args.channel}")
            if args.speed is not None:
                send_line(ser, f"s {int(args.speed)}")
            if args.angle is not None:
                # send in 'a <angle>' form (applies to current channel)
                send_line(ser, f"a {int(args.angle)}")
    finally:
        ser.close()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

