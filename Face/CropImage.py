import numpy as np
import cv2
import face_recognition
import os

test_path = '/media/huanbuster/Vision/Python/Parki/Face/test_image/Huan_331.jpg'
data_dir = '/media/huanbuster/Vision/TempFolder'
check = '/media/huanbuster/Vision/Python/Parki/Face/Collect/Huan'
save = '/media/huanbuster/Vision/Python/Parki/Face/CollectCopy/Son'

def GetFaceLocation(OriginImage):
    ListOfLocation = face_recognition.face_locations(OriginImage)
    # There are some image that cant be detected 
    # If face in that image cant be detected then break the function
    if len(ListOfLocation) ==0:
        return (0,)
    else:
        TupleOfLocation = ListOfLocation[0]
        return TupleOfLocation
    

def CropImage(img, location):
    TupleOfLocation = location
    top = TupleOfLocation[0]
    right = TupleOfLocation[1]
    bottom = TupleOfLocation[2]
    left = TupleOfLocation[3]
    list4point = [[left,top], [right,top], [right,bottom], [left,bottom]]
    ArrayOfPoint = np.array(list4point)

    moments = cv2.moments(ArrayOfPoint)
    centerX = int(moments["m10"] / moments["m00"])
    centerY = int(moments["m01"] / moments["m00"])

    newX = centerX - 112
    newY = centerY - 112
    # cv2.circle(img, (newX, newY), 7, (255, 255, 255), -1)
    # cv2.imshow('center',img)
    # cv2.waitKey(0)

    crop = img[newY:newY+224, newX:newX+224]
    # cv2.imshow('crop',crop)
    # cv2.waitKey(0)
    return crop 

def SaveImage(SavePath,Image):
    # Save the image
    cv2.imwrite(SavePath, Image)

# for name in os.listdir(data_dir):
#     sub_dir = data_dir + '/' + name 
#     number_of_image = len(os.listdir(sub_dir))
#     NewSubDir = save + '/' + name 
#     os.mkdir(NewSubDir)
#     ReNumber = 0
#     for index in range(number_of_image):
#         OriginPath = sub_dir + '/' + name + '_{}'.format(index) + '.jpg'
#         img = cv2.imread(OriginPath)
#         CheckImage = GetFaceLocation(img)
#         if CheckImage == (0,):
#             print('Cant process image: {} {}/{}'.format(name, index, number_of_image))
#             continue 
#         else:
#             crop = CropImage(img, CheckImage)
#             SavePath = NewSubDir + '/' + name + '_{}'.format(ReNumber) + '.jpg'
#             SaveImage(SavePath,crop)
#             ReNumber +=1
#             print('Processing: {} {}/{}'.format(name, index, number_of_image))

        



