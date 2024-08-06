# 420 Countdown Timer

## Description
A port of a program originally written for an ESP32 powered LED matrix display. Using the power of Python3 and
multicore PC architecture, I have painstakingly brute forced the Emulated experience of Adafruit_Matrix and FastLED
backed animated LED scrolling display. Entertain friends and family alike as you count down to the golden 'hour'. \
🌿 Happy 420 🌿

Works on Windows, macOS, and probably Linuxes too. I'll test it on one of those someday. 

## Table of Contents
- [Description](#description)
- [Improvements](#improvements)
- [Features](#features)
- [Requirements](#requirements)
- [Usage](#usage)
- [Screenshot](#screenshot)
- [Fun Facts](#fun-facts)
- [License](#license)

## Improvements
 - _Now with Sound!_
 - _Re-programmable Countdown and Messages!_

## Features
 - Resizeable window
 - Closes to system tray
 - Pops up from tray with a 10 min, 2 min, and final 10 sec warnings
 - Sound effects for each warning
 - Customizable countdown time and messages (during runtime)

## Requirements
This program requires the following python modules:
1. PyQT5
2. pytz
3. numpy
4. playsound

## Usage
Install required python modules by typing: ```pip install -r requirements.txt``` into your console of choice. 
Then enter:```python GFXCountdownTimer.py``` or double-click the file if your system is so configured.

## Screenshot
![Project Screenshot](scrnshot.gif)

## Fun Facts
1. Ants take rest for around 8 Minutes in 12-hour period.
2. A cloud weighs around a million tonnes.
3. Starfish don’t have bodies. They are technically classed as heads.
4. Pressing Alt-T will allow you to set the hour and minute of the next countdown end, as well as the countdown messages.
5. This project was inspired by the creation of my [PROGMEM image editor tool](https://github.com/Qcent/LEDMatrixImageEditor), that I used to tune the images used in the original Arduino code.

## License
MIT License
[View License](http://choosealicense.com/licenses/mit/)

MIT License

Copyright (c) 2024 Dave Quinn

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

![Project Screenshot](leafbounce.gif)