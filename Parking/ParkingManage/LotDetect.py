from mysql.connector import MySQLConnection, Error
from python_mysql_dbconfig import read_db_config
import yaml
import cv2
import numpy as np 

output_path = "/media/huanbuster/Vision/Python/Parki/Parking/Parking-Lot-Detection-Using-OpenCV/data/coordinates_2.yml"
image_path = "/media/huanbuster/Vision/Python/Parki/Parking/Parking-Lot-Detection-Using-OpenCV/images/prototype1.png"
video_path = "/media/huanbuster/Vision/Python/Parki/Parking/Parking-Lot-Detection-Using-OpenCV/prototype2.mp4"

COLOR_BLACK = (0, 0, 0)
COLOR_BLUE = (0, 0, 255)
COLOR_GREEN = (0, 255, 0)
COLOR_RED = (255, 0, 0)
COLOR_WHITE = (255, 255, 255)

LAPLACIAN = 2
DETECT_DELAY = 1
start_frame = 1

contours = []
bounds = []
mask = []

def update_status(slot_number, status):
    # prepare query and data
    query = """ UPDATE parking_lot
                SET status = %s
                WHERE slot_number = %s """
    data = (status, slot_number)

    try:
        # read database configuration
        db_config = read_db_config()
        conn = MySQLConnection(**db_config)
        # update book title
        cursor = conn.cursor()
        cursor.execute(query, data)
        # accept the changes
        conn.commit()

    except Error as error:
        print(error)

    finally:
        cursor.close()
        conn.close()

#  Draw a contour and put a Text in the middle of the image 
def draw_contours(image,
                  coordinates,
                  label,
                  font_color,
                  border_color=COLOR_RED,
                  line_thickness=1,
                  font=cv2.FONT_HERSHEY_SIMPLEX,
                  font_scale=0.5):
    cv2.drawContours(image,
                         [coordinates],
                         contourIdx=-1,
                         color=border_color,
                         thickness=2,
                         lineType=cv2.LINE_8)
    moments = cv2.moments(coordinates)

    center = (int(moments["m10"] / moments["m00"]) - 3,
              int(moments["m01"] / moments["m00"]) + 3)

    cv2.putText(image,
                    label,
                    center,
                    font,
                    font_scale,
                    font_color,
                    line_thickness,
                    cv2.LINE_AA)

# Set up video stream
capture = cv2.VideoCapture(video_path)
capture.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

# Load the saved coordinates from yaml file and assign to -> AllLinesInFile
data = open(output_path,"r")
AllLinesInFile = yaml.load(data)

# Process the coordinates 
for index, slot in enumerate(AllLinesInFile):
    # Assign a line AllLinesInFile -> one_line to get a coordinate in arrayed form
    one_line = AllLinesInFile[index]
    # Put one_line one by one into array. Each coordinate is an array
    coordinate = np.array(one_line["coordinates"])
    # print("coordinate {}: \n".format(index), coordinates)
    # Get a rectangle from each coordinate. Each rectangle is a tuple 
    rect = cv2.boundingRect(coordinate)
    # print("rectangle {}: ".format(index), rect)

    # Put all the coordinate into contour list and all rect into bound list
    # contours is list of coordinate arrays 
    # bounds is a list of rectangle tuples
    contours.append(coordinate)
    bounds.append(rect)
    
    # Generate masks from each coordinate 
    # Generate coordinate of a mask from a coordinate and a corresponding rect
    mask_coordinate = coordinate.copy()
    mask_coordinate[:,0] = coordinate[:,0] - rect[0]
    mask_coordinate[:,1] = coordinate[:,1] - rect[1]
    one_mask = cv2.drawContours(np.zeros((rect[3], rect[2]), dtype=np.uint16), 
                                [mask_coordinate], contourIdx=-1,
                                color=255, thickness=-1, lineType=cv2.LINE_8)
    # Convert each value of one mask to boolean value true/false
    one_mask = one_mask == 255
    # Put all mask into list of mask
    mask.append(one_mask)
# print("Contours: \n", contours[2])
# print("Bounds: ", bounds[2])
# Set initially all the statuses into False
# set initially all time into None
statuses = [False]*len(AllLinesInFile)
times = [None]*len(AllLinesInFile)
#  Process a frame of video 
while capture.isOpened():
    ret, frame = capture.read()
    frame = cv2.rotate(frame,cv2.ROTATE_90_CLOCKWISE)
    if frame is None:
        break
    if not ret:
        raise CaptureReadError("Error reading video capture on frame %s" % str(frame))
    # img = cv2.imread(image_path)
    blur = cv2.GaussianBlur(frame.copy(), (5,5), 3)
    gray = cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY)
    # display = frame.copy()
    # Get the position of the frame in the video in unit second
    cur_time = capture.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
    # for each frame of a video loop through all the coordinates 
    for index, value in enumerate(contours):
        one_coordinate = contours[index]
        one_rect = bounds[index]
        # for each coordinate convert the image to gray and cut the roi
        roi = gray[one_rect[1]: (one_rect[1]+one_rect[3]),
                one_rect[0]: (one_rect[0]+one_rect[2])]
        # for each coordinate calculate Laplacian to decide the current status
        lap = cv2.Laplacian(roi, cv2.CV_64F)
        mean = np.mean(np.abs(lap * mask[index]))
        cur_status = mean < LAPLACIAN
        # 
        # coordinate[:,0] = coordinate[:,0] - rect[0]
        # coordinate[:,1] = coordinate[:,1] - rect[1]
        # Check the condition 
        # Compare one by one between the current status of on coordinate and itself at a time
        if times[index] is not None and cur_status == statuses[index]:
            times[index] = None
            # all slot in parking is remain the same 
            print("The same status: ", statuses)
        if times[index] is not None and cur_status != statuses[index]:
            # The current status of a coordinate has changed and the time of change has
            # been recorded 
            if cur_time - times[index] >= DETECT_DELAY:
                # Checking to eliminate false detection due to movement 
                # Update the current status to the list statuses
                statuses[index] = cur_status
                # Convert to MySQL type
                if statuses[index]:
                    statuses[index]=1
                else:
                    statuses[index]=0
                update_status(index+1, statuses[index])
                print("The status has changed: ", statuses)
                times[index] = None 
        if times[index] is None and cur_status != statuses[index]:
            # If the status's one coordinate has changed and the time of change has not
            # been recorded
            # Then capture the time 
            times[index] = cur_time
            print("Capture the time of change: ", times[index])
    # After checking through all the coordinate 
    # Display the result of all the coordinates to the windows
    for index, value in enumerate(contours):
        color = COLOR_GREEN if statuses[index] else COLOR_BLUE
        draw_contours(frame, value, str(index + 1), COLOR_WHITE, color)
    cv2.imshow("test", frame)
    k = cv2.waitKey(1)
    if k == ord("q"):
        break
capture.release()
cv2.destroyAllWindows()
