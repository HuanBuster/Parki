import numpy as np
import cv2
import face_recognition
import os
import keyboard
from CropImage import GetFaceLocation, CropImage, SaveImage
import imutils
from imutils.video import WebcamVideoStream

test = '/media/huanbuster/Vision/TempFolder/Son/Son_0.jpg'
cap = WebcamVideoStream(0).start()
locations = []
directory = '/media/huanbuster/Vision/Python/Parki/Face/CollectCopy'
number = 0
font = cv2.FONT_HERSHEY_SIMPLEX

# Display the input message 
# Get the name of user 
# name = input("Enter your name: ")
name = input("Enter your name: ")
# Make a save path from name
path = os.path.join(directory, name) 
# Create new directory per 1 person
os.mkdir(path) 
key = False
SaveText = ''
WarningText = ''
# frame = cv2.imread(test)
while(cap.grabbed):
    # Capture frame-by-frame
    frame = cap.read()
    Flipped = cv2.flip(frame,1)
    DisplayFrame = Flipped.copy()
    Convert2RGB = cv2.cvtColor(Flipped, cv2.COLOR_BGR2RGB)
    # Find all the faces in the current frame of video
    DetectFace = GetFaceLocation(Convert2RGB)
    # print(DetectFace)
    if keyboard.is_pressed('s'):
        key = True
        print("Key is pressed!")
    # if DetectFace != (0,) and key:
    #     Cropped = CropImage(Convert2RGB,DetectFace)
    #     SavePath = path + '/' + name + '_{}'.format(number) + '.jpg'
    #     # cv2.imwrite(path + '/' + name + '_{}'.format(number) + '.jpg',Cropped)
    #     SaveImage(SavePath,Cropped)
    #     text = "Number: {}".format(number)
    #     number +=1
    #     key = 115
    if DetectFace != (0,):
        # Draw a box around the face
        WarningText = ''
        (top, right, bottom, left) = DetectFace
        cv2.rectangle(DisplayFrame, (left, top), (right, bottom), (0, 0, 255), 2)
        Cropped = CropImage(Flipped,DetectFace)
        if key:
            SavePath = path + '/' + name + '_{}'.format(number) + '.jpg'
            SaveImage(SavePath,Cropped)
            SaveText = "Number: {}".format(number)
            number +=1
            key = 115
    else:
        WarningText = "Can not detect your face"
    # Display the resulting frame
    cv2.putText(DisplayFrame, SaveText, (50,50), font, 1, (0,0,255), 2, cv2.LINE_4)
    cv2.putText(DisplayFrame, WarningText, (150,150), font, 1, (0,0,255), 2, cv2.LINE_4)
    cv2.imshow('Face',DisplayFrame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.stop()
cv2.destroyAllWindows()
