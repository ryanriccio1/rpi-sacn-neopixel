# rpi-sacn-neopixel
Small little python program to output WS2811/2b on multiple pins of the arm64 single board development computer, Raspberry Pi (tested on RPi4 rev 1.1).

**WS2811** is the protocol used to control a strand of individually addressable LEDs. They require data at a constant clock signal and will update the entire stand at once. This is an issue because the Raspberry Pi is a non-realtime OS (possible variable clock signal) which makes scheduling and writing data to the pins an issue. Luckily, the RPi has a standalone SPI (Serial Peripheral Interface) chip that can interface with the kernel with its own separate clock (2MHz). Sychronizing this data is the difficult part. Starting with the RPi 4 there were more than 1 configurable SPI chips that can be swapped in place for use on pins.

Where does the RPi get its data from to write to the lights? In the professional lighting world, a lighting console will send data to lighting fixutres over a protocol called **"DMX"** (WS2811 uses SPI, not DMX). The DMX is made up of "universes", with each universe containing 512 8-bit values of data used to control the lights. A DMX cable normally only carries 1 universe over 3 pins. There is a protocol called **"sACN"** (Streaming Architecture for Control Networks) which allows for 63,999 universes to be multicast to the local network, rather than over a physical cable. A single pixel on a strand of WS2811 LEDs will use of 3 of these 8-bit values (red, green, blue), meaning that only 170 pixels can fit on 1 universe. This requires we combine multiple universes being updated at multiple times to make a pixel chain longer than 170 (keeping in mind the entire pixel strand needs to be updated at once). 

We use the Adafruit Neopixel module to make creating the SPI frames easier, and the sACN module to handle the network traffic. There is also intergration with an open source project called **"OpenLightingArch (OLA)"** which allows easy, over IP configuration changes of the universes and their data sources.
## Installation
Install the modules needed (needs Python 3.7+)
```shell
sudo apt-get install git screen
sudo pip3 install rpi_ws281x adafruit-circuitpython-neopixel sacn
sudo python3 -m pip install --force-reinstall adafruit-blinka
```
Clone to home directory
```shell
mkdir /home/pi/light
cd /home/pi/light/
git init
git remote add origin https://github.com/ryanriccio1/rpi-sacn-neopixel.git
git fetch origin
git checkout master
```
Copy auto-update script and helpful starting script to home directory
```shell
cp /home/pi/light/autoupdater.py /home/pi/light_starter.py
cp /home/pi/light/start_lights /home/pi/start_lights
chmod +x /home/pi/start_lights
```
Add this entry to `/boot/config.txt` using `sudo nano`
```
dtoverlay=disable-bt
```
And comment out any lines related to I2C, SPI, UART, audio, etc...
```
# dtparam=audio=on
# dtparam=i2s=on
# dtparam=spi=on
# enable_uart=1
# dtparam=audio=on
```

## Config
Start by copying the default config file to the directory of the repository (`light.py`).
```shell
cp /home/pi/light/config/config.txt /home/pi/light/config.txt
```
The config allows setup without having to dive into the code. The first section is dedicated to the "global" setup.

**pixel_pattern:** This could either be `neopixel.GRB` or `neopixel.RGB`. Pretty self self explanatory

**strand_amount:** This is the number of strands to use from the config. Will use the first ones.

**pack_universes:** This is kind of difficult to explain, however, when it == no, it will add each strand to a new universe. When it == yes, 
it will try to put mutliple "strands" on any universe so there is no break in the patch.

**use_ola:** This determines whether the Open Lighting Architecture will be used to receive DMX data. If not, normal multicast sACN will be used. To access OLA, the web portal is available on port 9090 for the IP address of the pi. Start the OLA daemon before running light.py if using OLA: `olad -l 3`

**export_patch:** This will export the generated patching of the pixels to `file.csv`

**write_logs:** This will write the console output to a `*.log` file.

**log_level:** This will determine the level of detail in console output and log file.

Each section after that is for each specific strand.
```
strand#.pixels = 5
strand#.pixel_offset = X
strand#.universe_start = 1
strand#.pin = board.D12
```
Make sure the change the '#' to the strand number and please make sure to increment them properly. The first strand needs to have a `universe_start` of 1, and each one after that can just be set to `auto`.
The pins can either be `board.D12` `board.D18` `board.D21`. D10 should work too but I haven't gotten it to work on my board. `pixel_offset` will skip the first "X" pixels on the physical strand.

## Running 
Run it as root, making sure to run OLA if using it:

```shell
olad -l 3 # if using OLA
sudo ./start_lights
```
I was not able to get the auto script to work, so I have included a handy startup script to put in /home/pi.

~~OR~~

~~Run the auto update script at startup:~~

~~Give proper permissions to both of the services and copy them to the service directory.~~
```shell
cd light
sudo chmod 644 olad.service
sudo chmod 644 light.service
sudo cp olad.service /lib/systemd/system/
sudo cp light.service /lib/systemd/system/
sudo systemctl enable systemd-networkd.service systemd-networkd-wait-online.service
sudo systemctl daemon-reload
sudo systemctl enable olad.service
sudo systemctl enable light.service
```
~~On next startup, the applications will start automatically. When using OLA however, even though both of the services start on their own, 
in my testing, I needed to manually restart both systems after a restart for the python library to be able to configure OLA patch.
If this occurs, restart the services with:~~
```shell
sudo systemctl restart olad
sudo systemctl restart light
```

~~When OLAD is not used, the console status can be viewed using~~
```shell
systemctl status light
```
~~Some common errors I have seen at runtime have to do with UTF-8 encoding or no sACN device found. In both cases, for me, I had DMX control software sending data as the server started up. I closed the application completely and restarted. This is not a fixable bug as it is an issue with the way the sACN socket is.~~
