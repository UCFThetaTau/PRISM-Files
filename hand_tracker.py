import cv2
import mediapipe as mp

handSolution = mp.solutions.hands
hands = handSolution.Hands()

# Open default camera
videoCap = cv2.VideoCapture(0)

while True:
    # Read image
    success, img = videoCap.read()

    if not success:
        break

    # Recognize hands
    recHands = hands.process(img)

    if recHands.multi_hand_landmarks:
        for hand in recHands.multi_hand_landmarks:
            # Draw dots on points
            for datapoint_id, point in enumerate(hand.landmark):
                h, w, c = img.shape
                x, y = int(point.x * w), int(point.y * h)
                cv2.circle(img, (x, y), 10, (255, 0, 255), cv2.FILLED)
    cv2.imshow("CamOutput", img)
    cv2.waitKey(1)