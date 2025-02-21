# Pill Reminder System with MicroPython

## Overview
This project is a **custom pill reminder system** built using an **ESP8266** or **ESP32** microcontroller. The system flashes an LED at scheduled times to remind the user to take their medication. The LED stops flashing when the button is pressed, ensuring acknowledgment of the reminder.

This system is particularly useful for individuals with dementia or memory-related challenges, as it provides a **non-intrusive** reminder method without relying on auditory alarms that may cause confusion or distress.

## Features
- **LED-Based Reminder**: Flashes an LED at set times to indicate medication time.
- **Button Acknowledgment**: Stops flashing only when the button is pressed.
- **Event Logging**: Logs the time the button is pressed to track medication adherence.
- **Wi-Fi Synchronization**: Connects to an NTP (Network Time Protocol) server to maintain accurate timing.
- **Power Efficiency**: Uses intelligent polling intervals to conserve power.

## Components Needed
- ESP8266 or ESP32 microcontroller
- LED (with a resistor, e.g., 100 ohms)
- Push button
- Breadboard and jumper wires
- USB power cable

## Setup Instructions

### 1. Install MicroPython on Your ESP8266/ESP32
1. Download the latest MicroPython firmware from [MicroPython.org](https://micropython.org/download/).
2. Flash the firmware using **esptool.py**:
   ```sh
   esptool.py --port /dev/ttyUSB0 erase_flash
   esptool.py --port /dev/ttyUSB0 --baud 460800 write_flash --flash_size=detect 0 firmware.bin
   ```

### 2. Connect to Your ESP Board
Use a serial tool like `mpremote` or `ampy`:
```sh
mpremote connect /dev/ttyUSB0
```

### 3. Upload the Script
Upload `main.py` and `boot.py` to the ESP8266/ESP32 using:
```sh
mpremote cp main.py :main.py
mpremote cp boot.py :boot.py
```

### 4. Configure Wi-Fi
Create a `wifi_settings.json` file in the root directory of your ESP8266/ESP32 and add your Wi-Fi credentials:
```json
{
    "wifi_name": "Your_SSID",
    "password": "Your_PASSWORD"
}
```

### 5. Run the Script
The script will automatically:
- Connect to Wi-Fi
- Synchronize the time using an NTP server
- Monitor pill-taking times and flash an LED when necessary
- Log events when the button is pressed

## Wiring Setup
| Component | ESP8266 Pin |
|-----------|------------|
| **LED**   | GPIO 5     |
| **Button**| GPIO 4     |

## Customization
You can modify the pill reminder times by editing the `pill_times` list in `main.py`:
```python
pill_times = [
    (8, 30),  # Morning pill at 08:30 AM
    (13, 15), # Afternoon pill at 01:15 PM
    (19, 45)  # Evening pill at 07:45 PM
]
```

## Example Log Output
An event log is saved in `report.txt`, which includes the timestamp and duration the LED flashed before acknowledgment:
```
IP: 192.168.1.100
Date: 2025/02/21
Pill time: 19:45
LED flashed for 12 seconds.
```

## Full Script
For the complete implementation, refer to [`main.py`](main.py) in this repository.

## License
This project is open-source under the MIT License. Feel free to use and modify it!

## Author
Created by **Jas** (adapted from personal experience helping a family member with dementia).

