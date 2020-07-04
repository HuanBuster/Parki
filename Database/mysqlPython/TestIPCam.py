import cv2

stream = cv2.VideoCapture('http://20087303:YR01D3F11V4N@192.168.0.117:80')  
while True:

    ret, frame = stream.read()
    cv2.imshow('IP Camera stream',frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()