import cv2

cap = cv2.VideoCapture("http://i23-ws002.diamond.ac.uk:8080/OAV.mjpg.mjpg")

while True:
    ret, image = cap.read()
    cv2.imshow("Test", image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cv2.destroyAllWindows()