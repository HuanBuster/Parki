from mysql.connector import MySQLConnection, Error
from python_mysql_dbconfig import read_db_config
import os 
from ShortestPath import DeleteLPFromParking

import numpy as np
import cv2
import face_recognition

import tensorflow as tf
from tensorflow import keras
import matplotlib.pylab as plt

from CropImage import GetFaceLocation, CropImage
import keyboard

IMG_HEIGHT = 224
IMG_WIDTH = 224
IMG_SHAPE = (IMG_HEIGHT, IMG_WIDTH, 3)
IMAGE_SIZE=(224,224)
BATCH_SIZE = 32
font = cv2.FONT_HERSHEY_SIMPLEX

test_path = '/media/huanbuster/Vision/Python/Parki/Face/test_image/Huan_331.jpg'
data_dir = '/media/huanbuster/Vision/Python/Parki/Face/Collect'

def GetCustomerId(SyntaxQueryName):
    dbconfig = read_db_config()
    conn = MySQLConnection(**dbconfig)
    cursor = conn.cursor()

    QueryStat = "SELECT customer_id FROM customer WHERE first_name LIKE {} ".format(SyntaxQueryName)
    cursor.execute(QueryStat)
    # the result is a tuple which have one value 
    TupleResult = cursor.fetchall()
    CustomerId = TupleResult[0]  
    # only_name = first_name[0].split()
    # name_from_database = only_name[-1]
    # print('name is:',only_name[-1])
    # print('Database: ', type(only_name))
    # print(name[0].split())
    cursor.close()
    conn.close()
    return CustomerId

def UserLogOutSession(CustomerId):
    dbconfig = read_db_config()
    conn = MySQLConnection(**dbconfig)
    cursor = conn.cursor()

    query = "DELETE FROM vehicle WHERE customer_id = %s"
    value = (CustomerId, )
    cursor.execute(query, value)
    conn.commit()
    CaptureMes = 'UnRegister successful'
    cv2.putText(frame, CaptureMes, (200,200), font, 1, (0,0,255), 2, cv2.LINE_4)
    cursor.close()
    conn.close()

def GetNameFromLP(VehicleNumber):
    dbconfig = read_db_config()
    conn = MySQLConnection(**dbconfig)
    cursor = conn.cursor()
    
    QueryStat = "SELECT first_name FROM vehicle JOIN customer on vehicle.customer_id = customer.customer_id where vehicle_number = {} ".format(VehicleNumber)
    cursor.execute(QueryStat)
    # the result is a tuple which have one value 
    TupleResult = cursor.fetchall()
    CustomerFirstName = TupleResult[0]
    SplitFirstName = CustomerFirstName[0].split()
    cursor.close()
    conn.close()
    return SplitFirstName[-1]

InputNumber = input("Enter the Licence: ")

# Create video stream 
cap = cv2.VideoCapture(1)
cap.set(3, 640)
cap.set(3, 480)
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
# Performing predition 
while(cap.isOpened()):
    ret, frame = cap.read()
    Convert2RGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    DetectFace = GetFaceLocation(Convert2RGB)
    if DetectFace == (0,):
        ErrorMes = 'Can not detect face'
        cv2.putText(frame, ErrorMes, (100,100), font, 1, (0,0,255), 2, cv2.LINE_4 )
        continue
    else:
        Cropped = CropImage(Convert2RGB,DetectFace)
        ConvertPixel = Cropped / 255.0
        ArrayImage = (np.expand_dims(ConvertPixel,0))
        prediction = probability_model.predict(ArrayImage)
        result = np.argmax(prediction)
        result_name = [str(Class_names[result])]
        NameFromRecognize = result_name[0]
        TrustPercent = "{}: {:.2f}%".format(NameFromRecognize, prediction[0,0] * 100)
        # for top, right, bottom, left in DetectFace:
        #     cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        if keyboard.is_pressed('c'):
            PredictLicencePlate  = '\'' + InputNumber + '\''
            NameFromDB = GetNameFromLP(PredictLicencePlate)
            if NameFromDB == NameFromRecognize:
                print('The same person')
                ConditionQuery = '\'' + '%' + NameFromRecognize + '\''
                TupleId = GetCustomerId(ConditionQuery)
                Id = TupleId[0]
                UserLogOutSession(Id)
                DeleteLPFromParking(InputNumber)
            else:
                print('Different person')
        cv2.putText(frame, TrustPercent, (50,50), font, 1, (0,0,255), 2, cv2.LINE_4)
        cv2.imshow('Face',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
