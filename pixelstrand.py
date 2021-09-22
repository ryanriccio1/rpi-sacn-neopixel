import neopixel
import board


class PixelStrand(object):
    def __init__(self, pin, amount, pattern, start_universe, start_address, pack_universes, pixel_bytes=3):
        self._pin_dict = {
            'board.D10': board.D10,
            'board.D12': board.D12,
            'board.D18': board.D18,
            'board.D21': board.D21
        }
        self._pattern_dict = {
            'neopixel.GRB': neopixel.GRB,
            'neopixel.RGB': neopixel.RGB
        }
        self.pin = self._pin_dict[pin]
        self.amount = amount
        self.pattern = self._pattern_dict[pattern]
        self.start_universe = start_universe
        self.start_address = start_address
        self.pack_universes = pack_universes
        self.pixel_bytes = pixel_bytes
        self.pixels = neopixel.NeoPixel(self.pin, 5, brightness=0.2, auto_write=False, pixel_order=self.pattern)

    def write(self, dmx, universe, address_start, address_end):
        amount_from_universe = int((address_range[1] - address_range[0] + 1) / self.pixel_bytes)
        # print(amount_in_universe)
        # if universe == self.start_universe:
        #     for address in range(self.start_address, amount_in_universe + 1):
        #         dmx_address = address_range[0] + address - 1
        #         self.pixels[address - 1] = dmx[dmx_address:dmx_address + self.pixel_bytes]
        #         print(f"Pixel {address} = {dmx[dmx_address:dmx_address + self.pixel_bytes]}")
        # if universe > self.start_universe:
        #     start_pixel = int((512 - self.start_address) / self.pixel_bytes) + 1
        #     for address in range(start_pixel, amount_in_universe + 1):
        #         self.pixels[address] = dmx[address_range[0] + address - 1]
        # # print(dmx[address_range[0],address_range[1]+1])
        # self.pixels.show()

    def calculate_end_universe(self):
        return int((self.start_address + self.amount * self.pixel_bytes) / 512) + self.start_universe

    def calculate_addresses(self):
        addr = self.start_address
        univ = self.start_universe
        address_table = {
            univ: []
        }
        for pixel in range(self.amount):
            if addr + self.pixel_bytes > 512:
                addr = 1
                univ += 1
                address_table[univ] = []
            print(address_table)
            address_table[univ].append([pixel + 1, addr])
            addr += self.pixel_bytes
        for univ, pixels in address_table.items():
            print(pixels)
            for pixel in enumerate(pixels):
                print(pixel)
                print(f'Univ: {univ}\tPixel: {pixels[pixel]}\tAddr: {pixels[pixel]}')

        # addr = int(self.start_address + ((self.amount * self.pixel_bytes) % 512) - 1)  # - (self.pixel_bytes - 1)
        # if self.amount * self.pixel_bytes > 512:
        #     addr += self.pixel_bytes - 1
        #     while addr > 512:
        #         addr -= 512
        #         addr += self.pixel_bytes - 1
        # return addr

    def get_start_universe(self):
        return self.start_universe

    def get_start_address(self):
        return self.start_address

    def get_next_address(self):
        if self.pack_universes:
            next_univ = int((((self.amount * self.pixel_bytes) + self.pixel_bytes) / 512) + self.start_universe)
            next_addr = ((self.amount * self.pixel_bytes) % 512) + self.start_address
            if self.amount * self.pixel_bytes > 512:
                next_addr += self.pixel_bytes - 1
                while next_addr > 512:
                    next_addr -= 512
                    next_addr += self.pixel_bytes - 1
            return {'universe': next_univ, 'addr': next_addr}
        else:
            return {'universe': self.start_universe + 1 + int(self.amount * self.pixel_bytes / 512), 'addr': 1}
