# import the necessary packages
import imutils
import numpy as np
import cv2

# Create custom dictionary of aruco markers
arucoDict = cv2.aruco.Dictionary_create(4,4)
arucoParams = cv2.aruco.DetectorParameters_create()

# Class to represent the aruco markers as form of gates
class gate:
    def __init__(self, corners, ID):
        self.corners = corners
        self.ID = ID
        self.size = cv2.norm(corners[0] - corners[2]) # diagonal length of the marker

# Function to calculate the midpoint between two markers
def calculate_midpoint(marker1, marker2):
    x1, y1 = marker1[1] # top-right corner of marker 1
    x2, y2 = marker2[3] # bottom-left corner of marker 2

    # calculate centre point
    x_mid = (x1 + x2) / 2
    y_mid = (y1 + y2) / 2

    return (x_mid, y_mid)

# Function to draw a circle at the midpoint between two markers
def drawtarget(image, marker1, marker2):
    x_mid, y_mid = calculate_midpoint(marker1, marker2)
    cv2.circle(image, (int(x_mid), int(y_mid)), 5, (0, 0, 255), -1)

# Method to draw a line between two points
def draw_line(frame, point1, point2):
    cv2.line(frame, point1, point2, (255, 255, 255), 2)


# load the input image from disk and resize it
# to have a maximum width of 750 pixels
print("[INFO] loading image...")
frame = cv2.imread("assets\IMG_0412(1).JPG")
frame = imutils.resize(frame, width=750)

# Get the height and width of the image
height, width, _ = frame.shape

# Draw circle at centre of the frame
centre = (width // 2, height // 2)
cv2.circle(frame, centre, 1, (255, 255, 255), -1)

# List of tags in view
tags  = []
tagID = []

# detect ArUco markers in the input frame
(corners, ids, rejected) = cv2.aruco.detectMarkers(frame, arucoDict, parameters=arucoParams)

# verify *at least* one ArUco marker was detected
if len(corners) > 0:
    # Zip corners and ids inside tuple
    markers = zip(corners, ids)
    
    for x in range(len(ids)):
        # Draw bounding box for detected aruco markers
        cv2.aruco.drawDetectedMarkers(frame, corners)

        # add detected ArUco markers to tags list
        g = gate(corners[x][0], ids[x])
        tags.append(g)
    
    # Sort tags list by size of ArUco markers in ascending order
    tags.sort(key = lambda gate: gate.size, reverse = True)

    # loop over the detected ArUCo corners
    for (markerCorner, markerID) in markers:
        # extract the marker corners (which are always returned in 
        # top-left, top-right, bottom-right, and bottom-left order)
        # corners[0][0], corners[0][1], corners[0][2], corners[0][3]
        corners = markerCorner.reshape((4, 2))
        (topLeft, topRight, bottomRight, bottomLeft) = corners

        # convert each of the (x, y)-coordinate pairs to integers
        topRight = (int(topRight[0]), int(topRight[1]))
        bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
        bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
        topLeft = (int(topLeft[0]), int(topLeft[1]))

        # compute and draw the center (x, y)-coordinates of the ArUco marker
        cX = int((topLeft[0] + bottomRight[0]) / 2.0)
        cY = int((topLeft[1] + bottomRight[1]) / 2.0)
        cv2.circle(frame, (cX, cY), 4, (255, 0, 0), -1)
        
        # draw the ArUco marker ID on the frame
        cv2.putText(frame, str(markerID),
            (topLeft[0], topLeft[1] - 15),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5, (0, 255, 0), 2)
        
    gatedetect = False
    gate = 0

    # Check if the gates are aligned correctly
    if (len(tags) >= 2):
        # Extracting the corners of the markers
        marker0Corners = tags[0].corners
        marker1Corners = tags[1].corners

        # Calculate the centre of the markers
        marker0Center = np.mean(marker0Corners, axis=0).astype(int)
        marker1Center = np.mean(marker1Corners, axis=0).astype(int)

        # Calculate the midpoint between the two markers to act as target
        target = calculate_midpoint(marker0Corners, marker1Corners)

        # Scale factor to find convert coordinates to an ascii value
        # 25 sections (26 characters, 0-25).
        scale_factor = 25 / width
        
        # TODO - Add tags[2] and tags[3] to account for third and fourth biggest marker
        # Compare the IDs of the markers
        if (tags[0].ID[0] == 0 and tags[1].ID[0] == 1):
            # Compare the positions of the markers
            if (marker0Center[0] < marker1Center[0]):
                # Draw a target point between the two markers
                drawtarget(frame, marker0Corners, marker1Corners)
                
                # Scale the target point to an ASCII character value
                asc = chr(int((target[0] * scale_factor) + 64))
                
                gatedetect = True
            else:
                asc = "-"
                gatedetect = False

        elif (tags[0].ID[0] == 1 and tags[1].ID[0] == 0):
            # Compare the positions of the markers
            if (marker0Center[0] > marker1Center[0]):
                # Draw a target point between the two markers
                drawtarget(frame, marker0Corners, marker1Corners)

                # Scale the target point to an ASCII character value
                asc = chr(int((target[0] * scale_factor) + 64))

                gatedetect = True
            else:
                asc = "-"
                gatedetect = False

    tagID = [tag.ID[0] for tag in tags]
    tagsize = [tag.size for tag in tags]
    tagcorner = [tag.corners[0][0] for tag in tags]

# show the output frame        
cv2.imshow("ArUco Gate Detection System", frame)
key = cv2.waitKey(0) & 0xFF

# if the `s` key was pressed, take a screenshot
if key == ord("s"):
    cv2.imwrite("screenshot.jpg", frame)
    print("[INFO] Screenshot saved.")

if not(tagID == []):
    print("[INFO] Detected Tags ID: " + str(tagID))
    print("[INFO] Tag Sizes (pixels): " + str(tagsize))
    print("[INFO] Tag Top Left Corner Coordinates: " + str(tagcorner))
    print()
    if gatedetect:
        print("[INFO] Gate detected.")
        print("[OUTPUT] Target Gate Coordinates: " + str(target))
    else:
        print("[INFO] No Gate detected.")
    print("[OUTPUT] ASCII value of target:", asc)
    
# cleanup
cv2.destroyAllWindows()