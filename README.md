# Windguru and Holfuy display

A PyGame-based wind data display.

Display local Windguru or Holfuy data on Raspberry Pi.

|![screenshot1](screenshots/screenshot1.png)|![screenshot2](screenshots/screenshot2.png)|![screenshot3](screenshots/screenshot3.png)|
| ----------------------------------------- | ----------------------------------------- | ----------------------------------------- |
|![screenshot4](screenshots/screenshot4.png)|![screenshot5](screenshots/screenshot5.png)|                                           |    
  
Installation instructions

# Install Python 3
   ```sh
   sudo apt-get install python3
   ```
   ```sh
   sudo apt-get install python3-pip
   ```
   ```sh
   sudo apt-get install libsdl1.2-dev libsdl-ttf2.0-dev libsdl-image1.2-dev libsdl-mixer1.2-dev libjpeg-dev libportmidi-dev libtimedate-perl
   ```
# Install Pygame
   ```sh
   pip3 install pygame
   ```
# Install requests
   ```sh
   pip3 install requests
   ```
# Install windguru-holfuy 
   ```sh
   git clone https://github.com/ciprian288/Windguru-and-Holfuy-display.git 
   ```
  # Run windguru-holfuy
- edit config.py with data for wind service and location and:
   
   ```sh
   cd Windguru-and-Holfuy-display
   ```
   ```sh
   python3 wind.py
   ```
#    To EXIT wind.py -- press Q    ####

© 2021 GitHub, Inc.
