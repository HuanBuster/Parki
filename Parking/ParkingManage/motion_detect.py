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

video_path = "/media/huanbuster/Vision/Python/Parki/Parking/Parking-Lot-Detection-Using-OpenCV/prototype2.mp4"
output_path = "/media/huanbuster/Vision/Python/Parki/Parking/Parking-Lot-Detection-Using-OpenCV/data/coordinates_2.yml"

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
    moments = cv2.moments(coordinates)
    center = (int(moments["m10"] / moments["m00"]) - 3,
              int(moments["m01"] / moments["m00"]) + 3)
    ## The center of the circle 
    # center = (centerX - 20, centerY - 20)
    # cv2.circle(img, (centerX, centerY), 7, (255, 255, 255), -1)
    cv2.putText(image, 
                label, 
                center, 
                font, 
                font_scale, 
                font_color, 
                line_thickness, 
                lineType=cv2.LINE_AA)

capture = cv2.VideoCapture(video_path)
capture.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

def process(p):
    return np.array(p["coordinate"])

# ----- A iteration -------
# Process the yml file
for index, p in enumerate(coordinates_data):
    location_of_lot = coordinates_data[index] 
    coordinates = np.array(location_of_lot["coordinates"])
    print("coordinates: ", coordinates)
    logging.debug("coordinates: %s", coordinates)
    rect = cv2.boundingRect(coordinates)
    # print("rect: ",rect)
    new_coordinates = coordinates.copy()
    new_coordinates[:, 0] = coordinates[:, 0] - rect[0]
    new_coordinates[:, 1] = coordinates[:, 1] - rect[1]
    logging.debug("new_coordinates: %s", new_coordinates)
    # print("New: ", new_coordinates)
    # print(type(new_coordinates))
    contours.append(coordinates)
    bounds.append(rect)
    # print("Contours: ", contours)
    # print("Bounds: ", bounds)
    mask1 = cv2.drawContours(np.zeros((rect[3], rect[2]), dtype=np.uint16),
                            [new_coordinates],contourIdx = -1, color = 255, thickness=-1,
                            lineType=cv2.LINE_8)
    # print(type(mask1))
    # print("Mask: \n",mask1)
    mask1 = mask1 == 255
    # print("New mask: \n",mask1)
    mask.append(mask1)
    # print("Last mask: \n", mask)
# ------ End of A Iteration -------
statuses = [False]*len(coordinates_data)
# print("Statuses: ", statuses)
times = [None]*len(coordinates_data)
# print("Times: ", times)
# Process the video 
while capture.isOpened():
    # Remember to use TAB
    result, frame = capture.read()
    frame = cv2.rotate(frame,cv2.ROTATE_90_CLOCKWISE)
    if frame is None:
        break
    if not result:
        raise CaptureReadError("Error reading video capture on frame %s" % str(frame))
    blurred = cv2.GaussianBlur(frame.copy(), (5,5), 3)
    grayed = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
    # print("Gray: \n",grayed)
    new_frame = frame.copy()
    logging.debug("new_frame: %s", new_frame)
    position_in_second = capture.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
        # --------- A Iteration ----------
    for index, c in enumerate(coordinates_data):
        location_of_lot = coordinates_data[index] 
        coordinates = np.array(location_of_lot["coordinates"])
        rect = bounds[index]
        logging.debug("rect: %s", rect)
        # print("rect: ", rect)
        roi_gray = grayed[rect[1]:(rect[1] + rect[3]), rect[0]:(rect[0] + rect[2])]
        # print("Roi:\n", roi_gray)
        lap = cv2.Laplacian(roi_gray, cv2.CV_64F)
        # print("Laplacian: \n", lap)

        coordinates[:, 0] = coordinates[:, 0] - rect[0]
        coordinates[:, 1] = coordinates[:, 1] - rect[1]

        # print("Coordinates: \n", coordinates)
        # print("result0: \n", lap * mask[0])
        # print("result1: \n", np.abs(lap * mask[0]))
        # print("result2: \n", np.mean(np.abs(lap * mask[0])))
        status = np.mean(np.abs(lap * mask[index])) < LAPLACIAN

        # print("Status: \n", status)
        if times[index] is not None and status == statuses[index]:
            times[index] = None
            print(statuses)
            # continue
        if  times[index] is not None  and  status != statuses[index]:
            if  position_in_second - times[index] >= DETECT_DELAY:
                statuses[index] = status
                print(statuses)
                times[index] = None
            # continue
        if times[index] is None and status != statuses[index]:
            times[index] = position_in_second
    for index, p in enumerate(coordinates_data):
        location_of_lot = coordinates_data[index] 
        coordinates = np.array(location_of_lot["coordinates"])
        color = COLOR_GREEN if statuses[index] else COLOR_BLUE
        draw_contours(new_frame, coordinates, str(p["id"] + 1), COLOR_WHITE, color)
    cv2.imshow("test", new_frame)
    k = cv2.waitKey(1)
    if k == ord("q"):
        break
capture.release()
cv2.destroyAllWindows()
# ----- End of a iteration-----