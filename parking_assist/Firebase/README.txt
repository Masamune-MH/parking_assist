# Firebase Integration

This folder contains the Firebase integration for the parking assistance system.

## My Part

This part uploads the distance data obtained by the ESP32 to Firebase Realtime Database and reads the latest distance data from Firebase using Python.

## Data Flow

ESP32 Distance Data  
(Left / Center / Right)  
↓  
Firebase Realtime Database  
↓  
Python Data Reader

## Files

### Parking_Sensor_Firebase.ino

This program is based on the existing ultrasonic sensor code.

It:

- Obtains the Left, Center, and Right distance values from the ESP32.
- Connects the ESP32 to Firebase Realtime Database.
- Uploads the three distance values to Firebase every second.
- A value of `-1` means that the corresponding ultrasonic sensor did not receive a valid echo.

The data is stored in Firebase as:

Parking
└── Current
    ├── Left
    ├── Center
    └── Right


### read_firebase.py

This program:

- Connects to Firebase Realtime Database.
- Reads the latest Left, Center, and Right distance values.
- Returns the data in the following Python format:

{
    "left": 35,
    "center": 52,
    "right": 80
}

The returned data can be passed to the next module for further processing.

## Configuration

Before testing, configure the Wi-Fi and Firebase information in the code.
