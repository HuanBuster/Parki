import yaml
import cv2
import numpy as np 
import logging

COLOR_BLACK = (0, 0, 0)
COLOR_BLUE = (0, 0, 255)
COLOR_GREEN = (0, 255, 0)
COLOR_RED = (255, 0, 0)
COLOR_WHITE = (255, 255, 255)

LAPLACIAN = 1.5
DETECT_DELAY = 1
start_frame = 1

output_path = "/media/huanbuster/Vision/Python/Parki/Parking/Parking-Lot-Detection-Using-OpenCV/data/coordinates_2.yml"
image_path = "/media/huanbuster/Vision/Python/Parki/Parking/Parking-Lot-Detection-Using-OpenCV/images/prototype1.png"
text = 'Test motion detection'

contours = []
bounds = []
mask = []
data = open(output_path,"r")
coordinates_data = yaml.load(data)

def draw_contours(image,
                  points,
                  label,
                  font_color,
                  border_color=COLOR_RED,
                  line_thickness=1,
                  font=cv2.FONT_HERSHEY_SIMPLEX,
                  font_scale=0.5):
    cv2.drawContours(image,
                         [points],
                         contourIdx=-1,
                         color=border_color,
                         thickness=2,
                         lineType=cv2.LINE_8)

    ## Find the center of the rectangle 
    moments = cv2.moments(coor)
    centerX = int(moments["m10"] / moments["m00"])
    centerY = int(moments["m01"] / moments["m00"])
    ## The center of the circle 
    center = (centerX - 20, centerY - 20)
    cv2.circle(img, (centerX, centerY), 7, (255, 255, 255), -1)
    cv2.putText(img, 
                label, 
                center, 
                font, 
                font_scale, 
                font_color, 
                line_thickness, 
                lineType=cv2.LINE_AA)



location_of_lot = coordinates_data[2]
coordinates = np.array(location_of_lot["coordinates"])
print("coordinates: \n", coordinates)
rect = cv2.boundingRect(coordinates)
new_coordinates = coordinates.copy()
new_coordinates[:, 0] = coordinates[:, 0] - rect[0]
new_coordinates[:, 1] = coordinates[:, 1] - rect[1]
print("New: \n", new_coordinates)

contours.append(coordinates)
bounds.append(rect)

mask1 = cv2.drawContours(np.zeros((rect[3], rect[2]), dtype=np.uint16),
                        [new_coordinates],contourIdx = -1, color = 255, thickness=-1,
                        lineType=cv2.LINE_8)

mask1 = mask1 == 255
mask.append(mask1)

statuses = [False]*len(coordinates_data)
times = [None]*len(coordinates_data)


cv2.namedWindow(text, cv2.WINDOW_GUI_EXPANDED)
im = cv2.imread(image_path)
blurred = cv2.GaussianBlur(im.copy(), (5,5), 3)
cv2.imshow(text, blurred)
cv2.waitKey(0)
grayed = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
cv2.imshow(text, grayed)
cv2.waitKey(0)
roi_gray = grayed[rect[1]:(rect[1] + rect[3]), rect[0]:(rect[0] + rect[2])]
cv2.imshow(text, roi_gray)
cv2.waitKey(0)
rect = bounds[0]
lap = cv2.Laplacian(roi_gray, cv2.CV_64F)
cv2.imshow(text, lap)
cv2.waitKey(0)

coordinates[:, 0] = coordinates[:, 0] - rect[0]
coordinates[:, 1] = coordinates[:, 1] - rect[1]
print("Coordinates: \n", coordinates)

mean = np.mean(np.abs(lap * mask[0]))
status = np.mean(np.abs(lap * mask[0])) < LAPLACIAN
print("Mean: ", mean)
print("Status: \n", status)