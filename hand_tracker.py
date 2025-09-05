import cv2
import mediapipe as mp
import time

# Open default camera
videoCap = cv2.VideoCapture(0)
lastFrameTime = 0

# Hand initialization
handSolution = mp.solutions.hands
hands = handSolution.Hands()

while True:
    # Read image
    success, img = videoCap.read()

    if success:
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Calculate fps
        thisFrameTime = time.time()
        fps = 1 / (thisFrameTime - lastFrameTime)
        lastFrameTime = thisFrameTime

        cv2.putText(img, f'FPS:{int(fps)}', (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

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