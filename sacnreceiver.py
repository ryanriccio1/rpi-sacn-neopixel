class SacnUniverse(object):
    def __init__(self, universe, sacn_receiver, pixel_strands):
        """
        Software universe constructor

        :param universe: The software universe number
        :type universe: int
        :param sacn_receiver: The main receiver thread
        :type sacn_receiver: sacn.sACNreceiver
        :param pixel_strands: The strands in this universe
        :type pixel_strands: list

        :return: None
        """
        self._universe = universe
        self._sacn_receiver = sacn_receiver

        # define callback
        @self._sacn_receiver.listen_on('universe', universe=self._universe)
        def callback(packet):
            # loop through each strand in universe and write given information
            for current_strand in iter(pixel_strands):
                current_strand[0].write(packet.dmxData, self._universe, current_strand[1][0], current_strand[1][1])

        # join multicast (do not need to specify IP on sending node) and tell the console
        self._sacn_receiver.join_multicast(self._universe)
        print(f"Universe {self._universe} started...")
