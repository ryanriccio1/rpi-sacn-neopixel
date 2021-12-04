import threading
from config import Config


class Universe(object):
    universe_array = []
    last_universe = 0

    def __init__(self, universe, pixel_strands):
        self._universe = universe
        self._pixel_strands = pixel_strands
        self._data = None

        config = Config('config.txt')
        self._use_ola = config.use_ola

    def _write_to_strand(self):
        # loop through each strand in universe and write given information
        for current_strand in iter(self._pixel_strands):
            current_strand[0].write(self._data, self._universe, current_strand[1][0], current_strand[1][1])

    def _set_data(self, data):
        # main callback that starts thread
        if self._use_ola:
            self._data = data   # ola data
        else:
            self._data = data.dmxData   # sacn data
        thread = threading.Thread(target=self._write_to_strand)
        thread.start()
