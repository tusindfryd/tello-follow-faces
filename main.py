from djitellopy import Tello
import cv2

drone = Tello()
drone.connect()
drone.streamon()

VIDEO_URL = drone.get_udp_video_address()

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')


capture = cv2.VideoCapture(VIDEO_URL)
capture.open(VIDEO_URL)

counter = 1
faces = []
print(f'Battery: {drone.get_battery()}')

while True:
    grabbed, frame = capture.read()
    if grabbed:
        if counter % 10 == 0:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            counter = 1
        else:
            counter = counter + 1
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        cv2.imshow('tello', frame)
    if cv2.waitKey(1) != -1:
        break

capture.release()
cv2.destroyAllWindows()
