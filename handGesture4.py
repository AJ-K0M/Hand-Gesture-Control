import cv2
import mediapipe as mp
from djitellopy import Tello
import time

# Initialize Mediapipe hands module
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(model_complexity=0, min_detection_confidence=0.5, min_tracking_confidence=0.5, max_num_hands=1)

# Initialize Tello drone
tello = Tello()
tello.connect()
tello.streamon()
tello.takeoff()
tello.send_rc_control(0, 0, 0, 0)

time.sleep(4)

# Initialize OpenCV video capture for Tello stream
cap = cv2.VideoCapture('udp://0.0.0.0:11111')

# Direction mapping
direction_mapping = {
    "Right": "right",
    "Left": "left",
    "Forward": "forward",
    "Backward": "backward",
}

while True:
    # Read frame from Tello video stream
    ret, frame = cap.read()

    if ret:
        # Convert the frame to RGB for Mediapipe
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the frame with Mediapipe hands
        results = hands.process(frame_rgb)

        # Initialize direction as "No Direction"
        direction = "No Direction"

        # Check if hands are detected
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Get the landmarks for the hand
                for landmark in hand_landmarks.landmark:
                    # Extract the x, y coordinates of the landmarks
                    x, y = int(landmark.x * frame.shape[1]), int(landmark.y * frame.shape[0])

                    # Draw a circle at each landmark point
                    cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)

                # Calculate the horizontal and vertical differences between thumb and index/middle fingers
                thumb_x = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x
                thumb_y = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].y
                index_x = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x
                index_y = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y
                middle_x = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].x
                middle_y = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y

                horizontal_diff = thumb_x - index_x
                vertical_diff = thumb_y - (index_y + middle_y) / 2

                # Determine the direction based on the differences
                if abs(horizontal_diff) > abs(vertical_diff):
                    if horizontal_diff > 0:
                        direction = "Right"
                        tello.send_rc_control(30, 0, 0, 0)
                    else:
                        direction = "Left"
                        tello.send_rc_control(30, 0, 0, 0)
                else:
                    if vertical_diff < 0:
                        direction = "Forward"
                        tello.send_rc_control(0, 30, 0, 0)
                    else:
                        direction = "Backward"
                        tello.send_rc_control(0, -30, 0, 0)
                   
                        

       

        # Display the frame with direction
        cv2.putText(frame, f"Direction: {direction_mapping.get(direction, 'No Direction')}", (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.imshow("Hand Gestures", frame)

    # Break the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        tello.land()
        break

# Land the Tello drone and release resources
tello.streamoff()
tello.disconnect()
cap.release()
cv2.destroyAllWindows()
