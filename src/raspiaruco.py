# import the necessary packages
import sys
import numpy as np
import cv2
import serial
import time

# Initialize UART serial communication
ser = serial.Serial('/dev/serial0', 9600)
time.sleep(0.1)
ser.reset_output_buffer()

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

# create custom dictionary of aruco markers
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
    signal = "%"
    ser.write(signal.encode())
    ser.flush()

    # Release the camera and serial port connection
    # and Exit the program
    cam.release()
    ser.close()
    sys.exit()
else:
    print("[INFO] Camera is ready")
    signal = "<"
    ser.write(signal.encode())
    ser.flush()
    time.sleep(0.5)

# Record of marker IDs detected in stream
tagID = []

# loop over the frames from the video stream
while True:
    # Capture frame-by-frame video stream
    _, frame = cam.read()

    # grab the frame from the threaded video stream and resize it
    # to have a maximum width of 1000 pixels
    # and maximum height of 750 pixels
    frame = cv2.resize(frame, (1000, 700))

    # Get the height and width of the image
    _, width, _ = frame.shape

    # List of tags in view
    tags  = []

    # detect ArUco markers in the input frame
    (corners, ids, rejected) = cv2.aruco.detectMarkers(frame, arucoDict, parameters=arucoParams)
    
    # verify *at least* one ArUco marker was detected
    if len(corners) > 0:
        # Add detected ArUco markers to tags list
        for x in range(len(ids)):
            # add detected ArUco markers to tags list
            g = gate(corners[x][0], ids[x])
            tags.append(g)
        
        # Sort tags list by size of ArUco markers in ascending order
        tags.sort(key = lambda gate: gate.size, reverse = True)
        
        gatedetect = False
        
        # Scale factor to find convert coordinates to an ascii value
        # 25 sections (26 characters, 0-25).
        scale_factor = 25 / width # 25 / 1000 = 0.02
        
        # Stop Marker
        if (tags[0].ID[0] == 3):
            signal = "!"
            ser.write(signal.encode())
            ser.flush()
            print("[INFO] STOP Marker detected")
            time.sleep(0.3)
            continue

        # Start Marker
        if (tags[0].ID[0] == 2):
            signal = "&"
            ser.write(signal.encode())
            ser.flush()
            print("[INFO] START Marker detected")
            time.sleep(0.3)
	
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

            print("[INFO] Detecting Gates") 

            # Close the program using start and stop markers simultaneously
            if (tags[0].ID[0] == 2 and tags[1].ID[0] == 3) or (tags[0].ID[0] == 3 and tags[1].ID[0] == 2):
                signal = "@"
                ser.write(signal.encode())
                ser.flush()
                print("[INFO] Stopping video stream")
                break

            # Default value for ASCII character if no gate is detected
            asc = '?'

            # Compare the IDs of the markers to verify gate alignment
            if (tags[0].ID[0] == 0 and tags[1].ID[0] == 1):
                # Compare the positions of the markers
                if (marker0Center[0] < marker1Center[0]):
                    # Scale the target point x-coordinate to an ASCII character value
                    asc = chr(int((target[0] * scale_factor) + 64))
                    gatedetect = True

            elif (tags[0].ID[0] == 1 and tags[1].ID[0] == 0):
                # Compare the positions of the markers
                if (marker0Center[0] > marker1Center[0]):
                    # Scale the target point to an ASCII character value
                    asc = chr(int((target[0] * scale_factor) + 64))
                    gatedetect = True

            # Send the ASCII character over UART
            ser.write(asc.encode())
            ser.flush()
            time.sleep(0.1)
            print(asc)

        if len(tags) >= 3:
            # Extracting the corners of the markers
            marker0Corners = tags[0].corners
            marker1Corners = tags[1].corners
            marker2Corners = tags[2].corners

            # Calculate the centre of the markers
            marker0Center = np.mean(marker0Corners, axis=0).astype(int)
            marker1Center = np.mean(marker1Corners, axis=0).astype(int)
            marker2Center = np.mean(marker2Corners, axis=0).astype(int)

            # Default value for ASCII character and if no gate is detected
            asc = '?'

            # Compare the IDs of the markers to verify gate alignment
            if (tags[0].ID[0] == 0 and tags[1].ID[0] == 1):
                # Calculate the midpoint between the two markers to act as target
                target = calculate_midpoint(marker0Corners, marker1Corners)

                # Compare the positions of the markers
                if (marker0Center[0] < marker1Center[0]):
                    # Scale the target point x-coordinate to an ASCII character value
                    asc = chr(int((target[0] * scale_factor) + 64))
                    gatedetect = True

            elif (tags[0].ID[0] == 1 and tags[1].ID[0] == 0):
                # Calculate the midpoint between the two markers to act as target
                target = calculate_midpoint(marker0Corners, marker1Corners)

                # Compare the positions of the markers
                if (marker0Center[0] > marker1Center[0]):
                    # Scale the target point to an ASCII character value
                    asc = chr(int((target[0] * scale_factor) + 64))
                    gatedetect = True

            elif (tags[1].ID[0] == 1 and tags[2].ID[0] == 0):
                # Calculate target point
                target = calculate_midpoint(marker1Corners, marker2Corners)
                
                # Compare the positions of the markers
                if (marker1Center[0] > marker2Center[0]):
                    # Scale the target point to an ASCII character value
                    asc = chr(int((target[0] * scale_factor) + 64))
                    gatedetect = True

            elif (tags[1].ID[0] == 0 and tags[2].ID[0] == 1):
                # Calculate target point
                target = calculate_midpoint(marker1Corners, marker2Corners)

                # Compare the positions of the markers
                if (marker1Center[0] < marker2Center[0]):
                    # Scale the target point x-coordinate to an ASCII character value
                    asc = chr(int((target[0] * scale_factor) + 64))
                    gatedetect = True

            # Send the ASCII character over UART
            ser.write(asc.encode())
            ser.flush()
            time.sleep(0.1)
            print(asc)

        tagID = [tag.ID[0] for tag in tags]
        tagsize = [tag.size for tag in tags]
    else:
        # No marker detected
        signal = "-"
        ser.write(signal.encode())
        ser.flush()
        time.sleep(0.3)

if not(tagID == []):
    print("[INFO] Detected Tags ID: " + str(tagID))
    print("[INFO] Tag Sizes (pixels): " + str(tagsize))

    if gatedetect:
        print("[INFO] Gate detected.")
        print("[OUTPUT] Target Gate Coordinates: " + str(target))
    else:
        print("[INFO] No Gate detected.")
    print("[OUTPUT] ASCII value of target:", asc)

print("[INFO] Cleaning up and Exiting Program")

# close the serial port
ser.close()

# cleanup
cam.release()
cv2.destroyAllWindows()
