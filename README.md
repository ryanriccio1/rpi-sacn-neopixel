# rpi-sacn-neopixel
Small little python program to try and output WS2811/2b on multiple pins of the RPI (tested on RPI4 rev 1.1)
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
