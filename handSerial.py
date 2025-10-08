# pip install pyserial
import time, serial

PORT = "COM5"         # Windows: COM5, COM3, ...
# PORT = "/dev/ttyACM0"  # Linux
# PORT = "/dev/ttyUSB0"  # some boards on Linux
# PORT = "/dev/cu.usbmodem2101"  # macOS (varies)

BAUD = 115200

with serial.Serial(PORT, BAUD, timeout=1) as ser:
    time.sleep(2)                 # give the Arduino time to reset
    ser.reset_input_buffer()      # clear boot messages

    def send(line: str):
        print(">>", line)
        ser.write((line + "\n").encode("utf-8"))
        # read back any response lines (optional)
        time.sleep(0.02)
        while ser.in_waiting:
            print(ser.readline().decode(errors="ignore").rstrip())

    # examples that match your sketch:
    send("c 0")      # select channel 0
    send("s 45")     # set speed 45 deg/s
    send("a 135")    # ramp to 135°
    time.sleep(1.5)
    send("0 270")    # channel 0 → 270°

