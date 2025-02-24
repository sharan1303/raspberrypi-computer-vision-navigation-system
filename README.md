# Low-cost Computer Vision System for Autonomous Outdoor Robots

This project formulates my final year dissertation project for my BSc in Computer Science. It is a computer vision-based navigation system using ArUco fiducial markers for guiding autonomous robots through gate formations.

## Overview

This project implements a low-cost vision system using ArUco markers and a Raspberry Pi to provide directional guidance for autonomous outdoor robots. The system:

- Uses custom ArUco markers arranged in gates to create a navigation path
- Detects markers using computer vision (OpenCV)
- Calculates target points between marker pairs
- Provides directional output via GPIO pins or UART serial communication
- Runs on resource-constrained hardware (Raspberry Pi Zero)

## Components

The system uses:

### ArUco Markers

- Custom 4x4 bit ArUco markers (4 types):
  - Left marker (ID 0)
  - Right marker (ID 1)
  - Start marker (ID 2)
  - Stop marker (ID 3)

### Hardware

- Raspberry Pi Zero with camera
- OpenCV for computer vision
- Serial UART communication

## Installation

Install OpenCV and dependencies

```bash
pip install opencv-python
pip install numpy
pip install pyserial
```

## Usage

### Running on Desktop/Development Machine

#### Test with image input

```bash
python src/detectarucoimage.py
```

#### Test with video input from camera

```bash
python src/detectarucovideo.py [camera_index]
```

### Running on Raspberry Pi

#### Main navigation program

```bash
python src/raspiaruco.py [camera_index]
```

#### Test serial communication

```bash
 python src/testserial.py  # Send test message
 python src/readserial.py  # Read serial output
```

## Gate Formation

- Place left and right ArUco markers in parallel to form gates
- Start marker initiates navigation
- Stop marker ends navigation
- System calculates target point between valid marker pairs
- Direction is encoded as ASCII characters (A-Z) based on target position

## How It Works

1. Camera captures video feed
2. OpenCV detects ArUco markers in each frame
3. System identifies valid gate formations:
   - Left marker must be on left side
   - Right marker must be on right side
   - Markers should be roughly parallel and similar size
4. Target point calculated between valid marker pairs
5. Target x-coordinate scaled to A-Z ASCII character
6. Direction sent via UART/GPIO to robot controller

## Project Structure

```
 ├── src/
 │   ├── detectarucoimage.py   # Image detection test
 │   ├── detectarucovideo.py   # Video detection test  
 │   ├── raspiaruco.py         # Main Raspberry Pi program
 │   ├── readserial.py         # Serial read test
 │   └── testserial.py         # Serial write test
 ├── Images/                   # Documentation images
 └── README.md
```

## Author

Sharan Govinden Umavassee

## Acknowledgments

- Project Supervisor: Dr. Klaus-Peter Zauner
- Second Examiner: Prof. Christopher Freeman
- University of Southampton, School of Electronics and Computer Science

## License

This project is part of MEng Computer Science with Industrial Studies at University of Southampton.
