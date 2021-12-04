import configparser
import os
from customlogs import Log


class Config(object):
    def __init__(self, file):
        self._config = configparser.ConfigParser(allow_no_value=True)
        self._config.read_file(open(file))

        self._pixel_pattern = self._config.get('DMX Out', 'pixel_pattern')  # GRB or RGB
        self._strand_amount = int(self._config.get('DMX Out', 'strand_amount'))  # total physical strands
        self._pack_universes = self._config.getboolean('DMX Out', 'pack_universes')  # multiple strands per universe = true

        self._use_ola = self._config.getboolean('DMX Out', 'use_ola')
        self._export_patch = self._config.getboolean('DMX Out', 'export_patch')
        self._write_logs = self._config.getboolean('DMX Out', 'write_logs')
        self._log_level = int(self._config.get('DMX Out', 'log_level'))
        self._current_strand = 0

        if self._export_patch:
            if os.path.exists("file.csv"):
                os.remove("file.csv")

    def set_current_strand(self, strand):
        if type(strand) == int:
            self._current_strand = strand

    @property
    def pixel_pattern(self):
        return self._pixel_pattern

    @property
    def strand_amount(self):
        return self._strand_amount

    @property
    def pack_universes(self):
        return self._pack_universes

    @property
    def use_ola(self):
        return self._use_ola

    @property
    def export_patch(self):
        return self._export_patch

    @property
    def write_logs(self):
        return self._write_logs

    @property
    def log_level(self):
        return self._log_level

    @property
    def pin(self):
        return self._config.get('DMX Out', f'strand{self._current_strand}.pin')

    @property
    def universe_start(self):
        return self._config.get('DMX Out', f'strand{self._current_strand}.universe_start')

    @property
    def pixel_amount(self):
        return int(self._config.get('DMX Out', f'strand{self._current_strand}.pixels'))

    @property
    def pixel_offset(self):
        return int(self._config.get('DMX Out', f'strand{self._current_strand}.pixel_offset'))
