import os

os.chdir('/home/pi/light/')
os.system('git checkout master')
os.system('git fetch --all')
os.system('git reset --hard origin/master')
os.system('python3 /home/pi/light/light.py')
