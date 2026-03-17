# ESP8266 Sensor Firmware

This folder contains the Arduino sketch for the ESP8266 microcontroller to monitor bin fill levels using an ultrasonic sensor (HC-SR04).

## Hardware Component

1.  **ESP8266 Board**: NodeMCU, Wemos D1 Mini, or similar.
2.  **Ultrasonic Sensor**: HC-SR04.
3.  **Jumper Wires**.
4.  **Resistors (Optional but recommended)**: 1kΩ and 2kΩ for voltage divider on Echo pin.

## Wiring Connections

| HC-SR04 Pin | ESP8266 Pin | Notes |
| :--- | :--- | :--- |
| **VCC** | **VIN** (5V) or **3V3** | Connect to 5V if available (VIN on NodeMCU/Wemos). Most HC-SR04 require 5V. |
| **GND** | **GND** | Common ground. |
| **Trig** | **D1** (GPIO 5) | Trigger pin. Sends the pulse. |
| **Echo** | **D2** (GPIO 4) | Echo pin. **WARNING**: HC-SR04 outputs 5V logic. ESP8266 is 3.3V logic. Use a voltage divider (see below) or connect directly at your own risk (often works but not recommended). |

### Voltage Divider for Echo Pin (Recommended)
To step down 5V from the sensor to 3.3V for the ESP8266:
1.  Connect **Echo** pin of HC-SR04 to one end of a **1kΩ resistor**.
2.  Connect the other end of the **1kΩ resistor** to **D2** on ESP8266.
3.  Connect a **2kΩ resistor** from **D2** to **GND**.

## Software Setup

1.  Open `esp8266_sensor.ino` in Arduino IDE.
2.  Install **ESP8266 Board Manager**:
    -   Go to `File` > `Preferences`.
    -   Add `http://arduino.esp8266.com/stable/package_esp8266com_index.json` to "Additional Boards Manager URLs".
    -   Go to `Tools` > `Board` > `Boards Manager`, search for "esp8266" and install.
3.  Configure the sketch:
    -   Update `ssid` and `password` with your Wi-Fi credentials.
    -   Update `serverUrl` with your computer's IP address (e.g., `http://192.168.1.X:5000/...`).
    -   Update `binId` and `binDepth` as needed.
4.  Upload to your board.
