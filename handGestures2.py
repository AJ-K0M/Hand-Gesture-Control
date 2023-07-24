import cv2
import mediapipe as mp
from djitellopy import Tello

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(model_complexity=0, min_detection_confidence=0.5, min_tracking_confidence=0.5, max_num_hands=1)
cap = cv2.VideoCapture(0)
width = 720
height = 280
cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
tello = Tello()
tello.connect()
tello.streamoff()
tello.streamon()
isDroneFlying = False

def droneGestureController(image):
    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image)
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    if results.multi_hand_landmarks:

        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                                      mp_drawing_styles.get_default_hand_landmarks_style(),
                                      mp_drawing_styles.get_default_hand_connections_style())
            handlms = []

            c = 0
            for i in hand_landmarks.landmark:
                height, width, fc = image.shape
                x = int(i.x * width)
                y = int(i.y * height)
                handlms.append([c, x, y])
                c = c + 1
            totalFingers = 0

            if len(handlms) != 0:
                fingerTips = [8, 12, 16, 20]
                if handlms[4][1] > handlms[3][1]:
                    totalFingers += 1

                for i in fingerTips:
                    if handlms[i][2] < handlms[i - 2][2]:
                        totalFingers += 1

            droneAction = ""

            if totalFingers == 0:
                droneAction = "Land"
                tello.land()

            elif totalFingers == 1:
                droneAction = "Move forward"
                tello.send_rc_control(0, 20, 0, 0)

            elif totalFingers == 2:
                droneAction = "Move backward"
                tello.send_rc_control(0, -20, 0, 0)

            elif totalFingers == 3:
                droneAction = "Left"
                tello.send_rc_control(-20, 0, 0, 0)

            elif totalFingers == 4:
                droneAction = "Right"
                tello.send_rc_control(20, 0, 0, 0)

            elif totalFingers == 5:
                droneAction = "Takeoff"
                tello.takeoff()
                tello.send_rc_control(0, 0, 25, 0)

            else:
                droneAction = "No Action"

            cv2.putText(image, droneAction + " " + str(totalFingers), (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (255, 0, 0), 2, cv2.LINE_AA)
            return [image, handlms]
        return [image, [0]]
    return [image, [0]]


while True:
    try:
        success, image = cap.read()
        droneImage = tello.get_frame_read().frame
        droneImage = cv2.resize(droneImage, (360, 240))
        image = droneGestureController(image)[0]
        isDroneFlying = True
        cv2.imshow('YourPC', image)
        cv2.imshow('Drone', droneImage)
        k = cv2.waitKey(1) & 0xFF
        if k == ord('q'):
            cv2.destroyAllWindows()
            break
    except:
        continue

cap.release()
tello.streamoff()
tello.disconnect()
