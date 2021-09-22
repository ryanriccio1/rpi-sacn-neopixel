class SacnUniverse(object):
    def __init__(self, universe, sacn_receiver, pixel_strands):
        self._universe = universe
        self._sacn_receiver = sacn_receiver

        @self._sacn_receiver.listen_on('universe', universe=self._universe)
        def callback(packet):
            for current_strand in enumerate(pixel_strands):
                # does not need to know end addr, will write from start, to end of univ, or end of pixels
                # pixel_strands = [ [strand]    [1, 1]  [1,15]  ], [...]
                #                   [x][0]   [x][1][1]  [x][2]
                pixel_strands[current_strand][0].write(packet.dmxData, self._universe,
                                                       pixel_strands[current_strand][1],
                                                       pixel_strands[current_strand][2])

        self._sacn_receiver.join_multicast(self._universe)
        print(f"Universe {self._universe} started...")
