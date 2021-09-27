# rpi-sacn-neopixel
Small little python program to try and output WS2811/2b on multiple pins of the RPI (tested on RPI4 rev 1.1)
## Installation
Install the modules needed (needs Python 3.7+)
```
sudo pip3 install rpi_ws281x adafruit-circuitpython-neopixel sacn
sudo python3 -m pip install --force-reinstall adafruit-blinka
```
Clone to directory
`git clone https://github.com/ryanriccio1/rpi-sacn-neopixel.git`

## Config
The config allows setup without having to dive into the code. The first section is dedicated to the "global" setup.

**pixel_pattern:** This could either be `neopixel.GRB` or `neopixel.RGB`. Pretty self self explanatory

**strand_amount:** This is the number of strands to use from the config. Will use the first ones.

**pack_universes:** This is kind of difficult to explain, however, when it == no, it will add each strand to a new universe. When it == yes, 
it will try to put mutliple "strands" on any universe so there is no break in the patch.

Each section after that is for each specific strand
```
strand#.pixels = 5
strand#.universe_start = 1
strand#.pin = board.D12
```
Make sure the change the '#' to the strand number and please make sure to increment them properly. The first strand needs to have a `universe_start` of 1, and each one after that can just be set to `auto`.
The pins can either be `board.D12` `board.D18` `board.D21`. D10 should work too but I haven't gotten it to work on my board.

## Running 
Run it as root

`sudo python3 light.py`
