import cv2
import numpy as np
import logging

COLOR_BLACK = (0, 0, 0)
COLOR_BLUE = (0, 0, 255)
COLOR_GREEN = (0, 255, 0)
COLOR_RED = (255, 0, 0)
COLOR_WHITE = (255, 255, 255)
KEY_RESET = ord("r")
KEY_QUIT = ord("q")

image_path = "/media/huanbuster/Vision/Python/Parki/Parking/Parking-Lot-Detection-Using-OpenCV/images/prototype1.png"
output_path = "/media/huanbuster/Vision/Python/Parki/Parking/Parking-Lot-Detection-Using-OpenCV/data/coordinates_2.yml"

position1 = [[185,26],[313,26],[315,169],[191,171]]
coor = np.array(position1)
label1 = "1"
WindowName = "Select parking lot"
click = 0
ClickPoints = []
ids = 0

def draw_contours(image,
                  points,
                  label,
                  font_color,
                  border_color=COLOR_RED,
                  line_thickness=1,
                  font=cv2.FONT_HERSHEY_SIMPLEX,
                  font_scale=0.5):
    cv2.drawContours(image,
                         [ClickPoints],
                         contourIdx=-1,
                         color=border_color,
                         thickness=2,
                         lineType=cv2.LINE_8)

    ## Find the center of the rectangle 
    moments = cv2.moments(points)
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

def onMouse(event, x, y, flags, params):
    global click, ids
    if event == cv2.EVENT_LBUTTONDOWN:
        ClickPoints.append((x,y))
        click += 1
        if click >= 4:
            # If user has choose 4 point (a rectangle) then draw 2 lines
            # Finishing a rectangle by drawing 2 last lines
            cv2.line(img, ClickPoints[2], ClickPoints[3], COLOR_RED, 2)
            cv2.line(img, ClickPoints[3], ClickPoints[0], COLOR_RED, 2)
            click = 0
        if click >1:
            # If user has not finished choosing 4 point, then just draw 1 line 
            # Drawing 1 line from 2 last ClickPoints  
            cv2.line(img, ClickPoints[-2], ClickPoints[-1], COLOR_RED, 2)
        #Save list of ClickPoints into array to drawing contours 
        coordinates = np.array(ClickPoints) 
        #Print output points 
        SavedFile.write("-\n          id: " + str(ids) + "\n          coordinates: [" +
                "[" + str(coordinates[0][0]) + "," + str(coordinates[0][1]) + "]," +
                "[" + str(coordinates[1][0]) + "," + str(coordinates[1][1]) + "]," +
                "[" + str(coordinates[2][0]) + "," + str(coordinates[2][1]) + "]," +
                "[" + str(coordinates[3][0]) + "," + str(coordinates[3][1]) + "]]\n")  
        
        draw_contours(img, coordinates, str(ids+1), COLOR_WHITE)
        # Delete list of point when there are 4 points
        for i in range(0,4):
            ClickPoints.pop()

        ids +=1
    cv2.imshow(WindowName,img)


# #Test drawing contours
# draw_contours(img, coor, label1, COLOR_WHITE)
# cv2.imshow(text, img)
# cv2.waitKey(0)
#---------------------------------------
# Open file to save locations 
SavedFile = open(output_path,"w+") 
# Load the image, clone it
img = cv2.imread(image_path).copy()
# Setup the mouse callback function
cv2.namedWindow(WindowName, cv2.WINDOW_GUI_EXPANDED)
cv2.setMouseCallback(WindowName, onMouse)


while True:
    cv2.imshow(text, img)
    key = cv2.waitKey(0)
    if key == KEY_RESET: 
        cloned = img.copy()
    elif key == KEY_QUIT:
        SavedFile.close()
        break
cv2.destroyAllWindows(text)

