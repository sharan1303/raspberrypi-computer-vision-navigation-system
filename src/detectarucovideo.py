# import the necessary packages
import sys
import numpy as np
import cv2
import time

# Create custom dictionary of aruco markers
arucoDict = cv2.aruco.Dictionary_create(4,4)
arucoParams = cv2.aruco.DetectorParameters_create()

if len(sys.argv) > 1:
    camera_index = int(sys.argv[1])
else:
    camera_index = 0  # Default camera index

# Camera Setup
print("[INFO] Starting video stream...")
cam = cv2.VideoCapture(camera_index)
if not cam.isOpened():
    print("[INFO] Cannot open camera")
    sys.exit()
else:
    print("[INFO] Camera ready")

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

    # calculate midpoint
    x_mid = (x1 + x2) / 2
    y_mid = (y1 + y2) / 2

    return (x_mid, y_mid)

# Function to draw a circle at the midpoint between two markers
def drawtarget(image, target, asc):
    # Initialise midpoint coordinates
    x_mid, y_mid = target

    # draw a circle at the midpoint when gate is detected
    if not asc == "?":
        cv2.circle(image, (int(x_mid), int(y_mid)), 5, (0, 0, 255), -1)

    # draw the ASCII character on the frame
    cv2.putText(frame, asc,
        (int(x_mid), int(y_mid + 30)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5, (0, 255, 0), 2)

# loop over the frames from the video stream
while True:
    # Capture frame-by-frame video stream
    _, frame = cam.read()

    # grab the frame from the threaded video stream and resize it
    # to have a maximum width of 1000 pixels
    # and maximum height of 700 pixels
    frame = cv2.resize(frame, (1000, 700))

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
        
        # Scale factor to find convert coordinates to an ascii value
        # 25 sections (26 characters, 0-25).
        scale_factor = 25 / width # 0.025
        
        # Start marker
        if (tags[0].ID[0] == 2):
            start_signal = "& - Start Signal"
            drawtarget(frame, centre, start_signal)
            print(start_signal)
        
        # Stop marker
        if (tags[0].ID[0] == 3):
            stop_signal = "! - Stop Signal"
            print(stop_signal)
            drawtarget(frame, centre, stop_signal)
            continue
        
        # Check if the gates are aligned correctly
        if (len(tags) == 2):
            # Extracting the corners of the markers
            marker0Corners = tags[0].corners
            marker1Corners = tags[1].corners

            # Calculate the centre of the markers
            marker0Center = np.mean(marker0Corners, axis=0).astype(int)
            marker1Center = np.mean(marker1Corners, axis=0).astype(int)

            # Calculate the midpoint between the two markers to act as target
            target = calculate_midpoint(marker0Corners, marker1Corners)        

            # Default value for ASCII character and if no gate is detected
            asc = "?" 

            # Check if the markers are aligned correctly
            if (tags[0].ID[0] == 0 and tags[1].ID[0] == 1):
                # Compare the positions of the markers
                if (marker0Center[0] < marker1Center[0]):
                    # Gate detected
                    # Scale and convert the target point  
                    # x-coordinate to uppercase character
                    asc = chr(int((target[0] * scale_factor) + 64))
                    gatedetect = True

            elif (tags[0].ID[0] == 1 and tags[1].ID[0] == 0):
                # Compare the positions of the markers
                if (marker0Center[0] > marker1Center[0]):
                    # Gate detected
                    # Scale and convert the target point  
                    # x-coordinate to uppercase character
                    asc = chr(int((target[0] * scale_factor) + 64))
                    gatedetect = True
            
            # Print the ASCII character to the console
            print(asc)

            # Draw a target point between the two markers
            drawtarget(frame, target, asc)

        if len(tags) >= 3:
            # Extracting the corners of the markers
            marker0Corners = tags[0].corners
            marker1Corners = tags[1].corners
            marker2Corners = tags[2].corners

            # Calculate the centre of the markers
            marker0Center = np.mean(marker0Corners, axis=0).astype(int)
            marker1Center = np.mean(marker1Corners, axis=0).astype(int)
            marker2Center = np.mean(marker2Corners, axis=0).astype(int)

            # Default value for ASCII character
            asc = "?"

            # Compare the IDs of the markers
            if (tags[0].ID[0] == 0 and tags[1].ID[0] == 1):
                # Calculate the midpoint between the two markers to act as target
                target = calculate_midpoint(marker0Corners, marker1Corners)

                # Compare the positions of the markers
                if (marker0Center[0] < marker1Center[0]):
                    # Gate detected
                    # Scale and convert the target point  
                    # x-coordinate to uppercase character
                    asc = chr(int((target[0] * scale_factor) + 64))
                    
                    # # Draw a target point between the two markers
                    # drawtarget(frame, target, asc)
                    
                    gatedetect = True

            elif (tags[0].ID[0] == 1 and tags[1].ID[0] == 0):
                # Calculate the midpoint between the two markers to act as target
                target = calculate_midpoint(marker0Corners, marker1Corners)

                # Compare the positions of the markers
                if (marker0Center[0] > marker1Center[0]):
                    # Gate detected
                    # Scale and convert the target point  
                    # x-coordinate to uppercase character
                    asc = chr(int((target[0] * scale_factor) + 64))

                    # # Draw a target point between the two markers
                    # drawtarget(frame, target, asc)

                    gatedetect = True

            elif (tags[1].ID[0] == 1 and tags[2].ID[0] == 0):
                # Calculate target point
                target = calculate_midpoint(marker1Corners, marker2Corners)
                
                # Compare the positions of the markers
                if (marker1Center[0] > marker2Center[0]):
                    # Gate detected
                    # Scale and convert the target point  
                    # x-coordinate to uppercase character
                    asc = chr(int((target[0] * scale_factor) + 64))

                    # # Draw a target point between the two markers
                    # drawtarget(frame, target, asc)

                    gatedetect = True

            elif (tags[1].ID[0] == 0 and tags[2].ID[0] == 1):
                # Calculate target point
                target = calculate_midpoint(marker1Corners, marker2Corners)

                # Compare the positions of the markers
                if (marker1Center[0] < marker2Center[0]):
                    # Gate detected
                    # Scale and convert the target point  
                    # x-coordinate to uppercase character
                    asc = chr(int((target[0] * scale_factor) + 64))
                    
                    # # Draw a target point between the two markers
                    # drawtarget(frame, target, asc)

                    gatedetect = True

            # Print the ASCII character to the console
            print(asc)

            # Draw a target point between the two markers
            drawtarget(frame, target, asc)

        tagID = [tag.ID[0] for tag in tags]
        tagsize = [tag.size for tag in tags]

    # else:
    #     drawtarget(frame, centre, "- no markers detected -")
    
    # show the output frame        
    cv2.imshow("Fiducial Marker Computer Vision-based Navigation System", frame)
    key = cv2.waitKey(1) & 0xFF
    
    # if the `s` key was pressed, take a screenshot
    if key == ord("s"):
        cv2.imwrite("screenshot.jpg", frame)
        print("[INFO] Screenshot saved.")

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        print("[INFO] stopping video stream...")
        break

if not(tagID == []):
    print("[INFO] Detected Tags ID: " + str(tagID))
    print("[INFO] Tag Sizes (pixels): " + str(tagsize))
    if gatedetect:
        print("[INFO] Gate detected.")
        print("[OUTPUT] Target Gate Coordinates: " + str(target))
    else:
        print("[INFO] No Gate detected.")
    print("[OUTPUT] ASCII value of target:", asc)

# cleanup
cam.release()
cv2.destroyAllWindows()