import argparse
import cv2
import mediapipe as mp
import time
import math
import subprocess
import sys
from pathlib import Path

# allow disabling sends from CLI
parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('--no-send', action='store_true', help='Do not send angles to handSerial (for testing)')
known_args, _ = parser.parse_known_args()
NO_SEND_FLAG = known_args.no_send

# Open default camera
videoCap = cv2.VideoCapture(0)
lastFrameTime = 0.0

# Hand initialization
handSolution = mp.solutions.hands
hands = handSolution.Hands(static_image_mode=False, max_num_hands=2,
                           min_detection_confidence=0.5, min_tracking_confidence=0.5)

# smoothing state
smoothed_angle = None
SMOOTH_ALPHA = 0.2  # EMA smoothing factor, 0..1 (lower = smoother)

# --- Settings for sending to the hand program ---
SEND_TO_HAND = True                     # toggle sending from tracker
HAND_CHANNEL = 0                        # default servo channel to control
HAND_PORT = None                        # if None, handSerial will pick platform default
SEND_INTERVAL = 0.20                    # seconds between sends (rate limit)
SEND_DELTA = 2                          # minimum change in degrees to trigger a send

# Mapping from camera angle to servo angle
IN_MIN, IN_MAX = -90.0, 90.0            # camera-angle expected range (deg)
OUT_MIN, OUT_MAX = 0, 270               # servo range expected by Arduino/sketch

_last_sent_time = 0.0
_last_sent_angle = None

# Locate handSerial.py at repo root (two parents up from Applications/HandTracker)
HAND_SERIAL_PY = Path(__file__).resolve().parents[2] / "handSerial.py"

print("Starting hand tracker (press ESC to quit)")

while True:
    success, img = videoCap.read()
    if not success:
        time.sleep(0.01)
        continue

    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Calculate fps (robust)
    thisFrameTime = time.time()
    if lastFrameTime:
        fps = 1.0 / max(1e-6, (thisFrameTime - lastFrameTime))
    else:
        fps = 0.0
    lastFrameTime = thisFrameTime
    cv2.putText(img, f'FPS:{int(fps)}', (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    recHands = hands.process(imgRGB)

    if recHands.multi_hand_landmarks:
        # multi_hand_landmarks and multi_handedness are aligned by index
        handedness = []
        if recHands.multi_handedness:
            handedness = [h.classification[0].label for h in recHands.multi_handedness]

        for i, hand in enumerate(recHands.multi_hand_landmarks):
            h_img, w_img, _ = img.shape

            # Landmark indices: 0 = wrist, 9 = middle_finger_mcp, 5 = index_finger_mcp, 17 = pinky_mcp
            w = hand.landmark[0]
            m = hand.landmark[9]
            idx = hand.landmark[5]
            pinky = hand.landmark[17]

            # screen coordinates (pixels)
            wx, wy = int(w.x * w_img), int(w.y * h_img)
            mx, my = int(m.x * w_img), int(m.y * h_img)
            ix, iy = int(idx.x * w_img), int(idx.y * h_img)
            px, py = int(pinky.x * w_img), int(pinky.y * h_img)

            # Compute a rotation-like angle using wrist -> middle_mcp vector
            dx = mx - wx
            dy = my - wy
            angle_rad = math.atan2(dy, dx)
            angle_deg = math.degrees(angle_rad)  # -180..180

            # Optional: use index->pinky vector for better roll estimate on some poses
            # alt_dx = px - ix
            # alt_dy = py - iy
            # alt_angle_deg = math.degrees(math.atan2(alt_dy, alt_dx))

            # Normalize sign for handedness to keep consistent direction (optional)
            if i < len(handedness) and handedness[i].lower().startswith('l'):
                angle_deg = -angle_deg

            # Smooth angle (circular-safe smoothing isn't implemented here; this works for small changes)
            if smoothed_angle is None:
                smoothed_angle = angle_deg
            else:
                smoothed_angle = SMOOTH_ALPHA * angle_deg + (1 - SMOOTH_ALPHA) * smoothed_angle

            # Draw reference points and line
            cv2.circle(img, (wx, wy), 6, (0, 255, 255), cv2.FILLED)
            cv2.circle(img, (mx, my), 6, (255, 0, 255), cv2.FILLED)
            cv2.line(img, (wx, wy), (mx, my), (200, 200, 0), 2)

            # Display angles
            cv2.putText(img, f'Raw:{int(angle_deg)}d', (wx + 10, wy - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,0), 2)
            cv2.putText(img, f'Sm:{int(smoothed_angle)}d', (wx + 10, wy + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

            # Print the smoothed angle to stdout (one line per detected hand)
            # Format: ANGLE <hand_index> <degrees>
            print(f"ANGLE {i} {smoothed_angle:.2f}")

            # Map smoothed camera-space angle to servo angle and send via handSerial.py
            def map_range(x, in_min, in_max, out_min, out_max):
                # clamp x first
                if x < in_min: x = in_min
                if x > in_max: x = in_max
                return (x - in_min) / (in_max - in_min) * (out_max - out_min) + out_min

            def try_send_to_hand(angle_deg: float):
                global _last_sent_time, _last_sent_angle
                now = time.time()
                if now - _last_sent_time < SEND_INTERVAL:
                    return
                if _last_sent_angle is not None and abs(angle_deg - _last_sent_angle) < SEND_DELTA:
                    return

                # map
                servo_val = int(round(map_range(angle_deg, IN_MIN, IN_MAX, OUT_MIN, OUT_MAX)))

                # build args
                args = [sys.executable, str(HAND_SERIAL_PY), "--channel", str(HAND_CHANNEL), "--angle", str(servo_val)]
                if HAND_PORT:
                    args += ["--port", str(HAND_PORT)]

                # start subprocess (non-blocking). It will open serial, send the command and exit.
                try:
                    subprocess.Popen(args)
                    _last_sent_time = now
                    _last_sent_angle = angle_deg
                    print(f"SENT {servo_val} (servo) from camera angle {angle_deg:.2f}")
                except Exception as e:
                    print(f"ERROR launching handSerial: {e}", file=sys.stderr)

            if SEND_TO_HAND:
                try_send_to_hand(smoothed_angle)

            # Draw all landmarks for clarity
            for datapoint_id, point in enumerate(hand.landmark):
                x, y = int(point.x * w_img), int(point.y * h_img)
                cv2.circle(img, (x, y), 4, (150, 50, 200), cv2.FILLED)

    cv2.imshow("CamOutput", img)
    key = cv2.waitKey(1) & 0xFF
    if key == 27:  # ESC
        break

videoCap.release()
cv2.destroyAllWindows()