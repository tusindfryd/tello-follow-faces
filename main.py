from djitellopy import Tello
import cv2
from time import sleep
from datetime import datetime
from threading import Thread
import os

flying = True
drone = Tello()
instructions = []


def clear_old_instructions(instructions, timeout=10):
    now = datetime.now()
    return [instruction for instruction in instructions if (now - instruction[1]).seconds < timeout]


def fly():
    global flying
    drone.connect()
    print(f"Battery: {drone.get_battery()}%")
    drone.takeoff()
    drone.move_up(80)
    drone.streamon()
    sleep(3)
    fly_instructions = []
    done_instructions = []
    while flying:
        sleep(0.1)
        if instructions and instructions[-1] not in fly_instructions:
            fly_instructions.append(instructions[-1])
        # print(f"Done: {done_instructions}")
        # print(f"Fly: {done_instructions}")
        for instruction in fly_instructions:
            if instruction not in done_instructions:
                direction = instruction[0]
                match direction:
                    case "right":
                        print("Turning right...")
                        drone.rotate_clockwise(15)
                    case "left":
                        print("Turning left...")
                        drone.rotate_counter_clockwise(15)
                    case "forward":
                        print("Moving forward...")
                        drone.move_forward(20)
                    case "backward":
                        print("Moving backward...")
                        drone.move_back(20)
                sleep(5)
                done_instructions.append(instruction)
        if len(done_instructions) == 3:
            print("3 instructions done - landing...")
            flying = False
            drone.land()
        fly_instructions = clear_old_instructions(fly_instructions)
        done_instructions = clear_old_instructions(done_instructions, 20)


fly_thread = Thread(target=fly, daemon=True)
fly_thread.start()

VIDEO_URL = drone.get_udp_video_address()
face_cascade = cv2.CascadeClassifier("lbpcascade_frontalface_improved.xml")

counter = 1
face = [0, 0, 0, 0]

capture = cv2.VideoCapture(VIDEO_URL)
capture.open(VIDEO_URL)
frame_width, frame_height = capture.get(3), capture.get(4)


try:
    while flying:
        grabbed, frame = capture.read()
        if grabbed:
            if counter % 10 == 0:  # every ten frames: detect faces
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.1, 4)
                if len(faces) > 0:
                    # choose the biggest face
                    face = sorted(
                        faces, key=lambda face: face[2] * face[3])[-1]
                else:
                    face = [0, 0, 0, 0]

            if counter % 100 == 0:  # every hundred frames: move
                if all(face):
                    (x, y, w, h) = face
                    face_size = w * h
                    horizontal_dist = (frame_width / 2) - (x + w / 2)
                    vertical_dist = (frame_height / 2) - (y + h / 2)
                    if face_size < 19000:
                        instructions.append(["forward", datetime.now()])
                    elif face_size > 22000:
                        instructions.append(["backward", datetime.now()])
                    if abs(horizontal_dist) > 30:
                        if horizontal_dist < 0:
                            instructions.append(["right", datetime.now()])
                        elif horizontal_dist > 0:
                            instructions.append(["left", datetime.now()])
                        # print(f"All instructions: {instructions}")
                counter = 1

            else:
                counter = counter + 1

            cv2.circle(frame, (int(frame_width / 2), int(frame_height / 2)),
                       radius=2, color=(0, 255, 0), thickness=1)
            for (x, y, w, h) in [face]:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                cv2.circle(frame, (int(x + w / 2), int(y + h / 2)),
                           radius=2, color=(0, 0, 255), thickness=1)

            cv2.imshow("Tello", frame)
        if cv2.waitKey(1) != -1:
            break
        instructions = clear_old_instructions(instructions)
except KeyboardInterrupt:
    flying = False
    print("Landing...")
    drone.land()
finally:
    capture.release()
    cv2.destroyAllWindows()
    os._exit(0)
