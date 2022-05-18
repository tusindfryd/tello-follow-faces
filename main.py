from dis import dis
from math import dist
import sys
from djitellopy import Tello
import cv2
from time import sleep

drone = Tello()
drone.connect()
drone.streamon()

VIDEO_URL = drone.get_udp_video_address()

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

counter = 1
faces = []
print(f'Battery: {drone.get_battery()}')
drone.takeoff()
drone.move_up(80)

# while True:
#     height = int(drone.send_read_command('height?')[:-2]) * 10
#     if height <= 120:
#         drone.move_up(20)
#         sleep(1)
#     else:
#         break

# drone.rotate_clockwise(360)

capture = cv2.VideoCapture(VIDEO_URL)
capture.open(VIDEO_URL)
frame_width, frame_height = capture.get(3), capture.get(4)

while True:
    grabbed, frame = capture.read()
    if grabbed:
        if counter % 10 == 0:
            if len(faces) > 0:
                face = sorted(faces, key=lambda face: face[2] * face[3])[-1]
                for (x, y, w, h) in [face]:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)

        if counter % 100 == 0:
            if len(faces) > 0:
                distance_horizontal = (frame_width / 2) - ((x + w) / 2)
                if abs(distance_horizontal) > 30:
                    if distance_horizontal > 0:
                        drone.move_right(20)
                    elif distance_horizontal < 0:
                        drone.move_left(20)
                print(distance_horizontal)
                counter = 1
        else:
            counter = counter + 1

            # print(f'Frame: {frame_width}, {frame_height}, x: {x}, y: {y}')

            # if distance_horizontal - frame_width / 2 > 20:
            #     drone.move_right(20)
            # elif distance_horizontal - frame_width / 2 < 20:
            #     drone.move_left(20)
            # drone.land()
            # break

        cv2.imshow('tello', frame)
    if cv2.waitKey(1) != -1:
        break

capture.release()
cv2.destroyAllWindows()
