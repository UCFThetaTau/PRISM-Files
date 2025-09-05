import cv2
import mediapipe as mp

# Open default camera
videoCap = cv2.VideoCapture(0)

# Read image
success, img = videoCap.read()

if success:
    cv2.imshow("CamOutput", img)
    cv2.waitKey(1000)