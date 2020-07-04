import tkinter as tk
import cv2
from PIL import Image, ImageTk
import numpy as np
import threading
import imutils
from imutils.video import WebcamVideoStream

import tensorflow as tf
from tensorflow import keras
import os

# Create a window
window = tk.Tk()
window.title("Face Input")
window.config(bg='white')

#Graphics window
VideoFrame = tk.Frame(window, width=600, height=480)
VideoFrame.grid(row=1, column=0,columnspan=3, padx=10, pady=2)
DisplayFrame = tk.Label(VideoFrame)
DisplayFrame.grid(row=1, column=0, columnspan=3)

DatabaseStatus = tk.Label(text="Database is ready", fg='orange', bg='white')
DatabaseStatus.grid(row=2, column=2)
RecogResult = tk.Label(text="Name + accuracy", fg='orange', bg='white')
RecogResult.grid(row=2, column=0)
PositionRec = tk.Label(text="Shortest", fg='orange', bg='white')
PositionRec.grid(row=2, column=1)
InputLicence = tk.Entry(fg='black', bg='white')
InputLicence.grid(row=3,column=1)

InstructionText = "Please, align your face in the center of the screen!"
InstructionMessage = tk.Label(text=InstructionText, fg='orange', bg='white')
InstructionMessage.grid(row = 0, column = 0,columnspan=3)
# Functions of Buttons are here:
def ExitFunction():
    global cap
    # cap.stop()
    cap.release()
    window.quit()

RegisterButton = tk.Button(text='Login Parking', fg='white', bg='orange')
RegisterButton.grid(row=3, column=0)
ExitButton = tk.Button(text='Close Program', fg='white', bg='orange', command=ExitFunction)
ExitButton.grid(row=3,column=2)


cap = cv2.VideoCapture(0)
def PrepareModel():
    # Load trained model
    my_model = tf.keras.models.load_model('Output/Recognizer_V6')
    my_model.summary()
    # Get the class name
    folder = [name for name in os.listdir(data_dir) 
            if os.path.isdir(os.path.join(data_dir, name))]
    Class_names = np.array(folder)
    # Adding Softmax layer 
    probability_model = tf.keras.Sequential([my_model, 
                                            tf.keras.layers.Softmax()])
    return Class_names, probability_model

def ProcessAndPredict(frame, probability_model, Class_names):
    frame = cv2.flip(frame, 1)
    Convert2RGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    DetectFace = GetFaceLocation(Convert2RGB)
    if DetectFace == (0,):
        ErrorMes = 'Can not detect face'
        cv2.putText(frame, ErrorMes, (100,100), font, 1, (0,0,255), 2, cv2.LINE_4 )
        return None
    else:
        Cropped = CropImage(Convert2RGB,DetectFace)
        ConvertPixel = Cropped / 255.0
        ArrayImage = (np.expand_dims(ConvertPixel,0))
        prediction = probability_model.predict(ArrayImage)
        result = np.argmax(prediction)
        result_name = [str(Class_names[result])]
        NameFromRecognize = result_name[0]
        TrustPercent = "{}: {:.2f}%".format(NameFromRecognize, prediction[0,0] * 100)
        return NameFromRecognize, TrustPercent

def ShowVideo():
    _,frame = cap.read()

    flip = cv2.flip(frame, 1)
    cv2image = cv2.cvtColor(flip, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(cv2image)

    imgtk = ImageTk.PhotoImage(image=img)
    DisplayFrame.imgtk = imgtk
    DisplayFrame.configure(image=imgtk)
    DisplayFrame.after(1, ShowVideo)
    return frame
while(cap.isOpened()):
    frame = ShowVideo() 
    ClassName, LoadModel = PrepareModel()
    ResultName, ResultPercent = ProcessAndPredict(frame, model, classname)
    RecogResult = tk.Label(text=ResultName + ' ' + ResultPercent, fg='orange', bg='white')
    RecogResult.grid(row=2, column=0)
    window.mainloop()
      